#!/usr/bin/env python3
"""
Sync Obsidian vault content into MkDocs docs/.

- Copies Daily/ Weekly/ Topics/ Papers/ into docs/ preserving structure.
- Converts Obsidian PDF embeds to mkdocs-pdf embeds.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from os import path as osp
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
SOURCE_DIRS = ["Daily", "Weekly", "Topics", "Papers"]
HOME_GUIDE_SOURCE = Path("ppt/LLM_Evaluation_and_Safety_Guide.pdf")
HOME_GUIDE_TARGET = Path("assets/guides/LLM_Evaluation_and_Safety_Guide.pdf")

CANONICAL_CATEGORIES = [
    "Benchmark",
    "RAG Evaluation",
    "Safety & Alignment",
    "Agent Evaluation",
    "Hallucination & Faithfulness",
    "Multimodal Evaluation",
]

CATEGORY_ALIASES = {
    "benchmark": "Benchmark",
    "rag": "RAG Evaluation",
    "rag-evaluation": "RAG Evaluation",
    "safety": "Safety & Alignment",
    "safety-alignment": "Safety & Alignment",
    "alignment": "Safety & Alignment",
    "prompt-injection": "Safety & Alignment",
    "jailbreak": "Safety & Alignment",
    "agent": "Agent Evaluation",
    "agent-evaluation": "Agent Evaluation",
    "cs.se": "Agent Evaluation",
    "hallucination": "Hallucination & Faithfulness",
    "faithfulness": "Hallucination & Faithfulness",
    "multimodal": "Multimodal Evaluation",
    "multimodal-safety": "Multimodal Evaluation",
}

PDF_EMBED_RE = re.compile(r"!\[\[([^\]]+?\.pdf)(#[^\]]+)?\]\]")
PDF_LINK_RE = re.compile(r"\[\[([^\]]+?\.pdf)(#[^\]]+)?\]\]")
LOCAL_ARXIV_PDF_RE = re.compile(
    r"\.\./PDFs/(\d{4}\.\d{4,5})(?:v\d+)?\.pdf(?:#[^)\s]+)?"
)


def arxiv_pdf_url(filename: str) -> str | None:
    match = re.fullmatch(r"(\d{4}\.\d{4,5})(?:v\d+)?\.pdf", Path(filename).name)
    if not match:
        return None
    return f"https://arxiv.org/pdf/{match.group(1)}"


def build_pdf_index(root: Path) -> dict[str, Path]:
    pdf_root = root / "PDFs"
    index: dict[str, Path] = {}
    if not pdf_root.exists():
        return index
    for path in pdf_root.rglob("*.pdf"):
        index[path.name] = path
    return index


def replace_pdf_embeds(text: str, doc_path: Path, pdf_index: dict[str, Path]) -> str:
    def _embed_repl(match: re.Match) -> str:
        filename = match.group(1)
        remote_url = arxiv_pdf_url(filename)
        if remote_url:
            return f"[開啟 arXiv PDF]({remote_url})"
        pdf_src = pdf_index.get(filename)
        if not pdf_src:
            return f"(PDF 未找到: {filename})"
        pdf_doc_path = DOCS_DIR / pdf_src.relative_to(ROOT)
        rel_path = osp.relpath(pdf_doc_path, doc_path.parent)
        return (
            f"![]({rel_path}#navpanes=0&toolbar=0)"
            "{ type=application/pdf style=\"min-height:60vh;width:100%;\" }"
        )

    def _link_repl(match: re.Match) -> str:
        filename = match.group(1)
        remote_url = arxiv_pdf_url(filename)
        if remote_url:
            return f"[PDF]({remote_url})"
        pdf_src = pdf_index.get(filename)
        if not pdf_src:
            return f"(PDF 未找到: {filename})"
        pdf_doc_path = DOCS_DIR / pdf_src.relative_to(ROOT)
        rel_path = osp.relpath(pdf_doc_path, doc_path.parent)
        return f"[PDF]({rel_path})"

    text = PDF_EMBED_RE.sub(_embed_repl, text)
    text = PDF_LINK_RE.sub(_link_repl, text)
    text = LOCAL_ARXIV_PDF_RE.sub(
        lambda match: f"https://arxiv.org/pdf/{match.group(1)}",
        text,
    )
    return text


def copy_markdown_tree(src: Path, dst: Path, pdf_index: dict[str, Path]) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)

    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        if path.suffix.lower() == ".md":
            content = path.read_text(encoding="utf-8")
            content = replace_pdf_embeds(content, target, pdf_index)
            target.write_text(content, encoding="utf-8")
        else:
            shutil.copy2(path, target)


def copy_home_assets() -> None:
    source = ROOT / HOME_GUIDE_SOURCE
    if not source.exists():
        return
    target = DOCS_DIR / HOME_GUIDE_TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def ensure_index() -> None:
    index_path = DOCS_DIR / "index.md"
    if index_path.exists():
        return
    index_path.write_text(
        "# LLM Paper Daily Digest\n\n"
        "這是一個每日自動抓取 arXiv LLM 論文、生成結構化摘要並同步到 Obsidian 的知識庫。\n",
        encoding="utf-8",
    )


def extract_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass
    return path.stem


def parse_frontmatter(path: Path) -> dict[str, object]:
    """Parse the small YAML subset used by generated paper notes."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    data: dict[str, object] = {}
    current_list: str | None = None
    for line in text[4:end].splitlines():
        item = re.match(r"^\s+-\s+(.+)$", line)
        if item and current_list:
            value = item.group(1).strip().strip('"').strip("'")
            values = data.setdefault(current_list, [])
            if isinstance(values, list):
                values.append(value)
            continue

        field = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not field:
            continue
        key, raw_value = field.groups()
        if raw_value:
            data[key] = raw_value.strip().strip('"').strip("'")
            current_list = None
        else:
            data[key] = []
            current_list = key
    return data


def extract_section(path: Path, heading: str, max_chars: int = 220) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$\n+(.*?)(?=^##\s|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return ""
    value = re.sub(r"\s+", " ", match.group(1)).strip()
    return value if len(value) <= max_chars else value[: max_chars - 1].rstrip() + "…"


def normalize_paper_category(category: str, tags: list[str]) -> str:
    """Collapse historical labels into the six categories used by the site."""
    normalized = CATEGORY_ALIASES.get(category.strip().lower())
    if normalized:
        return normalized

    tag_set = {tag.strip().lower() for tag in tags}
    fallbacks = (
        ({"multimodal", "multimodal-safety"}, "Multimodal Evaluation"),
        ({"safety", "alignment", "red-teaming", "prompt-injection", "jailbreak"}, "Safety & Alignment"),
        ({"rag", "rag-evaluation"}, "RAG Evaluation"),
        ({"hallucination", "faithfulness"}, "Hallucination & Faithfulness"),
        ({"agent", "agent-evaluation"}, "Agent Evaluation"),
    )
    for candidates, canonical in fallbacks:
        if tag_set & candidates:
            return canonical
    return "Benchmark"


def paper_records() -> list[dict[str, object]]:
    paper_dir = DOCS_DIR / "Papers"
    if not paper_dir.exists():
        return []

    records: list[dict[str, object]] = []
    for path in paper_dir.glob("*.md"):
        if path.name == "index.md":
            continue
        metadata = parse_frontmatter(path)
        title = str(metadata.get("title") or extract_title(path))
        tags = metadata.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        tag_values = [str(tag) for tag in tags]
        records.append({
            "path": path,
            "url": f"{quote(path.stem, safe='')}/",
            "title": title,
            "date": str(metadata.get("date") or ""),
            "arxiv_id": str(metadata.get("arxiv_id") or ""),
            "category": normalize_paper_category(
                str(metadata.get("category") or ""), tag_values
            ),
            "relevance": int(str(metadata.get("relevance") or "0")),
            "tags": tag_values,
            "authors": str(metadata.get("authors") or ""),
            "summary": extract_section(path, "摘要（中文翻譯）"),
        })
    return sorted(
        records,
        key=lambda item: (str(item["date"]), str(item["arxiv_id"])),
        reverse=True,
    )


def daily_records() -> list[dict[str, object]]:
    daily_dir = DOCS_DIR / "Daily"
    if not daily_dir.exists():
        return []
    records = []
    for path in daily_dir.glob("*.md"):
        if path.name == "index.md":
            continue
        text = path.read_text(encoding="utf-8")
        count_match = re.search(r'data-paper-count="(\d+)"', text)
        if not count_match:
            count_match = re.search(r"今日分析\s+\*\*(\d+)\*\*", text)
        records.append({
            "date": path.stem,
            "title": extract_title(path),
            "count": int(count_match.group(1)) if count_match else 0,
            "url": f"{quote(path.stem, safe='')}/",
        })
    return sorted(records, key=lambda item: str(item["date"]), reverse=True)


def _shorten(value: object, max_chars: int = 280) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip("，。、；： ") + "…"


def _paper_note_url(arxiv_id: str) -> str | None:
    paper_dir = DOCS_DIR / "Papers"
    # ``[]`` has special meaning in glob patterns, so compare the literal
    # filename prefix instead of interpolating the arXiv ID into a glob.
    matches = sorted(
        path for path in paper_dir.glob("*.md")
        if path.name.startswith(f"[{arxiv_id}]")
    )
    if not matches:
        return None
    return f"../../Papers/{quote(matches[0].stem, safe='')}/"


def write_daily_detail_pages() -> None:
    """Render structured DailyJSON data as mobile-friendly web digest cards."""
    json_dir = ROOT / "DailyJSON"
    daily_dir = DOCS_DIR / "Daily"
    if not json_dir.exists() or not daily_dir.exists():
        return

    for json_path in sorted(json_dir.glob("????-??-??.json")):
        output_path = daily_dir / f"{json_path.stem}.md"
        if not output_path.exists():
            continue
        try:
            records = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(records, list) or not records:
            continue

        cards: list[str] = []
        for item in records:
            if not isinstance(item, dict):
                continue
            paper = item.get("paper") or {}
            analysis = item.get("analysis") or {}
            if not isinstance(paper, dict) or not isinstance(analysis, dict):
                continue

            arxiv_id = str(paper.get("arxiv_id") or "")
            title = html.escape(str(paper.get("title") or arxiv_id or "未命名論文"))
            category = html.escape(str(analysis.get("category") or "uncategorized"))
            relevance = max(0, min(5, int(analysis.get("relevance") or 0)))
            stars = "★" * relevance + "☆" * (5 - relevance)
            tags = [str(tag) for tag in analysis.get("tags") or []]
            insights = [str(value) for value in analysis.get("insights") or []]
            contributions = [str(value) for value in analysis.get("core_contributions") or []]
            published = str(paper.get("published") or "")[:10]
            note_url = _paper_note_url(arxiv_id)

            insight_items = "".join(
                f"<li>{html.escape(_shorten(value, 220))}</li>"
                for value in (insights or contributions)[:3]
            )
            note_action = (
                f'<a class="daily-action daily-action--primary" href="{note_url}">閱讀完整分析</a>'
                if note_url else ""
            )
            arxiv_url = html.escape(str(paper.get("arxiv_url") or ""), quote=True)
            pdf_url = html.escape(str(paper.get("pdf_url") or ""), quote=True)
            external_actions = "".join([
                f'<a class="daily-action" href="{arxiv_url}" target="_blank" rel="noopener">arXiv 摘要 ↗</a>' if arxiv_url else "",
                f'<a class="daily-action" href="{pdf_url}" target="_blank" rel="noopener">開啟 PDF ↗</a>' if pdf_url else "",
            ])

            cards.append(f"""
<article class="daily-paper-card">
  <div class="daily-paper-card__meta">
    <span class="research-category">{category}</span>
    <span>arXiv {html.escape(arxiv_id)}</span>
    {f'<span>{html.escape(published)}</span>' if published else ''}
    <span class="daily-paper-card__rating" aria-label="相關度 {relevance} 顆星">{stars}</span>
  </div>
  <h2>{title}</h2>
  <div class="daily-paper-card__tags">{_tag_badges(tags)}</div>
  <section class="daily-takeaway" aria-label="研究重點">
    <span>研究重點</span>
    <p>{html.escape(_shorten(analysis.get('problem_statement') or analysis.get('abstract_zh'), 330))}</p>
  </section>
  {f'<h3>值得注意的洞察</h3><ul class="daily-insights">{insight_items}</ul>' if insight_items else ''}
  <details class="daily-abstract">
    <summary>展開完整中文摘要</summary>
    <p>{html.escape(str(analysis.get('abstract_zh') or '尚無中文摘要。'))}</p>
  </details>
  <div class="daily-paper-card__actions">{note_action}{external_actions}</div>
</article>""".strip())

        if not cards:
            continue
        count = len(cards)
        content = f"""# {json_path.stem} 每日論文摘要

<div class="daily-detail-hero" data-paper-count="{count}">
  <span class="daily-detail-hero__eyebrow">DAILY RESEARCH DIGEST</span>
  <div><strong>{count}</strong><span>篇精選論文</span></div>
  <p>今日分析 <strong>{count}</strong> 篇 LLM 評測相關論文。先讀研究重點與洞察，需要細節時再展開完整摘要。</p>
</div>

## 今日精選

<div class="daily-paper-list">
{chr(10).join(cards)}
</div>

<p class="daily-generated-note">由 LLM Paper Daily Digest 自動整理；重要研究結論請以原始論文為準。</p>
"""
        output_path.write_text(content, encoding="utf-8")


def _tag_badges(tags: list[str]) -> str:
    return "".join(
        f'<span class="research-tag">{html.escape(tag)}</span>' for tag in tags
    )


def write_papers_index() -> None:
    records = paper_records()
    paper_dir = DOCS_DIR / "Papers"
    paper_dir.mkdir(parents=True, exist_ok=True)
    present_categories = {str(record["category"]) for record in records}
    categories = [value for value in CANONICAL_CATEGORIES if value in present_categories]
    tags = sorted({tag for record in records for tag in record["tags"]})

    category_buttons = "\n".join(
        f'<button class="paper-category-chip" type="button" data-category="{html.escape(value, quote=True)}" aria-pressed="false">{html.escape(value)}</button>'
        for value in categories
    )
    tag_options = "\n".join(
        f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>'
        for value in tags
    )
    cards = []
    for record in records:
        title = html.escape(str(record["title"]))
        category = html.escape(str(record["category"]))
        tags_value = " ".join(str(tag) for tag in record["tags"])
        search_value = " ".join([
            str(record["title"]), str(record["arxiv_id"]),
            str(record["category"]), tags_value, str(record["authors"]),
            str(record["summary"]),
        ]).lower()
        stars = "★" * int(record["relevance"]) or "待評分"
        arxiv_id = html.escape(str(record["arxiv_id"]), quote=True)
        cards.append(f"""
<article class="research-card paper-entry"
  data-search="{html.escape(search_value, quote=True)}"
  data-category="{html.escape(str(record['category']), quote=True)}"
  data-tags="{html.escape(tags_value, quote=True)}"
  data-date="{html.escape(str(record['date']), quote=True)}"
  data-relevance="{int(record['relevance'])}"
  data-title="{html.escape(str(record['title']).lower(), quote=True)}">
  <div class="research-card__meta">
    <span>{html.escape(str(record['date']))}</span>
    <span>{html.escape(str(record['arxiv_id']))}</span>
    <span class="research-relevance" aria-label="相關度 {int(record['relevance'])} 顆星">{stars}</span>
  </div>
  <h2><a href="{record['url']}">{title}</a></h2>
  <p class="research-card__summary">{html.escape(str(record['summary']) or '尚無中文摘要。')}</p>
  <div class="research-card__tags"><span class="research-category">{category}</span>{_tag_badges(record['tags'])}</div>
  <div class="paper-card-actions">
    <a class="paper-card-action paper-card-action--primary" href="{record['url']}">閱讀分析</a>
    <a class="paper-card-action" href="https://arxiv.org/abs/{arxiv_id}" target="_blank" rel="noopener">arXiv ↗</a>
    <a class="paper-card-action" href="https://arxiv.org/pdf/{arxiv_id}" target="_blank" rel="noopener">PDF ↗</a>
  </div>
</article>""".strip())

    latest_date = max((str(record["date"]) for record in records), default="—")
    content = f"""# 論文庫

聚焦 LLM 評測、RAG、安全對齊、Agent 與多模態評估。主分類已統一為六類，細節仍可用標籤深入篩選。

<div id="paper-library" class="paper-library">
  <div class="paper-library-hero" aria-label="論文庫摘要">
    <div><strong>{len(records)}</strong><span>篇論文</span></div>
    <div><strong>{len(categories)}</strong><span>個核心分類</span></div>
    <div><strong>{html.escape(latest_date)}</strong><span>最近更新</span></div>
  </div>
  <div class="paper-toolbar" role="search" aria-label="搜尋與排序論文">
    <label><span>搜尋論文</span>
      <input id="paper-search" type="search" placeholder="輸入標題、arXiv ID、作者或摘要關鍵字" autocomplete="off">
    </label>
    <label><span>排序方式</span>
      <select id="paper-sort">
        <option value="date-desc">最新發布</option>
        <option value="relevance-desc">相關度最高</option>
        <option value="title-asc">標題 A–Z</option>
      </select>
    </label>
  </div>
  <div class="paper-category-filter" aria-label="主分類">
    <button class="paper-category-chip is-active" type="button" data-category="" aria-pressed="true">全部</button>
    {category_buttons}
  </div>
  <details class="paper-advanced-filters">
    <summary>進階篩選</summary>
    <div>
      <label><span>研究標籤</span>
        <select id="paper-tag">
          <option value="">全部標籤</option>
          {tag_options}
        </select>
      </label>
      <button id="paper-reset" type="button">清除條件</button>
    </div>
  </details>
  <div class="paper-results-row">
    <p id="paper-results" class="paper-results" aria-live="polite">顯示 {min(12, len(records))} / {len(records)} 篇論文</p>
  </div>
  <div class="research-grid paper-grid">
    {chr(10).join(cards) if cards else '<p>尚無論文。</p>'}
  </div>
  <p id="paper-empty" class="paper-empty" hidden>找不到符合條件的論文，請調整篩選條件。</p>
  <div class="paper-load-more-wrap"><button id="paper-load-more" class="paper-load-more" type="button">載入更多論文</button></div>
</div>
"""
    (paper_dir / "index.md").write_text(content, encoding="utf-8")


def write_daily_index() -> None:
    records = daily_records()
    daily_dir = DOCS_DIR / "Daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    cards = "\n".join(
        f"""<a class="digest-card" href="{record['url']}">
  <span class="digest-card__date">{html.escape(str(record['date']))}</span>
  <strong>{int(record['count'])} 篇論文</strong>
  <span>閱讀當日摘要 →</span>
</a>"""
        for record in records
    )
    content = f"""# 每日論文摘要

每日自動從 arXiv 篩選相關論文，使用 AI 產生結構化繁體中文分析，再經 Pull Request 審閱後發布。

<div class="digest-grid">
{cards if cards else '<p>尚無每日摘要。</p>'}
</div>
"""
    (daily_dir / "index.md").write_text(content, encoding="utf-8")


def write_home_index() -> None:
    papers = paper_records()
    dailies = daily_records()
    topic_dir = DOCS_DIR / "Topics"
    topic_count = len([path for path in topic_dir.glob("*.md") if path.name != "index.md"]) if topic_dir.exists() else 0
    latest_daily = dailies[0] if dailies else None
    latest_papers = papers[:3]

    paper_cards = []
    for record in latest_papers:
        paper_cards.append(f"""<article class="research-card research-card--compact">
  <div class="research-card__meta"><span>{html.escape(str(record['date']))}</span><span>{html.escape(str(record['arxiv_id']))}</span></div>
  <h3><a href="Papers/{record['url']}">{html.escape(str(record['title']))}</a></h3>
  <p>{html.escape(str(record['summary']) or '尚無中文摘要。')}</p>
  <div class="research-card__tags"><span class="research-category">{html.escape(str(record['category']))}</span>{_tag_badges(record['tags'][:2])}</div>
</article>""")

    if latest_daily:
        digest_panel = f"""<div class="latest-digest">
  <div><span class="eyebrow">最新每日摘要</span><h2>{html.escape(str(latest_daily['date']))}</h2></div>
  <div><strong>{int(latest_daily['count'])}</strong><span>篇結構化論文分析</span></div>
  <a class="research-button" href="Daily/{latest_daily['url']}">閱讀今日摘要 →</a>
</div>"""
    else:
        digest_panel = '<div class="latest-digest"><p>尚無每日摘要。</p></div>'

    content = f"""# LLM 評測知識庫

<p class="research-lead">系統化整理 LLM 評測策略、RAG 品質量測、基準測試、安全性與最新論文的實作知識庫。</p>

<div class="knowledge-stats" aria-label="知識庫統計">
  <div><strong>{len(papers)}</strong><span>篇論文</span></div>
  <div><strong>{topic_count}</strong><span>個研究主題</span></div>
  <div><strong>{len(dailies)}</strong><span>份每日摘要</span></div>
</div>

{digest_panel}

## 快速開始

<div class="hub-grid">
  <a class="hub-card" href="Evaluation-Framework/"><span>📊</span><strong>評測策略與指標</strong><small>從準確率、真實性到 Responsible AI</small></a>
  <a class="hub-card" href="Benchmark-Governance/"><span>🧪</span><strong>基準測試與 RAG 工具</strong><small>RAGAS、DeepEval、Arize Phoenix 實作</small></a>
  <a class="hub-card" href="Security-RedTeam/"><span>🛡️</span><strong>安全性與紅隊演練</strong><small>Prompt Injection、Jailbreak 與 PII 防護</small></a>
  <a class="hub-card" href="Papers/"><span>📚</span><strong>搜尋論文庫</strong><small>按分類、標籤與關鍵字篩選</small></a>
</div>

## 最新論文

<div class="research-grid research-grid--latest">
{chr(10).join(paper_cards) if paper_cards else '<p>尚無論文。</p>'}
</div>

<p class="section-action"><a class="research-button research-button--secondary" href="Papers/">查看完整論文庫 →</a></p>

## NotebookLM 評測與安全指南

<div class="home-guide-panel" markdown>
這份由 NotebookLM 協助整理的完整指南，涵蓋企業級 LLM 品質驗證、評測指標與安全防禦策略。

[📥 下載完整評測與安全指南 (PDF)]({HOME_GUIDE_TARGET.as_posix()})

![LLM Evaluation Guide]({HOME_GUIDE_TARGET.as_posix()}#navpanes=0&toolbar=0){{ type=application/pdf class="home-guide-embed" }}
</div>

!!! tip "詢問 AI 助教"
    點擊右下角聊天按鈕，可以詢問評測方法、RAG 工具、安全測試與論文重點。
"""
    (DOCS_DIR / "index.md").write_text(content, encoding="utf-8")


def write_section_index(section: str, title: str, limit: int | None = None, reverse: bool = False) -> None:
    section_dir = DOCS_DIR / section
    if not section_dir.exists():
        return

    paths = [p for p in section_dir.rglob("*.md") if p.name != "index.md"]
    paths = sorted(paths, reverse=reverse)
    if limit is not None:
        paths = paths[:limit]

    items = []
    for path in paths:
        if path.name == "index.md":
            continue
        rel = path.relative_to(section_dir)
        label = extract_title(path)
        items.append(f"- [{label}]({rel.as_posix()})")

    content = [f"# {title}", ""]
    content.extend(items or ["（尚無內容）"])
    (section_dir / "index.md").write_text("\n".join(content) + "\n", encoding="utf-8")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_index = build_pdf_index(ROOT)
    copy_home_assets()

    for name in SOURCE_DIRS:
        src = ROOT / name
        if not src.exists():
            continue
        dst = DOCS_DIR / name
        copy_markdown_tree(src, dst, pdf_index)

    write_daily_detail_pages()
    write_daily_index()
    write_section_index("Weekly", "Weekly", reverse=True)
    write_section_index("Topics", "Topics")
    write_papers_index()
    write_home_index()


if __name__ == "__main__":
    main()
