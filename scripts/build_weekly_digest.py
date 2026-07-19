#!/usr/bin/env python3
"""Build a deterministic weekly research digest from DailyJSON files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def load_period(
    input_dir: Path,
    start_date: date,
    end_date: date,
) -> tuple[list[dict[str, Any]], list[date]]:
    papers_by_id: dict[str, dict[str, Any]] = {}
    covered_dates: list[date] = []

    current = start_date
    while current <= end_date:
        path = input_dir / f"{current.isoformat()}.json"
        if path.exists():
            covered_dates.append(current)
            try:
                records = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                raise ValueError(f"Cannot read {path}: {exc}") from exc
            if not isinstance(records, list):
                raise ValueError(f"Expected a JSON array in {path}")

            for record in records:
                paper = record.get("paper") or {}
                analysis = record.get("analysis") or {}
                arxiv_id = str(paper.get("arxiv_id") or "").strip()
                if not arxiv_id:
                    continue
                existing = papers_by_id.get(arxiv_id)
                relevance = int(analysis.get("relevance") or 0)
                existing_relevance = int(
                    ((existing or {}).get("analysis") or {}).get("relevance") or 0
                )
                if existing is None or relevance > existing_relevance:
                    papers_by_id[arxiv_id] = record
        current += timedelta(days=1)

    papers = sorted(
        papers_by_id.values(),
        key=lambda item: (
            -int((item.get("analysis") or {}).get("relevance") or 0),
            str((item.get("paper") or {}).get("published") or ""),
            str((item.get("paper") or {}).get("title") or ""),
        ),
    )
    return papers, covered_dates


def paper_link(record: dict[str, Any]) -> str:
    paper = record.get("paper") or {}
    arxiv_id = str(paper.get("arxiv_id") or "").strip()
    title = str(paper.get("title") or arxiv_id).strip().replace("|", "-")
    return f"[{title}](https://arxiv.org/abs/{arxiv_id})"


def render_weekly_digest(
    papers: list[dict[str, Any]],
    covered_dates: list[date],
    start_date: date,
    end_date: date,
) -> str:
    iso_year, iso_week, _ = end_date.isocalendar()
    week_id = f"{iso_year}-W{iso_week:02d}"
    category_counts = Counter(
        str((record.get("analysis") or {}).get("category") or "未分類")
        for record in papers
    )

    lines = [
        "---",
        "type: weekly-paper-digest",
        f"week: {week_id}",
        f"period_start: {start_date.isoformat()}",
        f"period_end: {end_date.isoformat()}",
        f"paper_count: {len(papers)}",
        "---",
        "",
        f"# {week_id} LLM 論文週報",
        "",
        f"統計區間：**{start_date.isoformat()} 至 {end_date.isoformat()}**  ",
        f"共彙整 **{len(papers)}** 篇不重複論文，涵蓋 **{len(covered_dates)}** 個有摘要資料的日期。",
        "",
        "## 本週重點論文",
        "",
    ]

    if papers:
        lines.extend(
            [
                "| 相關度 | 分類 | 論文 |",
                "|---:|---|---|",
            ]
        )
        for record in papers:
            analysis = record.get("analysis") or {}
            lines.append(
                f"| {int(analysis.get('relevance') or 0)} | "
                f"{analysis.get('category') or '未分類'} | {paper_link(record)} |"
            )
    else:
        lines.append("（本期尚無可用論文摘要。）")

    lines.extend(["", "## 主題分布", ""])
    if category_counts:
        for category, count in sorted(
            category_counts.items(), key=lambda item: (-item[1], item[0])
        ):
            lines.append(f"- **{category}**：{count} 篇")
    else:
        lines.append("- 尚無資料")

    lines.extend(["", "## 重點發現", ""])
    highlights: list[str] = []
    for record in papers[:5]:
        insights = (record.get("analysis") or {}).get("insights") or []
        if insights:
            highlights.append(f"- {insights[0]} — {paper_link(record)}")
    lines.extend(highlights or ["- 尚無可彙整的重點發現"])

    lines.extend(
        [
            "",
            "## 資料覆蓋",
            "",
            *(
                [f"- {covered.isoformat()}" for covered in covered_dates]
                if covered_dates
                else ["- 本期沒有 DailyJSON 輸入"]
            ),
            "",
            "---",
            "> 由 LLM Paper Daily Digest 週報流程自動生成。",
            "",
        ]
    )
    return "\n".join(lines)


def build_weekly_digest(
    input_dir: Path,
    output_dir: Path,
    end_date: date,
    days: int = 7,
    skip_empty: bool = False,
) -> Path | None:
    if days < 1:
        raise ValueError("days must be at least 1")
    start_date = end_date - timedelta(days=days - 1)
    papers, covered_dates = load_period(input_dir, start_date, end_date)
    if skip_empty and not papers:
        return None
    content = render_weekly_digest(papers, covered_dates, start_date, end_date)
    iso_year, iso_week, _ = end_date.isocalendar()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{iso_year}-W{iso_week:02d}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--end-date", type=parse_date, default=date.today())
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--input-dir", type=Path, default=Path("DailyJSON"))
    parser.add_argument("--output-dir", type=Path, default=Path("Weekly"))
    parser.add_argument(
        "--skip-empty",
        action="store_true",
        help="Do not write a weekly file when the period has no papers",
    )
    args = parser.parse_args()
    output_path = build_weekly_digest(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        end_date=args.end_date,
        days=args.days,
        skip_empty=args.skip_empty,
    )
    if output_path:
        print(output_path)
    else:
        print("No papers found; weekly digest skipped.")


if __name__ == "__main__":
    main()
