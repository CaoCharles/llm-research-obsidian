#!/usr/bin/env python3
"""Flatten Papers/ and PDFs/ into single-level directories."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "Papers"
PDFS = ROOT / "PDFs"


def flatten(dir_path: Path, pattern: str) -> None:
    if not dir_path.exists():
        return
    for path in list(dir_path.rglob(pattern)):
        if path.parent == dir_path:
            continue
        target = dir_path / path.name
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))

    # remove empty dirs
    for sub in sorted(dir_path.rglob("*"), reverse=True):
        if sub.is_dir() and not any(sub.iterdir()):
            sub.rmdir()


def main() -> None:
    flatten(PAPERS, "*.md")
    flatten(PDFS, "*.pdf")


if __name__ == "__main__":
    main()
