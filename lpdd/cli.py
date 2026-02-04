#!/usr/bin/env python3
"""
LLM Paper Daily Digest - 統一 CLI 入口點

供 Claude Skills 使用的命令列介面，輸出 JSON 格式。
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

from models import Paper, AnalysisResult
from fetcher import fetch_papers, fetch_papers_by_date, fetch_paper_by_id
from filter import load_keywords, get_top_papers, filter_papers, search_by_keyword
from writer import write_from_json, write_daily_from_json


def load_config(config_path: str = None) -> dict:
    """載入設定檔"""
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def paper_to_dict(paper: Paper) -> dict:
    """將 Paper 物件轉為 dict"""
    return {
        "arxiv_id": paper.arxiv_id,
        "title": paper.title,
        "abstract": paper.abstract,
        "authors": paper.authors,
        "categories": paper.categories,
        "published": paper.published.isoformat(),
        "pdf_url": paper.pdf_url,
        "arxiv_url": paper.arxiv_url,
        "score": paper.score,
    }


def output_json(data: dict | list, pretty: bool = True) -> None:
    """輸出 JSON 到 stdout"""
    if pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, ensure_ascii=False))


def cmd_fetch(args) -> None:
    """抓取論文子命令"""
    config = load_config()
    categories = config["arxiv"]["categories"]

    if args.date:
        papers = fetch_papers_by_date(
            categories=categories,
            date=args.date,
            max_results=config["arxiv"]["max_results"]
        )
    else:
        hours = args.hours or config["arxiv"]["hours_lookback"]
        papers = fetch_papers(
            categories=categories,
            hours=hours,
            max_results=config["arxiv"]["max_results"]
        )

    result = {
        "status": "success",
        "count": len(papers),
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "papers": [paper_to_dict(p) for p in papers]
    }
    output_json(result)


def cmd_filter(args) -> None:
    """篩選論文子命令"""
    config = load_config()
    keywords_path = Path(__file__).parent / "keywords.yaml"
    keywords = load_keywords(str(keywords_path))

    # 從 stdin 讀取論文列表
    input_data = json.load(sys.stdin)
    papers_data = input_data.get("papers", input_data)

    # 重建 Paper 物件
    papers = []
    for p in papers_data:
        paper = Paper(
            arxiv_id=p["arxiv_id"],
            title=p["title"],
            abstract=p["abstract"],
            authors=p["authors"],
            categories=p["categories"],
            published=datetime.fromisoformat(p["published"]),
            pdf_url=p["pdf_url"],
        )
        papers.append(paper)

    # 篩選
    min_score = args.min_score or config["filter"]["min_score"]
    top_n = args.top or config["filter"]["top_n"]

    top_papers = get_top_papers(
        papers=papers,
        keywords=keywords,
        min_score=min_score,
        top_n=top_n
    )

    result = {
        "status": "success",
        "count": len(top_papers),
        "min_score": min_score,
        "papers": [paper_to_dict(p) for p in top_papers]
    }
    output_json(result)


def cmd_get(args) -> None:
    """取得單篇論文子命令"""
    paper = fetch_paper_by_id(args.arxiv_id)

    if paper:
        result = {
            "status": "success",
            "paper": paper_to_dict(paper)
        }
    else:
        result = {
            "status": "error",
            "message": f"找不到論文: {args.arxiv_id}"
        }

    output_json(result)


def cmd_search(args) -> None:
    """搜尋論文子命令"""
    config = load_config()
    categories = config["arxiv"]["categories"]

    # 抓取最近 N 天的論文
    days = args.days or 7
    hours = days * 24

    papers = fetch_papers(
        categories=categories,
        hours=hours,
        max_results=500  # 搜尋時抓更多
    )

    # 關鍵字搜尋
    matched = search_by_keyword(papers, args.keyword)

    result = {
        "status": "success",
        "keyword": args.keyword,
        "days": days,
        "count": len(matched),
        "papers": [paper_to_dict(p) for p in matched]
    }
    output_json(result)


def cmd_write(args) -> None:
    """寫入 Obsidian 子命令"""
    load_dotenv()

    vault_path = Path(
        args.vault or
        os.environ.get("OBSIDIAN_VAULT_PATH") or
        load_config()["obsidian"]["vault_path"]
    ).expanduser()

    templates_dir = str(Path(__file__).parent / "templates")

    try:
        output_path = write_from_json(
            json_path=args.json_file,
            vault_path=vault_path,
            templates_dir=templates_dir
        )
        result = {
            "status": "success",
            "output_path": str(output_path)
        }
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }

    output_json(result)


def cmd_write_daily(args) -> None:
    """寫入每日摘要子命令"""
    load_dotenv()

    vault_path = Path(
        args.vault or
        os.environ.get("OBSIDIAN_VAULT_PATH") or
        load_config()["obsidian"]["vault_path"]
    ).expanduser()

    templates_dir = str(Path(__file__).parent / "templates")
    date = args.date or datetime.now().strftime("%Y-%m-%d")

    try:
        output_path = write_daily_from_json(
            json_path=args.json_file,
            date=date,
            vault_path=vault_path,
            templates_dir=templates_dir
        )
        result = {
            "status": "success",
            "output_path": str(output_path),
            "date": date
        }
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }

    output_json(result)


def cmd_trending(args) -> None:
    """查詢熱門論文子命令"""
    import urllib.request
    import urllib.parse

    topic = args.topic or "large language model evaluation"
    classic = args.classic

    # 使用 Semantic Scholar API 搜尋
    # API 文檔: https://api.semanticscholar.org/
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    # 建立查詢參數
    params = {
        "query": topic,
        "limit": args.limit or 10,
        "fields": "title,authors,year,citationCount,externalIds,abstract,url",
    }

    if classic:
        # 經典論文：按引用數排序
        params["sort"] = "citationCount:desc"
    else:
        # 熱門論文：最近的高引用
        params["year"] = "2023-2025"
        params["sort"] = "citationCount:desc"

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LLM-Paper-Digest/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        papers = []
        for item in data.get("data", []):
            arxiv_id = None
            external_ids = item.get("externalIds", {})
            if external_ids:
                arxiv_id = external_ids.get("ArXiv")

            papers.append({
                "title": item.get("title", ""),
                "authors": [a.get("name", "") for a in item.get("authors", [])[:3]],
                "year": item.get("year"),
                "citations": item.get("citationCount", 0),
                "arxiv_id": arxiv_id,
                "url": item.get("url", ""),
                "abstract": item.get("abstract", "")[:300] if item.get("abstract") else "",
            })

        result = {
            "status": "success",
            "topic": topic,
            "mode": "classic" if classic else "trending",
            "count": len(papers),
            "papers": papers
        }

    except Exception as e:
        result = {
            "status": "error",
            "message": f"搜尋失敗: {str(e)}",
            "topic": topic
        }

    output_json(result)


def cmd_list(args) -> None:
    """列出論文子命令（fetch + filter 合併）"""
    config = load_config()
    categories = config["arxiv"]["categories"]
    keywords_path = Path(__file__).parent / "keywords.yaml"
    keywords = load_keywords(str(keywords_path))

    # 抓取論文
    if args.date:
        papers = fetch_papers_by_date(
            categories=categories,
            date=args.date,
            max_results=config["arxiv"]["max_results"]
        )
    else:
        papers = fetch_papers(
            categories=categories,
            hours=config["arxiv"]["hours_lookback"],
            max_results=config["arxiv"]["max_results"]
        )

    # 篩選
    min_score = config["filter"]["min_score"]
    top_n = args.top or 10

    top_papers = get_top_papers(
        papers=papers,
        keywords=keywords,
        min_score=min_score,
        top_n=top_n
    )

    result = {
        "status": "success",
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "total_fetched": len(papers),
        "count": len(top_papers),
        "papers": [paper_to_dict(p) for p in top_papers]
    }
    output_json(result)


def main():
    parser = argparse.ArgumentParser(
        description="LLM Paper Daily Digest CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # fetch 子命令
    fetch_parser = subparsers.add_parser("fetch", help="抓取 arXiv 論文")
    fetch_parser.add_argument("--date", type=str, help="指定日期 (YYYY-MM-DD)")
    fetch_parser.add_argument("--hours", type=int, help="回溯時數")
    fetch_parser.set_defaults(func=cmd_fetch)

    # filter 子命令
    filter_parser = subparsers.add_parser("filter", help="篩選論文（從 stdin 讀取 JSON）")
    filter_parser.add_argument("--top", type=int, help="取 Top N 篇")
    filter_parser.add_argument("--min-score", type=int, help="最低分數")
    filter_parser.set_defaults(func=cmd_filter)

    # list 子命令（fetch + filter 合併，方便使用）
    list_parser = subparsers.add_parser("list", help="列出篩選後的論文")
    list_parser.add_argument("--top", type=int, default=10, help="取 Top N 篇")
    list_parser.add_argument("--date", type=str, help="指定日期 (YYYY-MM-DD)")
    list_parser.set_defaults(func=cmd_list)

    # get 子命令
    get_parser = subparsers.add_parser("get", help="取得單篇論文")
    get_parser.add_argument("arxiv_id", type=str, help="arXiv ID")
    get_parser.set_defaults(func=cmd_get)

    # search 子命令
    search_parser = subparsers.add_parser("search", help="搜尋論文")
    search_parser.add_argument("keyword", type=str, help="搜尋關鍵字")
    search_parser.add_argument("--days", type=int, default=7, help="天數範圍")
    search_parser.set_defaults(func=cmd_search)

    # trending 子命令
    trending_parser = subparsers.add_parser("trending", help="查詢熱門/經典論文")
    trending_parser.add_argument("topic", type=str, nargs="?", help="搜尋主題")
    trending_parser.add_argument("--classic", action="store_true", help="搜尋經典論文")
    trending_parser.add_argument("--limit", type=int, default=10, help="結果數量")
    trending_parser.set_defaults(func=cmd_trending)

    # write 子命令
    write_parser = subparsers.add_parser("write", help="寫入論文筆記到 Obsidian")
    write_parser.add_argument("json_file", type=str, help="分析結果 JSON 檔案路徑")
    write_parser.add_argument("--vault", type=str, help="Obsidian Vault 路徑")
    write_parser.set_defaults(func=cmd_write)

    # write-daily 子命令
    write_daily_parser = subparsers.add_parser("write-daily", help="寫入每日摘要")
    write_daily_parser.add_argument("json_file", type=str, help="論文分析 JSON 檔案路徑")
    write_daily_parser.add_argument("--date", type=str, help="日期 (YYYY-MM-DD)")
    write_daily_parser.add_argument("--vault", type=str, help="Obsidian Vault 路徑")
    write_daily_parser.set_defaults(func=cmd_write_daily)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
