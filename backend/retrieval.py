"""Lightweight retrieval for the published MkDocs knowledge base."""

from __future__ import annotations

import json
import math
import os
import re
import threading
import time
from dataclasses import dataclass
from urllib.request import Request, urlopen


DEFAULT_KNOWLEDGE_URL = (
    "https://caocharles.github.io/llm-research-obsidian/content.json"
)
KNOWLEDGE_URL = os.getenv("KNOWLEDGE_BASE_URL", DEFAULT_KNOWLEDGE_URL)
CACHE_TTL_SECONDS = int(os.getenv("KNOWLEDGE_CACHE_TTL_SECONDS", "900"))
MAX_CHUNK_CHARS = int(os.getenv("RAG_CHUNK_CHARS", "2400"))
TOP_K = int(os.getenv("RAG_TOP_K", "5"))
MIN_RELATIVE_SCORE = float(os.getenv("RAG_MIN_RELATIVE_SCORE", "0.6"))


@dataclass(frozen=True)
class KnowledgeChunk:
    title: str
    url: str
    content: str
    search_text: str
    terms: frozenset[str]


@dataclass(frozen=True)
class RetrievedSource:
    title: str
    url: str
    content: str
    score: float


def _terms(text: str) -> set[str]:
    """Tokenize English words plus CJK unigrams/bigrams for mixed queries."""
    normalized = text.lower()
    terms = set(re.findall(r"[a-z0-9][a-z0-9_.-]+", normalized))
    for segment in re.findall(r"[\u3400-\u9fff]+", normalized):
        terms.update(segment)
        terms.update(segment[index:index + 2] for index in range(len(segment) - 1))
    return {term for term in terms if term.strip()}


def _split_content(title: str, content: str) -> list[str]:
    """Create heading-aware chunks without introducing another vector service."""
    sections = re.split(r"(?=^#{1,3}\s+)", content, flags=re.MULTILINE)
    chunks: list[str] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        while len(section) > MAX_CHUNK_CHARS:
            boundary = section.rfind("\n", 0, MAX_CHUNK_CHARS)
            if boundary < MAX_CHUNK_CHARS // 2:
                boundary = MAX_CHUNK_CHARS
            chunks.append(section[:boundary].strip())
            section = section[boundary:].strip()
        if section:
            chunks.append(section)
    return chunks or [title]


class KnowledgeRetriever:
    def __init__(self, knowledge_url: str = KNOWLEDGE_URL) -> None:
        self.knowledge_url = knowledge_url
        self._chunks: list[KnowledgeChunk] = []
        self._loaded_at = 0.0
        self._lock = threading.Lock()

    def _fetch_documents(self) -> list[dict[str, str]]:
        request = Request(
            self.knowledge_url,
            headers={"User-Agent": "llm-research-rag/1.0"},
        )
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
        if not isinstance(payload, list):
            raise ValueError("Knowledge base payload must be a list.")
        return payload

    def _load(self) -> list[KnowledgeChunk]:
        now = time.monotonic()
        if self._chunks and now - self._loaded_at < CACHE_TTL_SECONDS:
            return self._chunks

        with self._lock:
            now = time.monotonic()
            if self._chunks and now - self._loaded_at < CACHE_TTL_SECONDS:
                return self._chunks

            try:
                documents = self._fetch_documents()
            except Exception:
                if self._chunks:
                    # A stale index is more useful than losing grounded answers
                    # during a transient GitHub Pages or network outage.
                    self._loaded_at = now
                    return self._chunks
                raise

            chunks: list[KnowledgeChunk] = []
            for document in documents:
                title = str(document.get("title") or "Untitled")
                url = str(document.get("url") or "")
                content = str(document.get("content") or "")
                if not url or not content:
                    continue
                for section in _split_content(title, content):
                    search_text = f"{title}\n{section}".lower()
                    chunks.append(KnowledgeChunk(
                        title=title,
                        url=url,
                        content=section,
                        search_text=search_text,
                        terms=frozenset(_terms(search_text)),
                    ))
            if not chunks:
                raise ValueError("Knowledge base contains no searchable content.")
            self._chunks = chunks
            self._loaded_at = now
            return chunks

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[RetrievedSource]:
        query_terms = _terms(query)
        if not query_terms:
            return []

        normalized_query = re.sub(r"\s+", " ", query.lower()).strip()
        scored: list[tuple[float, KnowledgeChunk]] = []
        for chunk in self._load():
            overlap = query_terms & chunk.terms
            if not overlap:
                continue
            coverage = len(overlap) / len(query_terms)
            specificity = sum(1.0 + math.log1p(len(term)) for term in overlap)
            title_terms = _terms(chunk.title)
            title_overlap = len(overlap & title_terms)
            distinctive_title_matches = sum(
                1 for term in overlap & title_terms
                if len(term) >= 4 and re.search(r"[a-z0-9]", term)
            )
            exact_bonus = 4.0 if normalized_query in chunk.search_text else 0.0
            score = (
                coverage * 8.0
                + specificity
                + title_overlap * 2.5
                + distinctive_title_matches * 22.0
                + exact_bonus
            )
            scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        minimum_score = scored[0][0] * MIN_RELATIVE_SCORE if scored else 0.0
        results: list[RetrievedSource] = []
        seen_urls: set[str] = set()
        for score, chunk in scored:
            if score < minimum_score:
                break
            if chunk.url in seen_urls:
                continue
            seen_urls.add(chunk.url)
            results.append(RetrievedSource(
                title=chunk.title,
                url=chunk.url,
                content=chunk.content,
                score=round(score, 3),
            ))
            if len(results) >= top_k:
                break
        return results

    def stats(self) -> dict[str, object]:
        return {
            "url": self.knowledge_url,
            "cached_chunks": len(self._chunks),
            "cache_loaded": bool(self._chunks),
        }
