#!/usr/bin/env python3
"""
Sync Obsidian vault content into MkDocs docs/.

- Copies Daily/ Topics/ Papers/ into docs/ preserving structure.
- Converts Obsidian PDF embeds to mkdocs-pdf embeds.
"""
from __future__ import annotations

import re
import shutil
from os import path as osp
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
SOURCE_DIRS = ["Daily", "Topics", "Papers"]

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

    for name in SOURCE_DIRS:
        src = ROOT / name
        if not src.exists():
            continue
        dst = DOCS_DIR / name
        copy_markdown_tree(src, dst, pdf_index)

    write_section_index("Daily", "Daily", reverse=True)
    write_section_index("Topics", "Topics")
    write_section_index("Papers", "Papers", reverse=True)
    ensure_index()


if __name__ == "__main__":
    main()
