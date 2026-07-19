"""Extract bounded text from arXiv PDFs for evidence-grounded analysis."""
from __future__ import annotations

from io import BytesIO

import requests
from pypdf import PdfReader


DEFAULT_MAX_CHARS = 60_000


def extract_pdf_text(pdf_url: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """Download a PDF in memory and return representative extracted text.

    Most papers fit inside the limit. For unusually long documents, retain the
    beginning (definitions and method) and ending (results, limitations, and
    conclusion) instead of silently cutting off the conclusion.
    """
    response = requests.get(
        pdf_url,
        timeout=90,
        headers={"User-Agent": "llm-paper-obsidian/1.0 (research digest)"},
    )
    response.raise_for_status()

    reader = PdfReader(BytesIO(response.content))
    pages = []
    for page_number, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"\n--- Page {page_number} ---\n{text}")

    full_text = "".join(pages).strip()
    if len(full_text) <= max_chars:
        return full_text

    tail_chars = min(15_000, max_chars // 3)
    head_chars = max_chars - tail_chars
    return (
        full_text[:head_chars].rstrip()
        + "\n\n[中間部分因長度限制省略]\n\n"
        + full_text[-tail_chars:].lstrip()
    )
