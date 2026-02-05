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
from analyzer import analyze_papers
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

def analysis_to_dict(analysis: AnalysisResult) -> dict:
    """將 AnalysisResult 物件轉為 dict"""
    return {
        "abstract_zh": analysis.abstract_zh,
        "problem_statement": analysis.problem_statement,
        "proposed_solution": analysis.proposed_solution,
        "core_contributions": analysis.core_contributions,
        "methodology": analysis.methodology,
        "key_results": analysis.key_results,
        "insights": analysis.insights,
        "limitations": analysis.limitations,
        "tags": analysis.tags,
        "relevance": analysis.relevance,
        "related_topics": analysis.related_topics,
        "category": analysis.category,
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

def _parse_date_arg(date_arg: str | None) -> str:
    if not date_arg or date_arg.lower() == "today":
        return datetime.now().strftime("%Y-%m-%d")
    return date_arg


def cmd_digest(args) -> None:
    """完整每日摘要流程（抓取 → 篩選 → 分析 → 產 JSON → 寫入 Obsidian）"""
    load_dotenv()
    config = load_config()

    date = _parse_date_arg(args.date)
    top_n = args.top or 10

    api_key = os.environ.get("OPENAI_API_KEY")
    if args.require_api_key and not api_key:
        output_json({
            "status": "error",
            "message": "缺少 OPENAI_API_KEY（已設定 --require-api-key）",
        })
        sys.exit(2)

    # 抓取 + 篩選
    categories = config["arxiv"]["categories"]
    keywords_path = Path(__file__).parent / "keywords.yaml"
    keywords = load_keywords(str(keywords_path))

    papers = fetch_papers_by_date(
        categories=categories,
        date=date,
        max_results=config["arxiv"]["max_results"]
    )

    min_score = args.min_score or config["filter"]["min_score"]
    top_papers = get_top_papers(
        papers=papers,
        keywords=keywords,
        min_score=min_score,
        top_n=top_n
    )

    # 分析
    from openai import OpenAI
    client = OpenAI(api_key=api_key) if api_key else None

    model = args.model or config["openai"]["model"]
    max_tokens = args.max_tokens or config["openai"]["max_tokens"]

    processed = analyze_papers(
        papers=top_papers,
        client=client,
        model=model,
        max_tokens=max_tokens,
        verbose=True
    )

    items = []
    for paper, analysis in processed:
        items.append({
            "paper": paper_to_dict(paper),
            "analysis": analysis_to_dict(analysis),
        })

    # 輸出 JSON 檔（可選）
    out_path = None
    if args.out:
        out_path = Path(args.out).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    # 寫入 Obsidian（可選）
    written = {
        "notes": [],
        "daily": None,
    }
    if args.write:
        vault_path = Path(
            args.vault or
            os.environ.get("OBSIDIAN_VAULT_PATH") or
            config["obsidian"]["vault_path"]
        ).expanduser()
        templates_dir = str(Path(__file__).parent / "templates")

        # 每篇筆記 + Topics
        # write_from_json 需要單篇 JSON 檔，因此使用臨時檔案轉接
        # （避免重複實作 writer 邏輯）
        tmp_dir = Path(args.tmp_dir).expanduser() if args.tmp_dir else Path("/tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)

        for item in items:
            arxiv_id = item["paper"]["arxiv_id"]
            tmp_json = tmp_dir / f"lpdd_{date}_{arxiv_id}.json"
            with open(tmp_json, "w", encoding="utf-8") as f:
                json.dump(item, f, ensure_ascii=False, indent=2)
            note_path = write_from_json(
                json_path=str(tmp_json),
                vault_path=vault_path,
                templates_dir=templates_dir,
                download_pdfs=(not args.no_download_pdfs),
                verbose=True
            )
            written["notes"].append(str(note_path))

        # 每日摘要
        daily_json = out_path
        if daily_json is None:
            daily_json = tmp_dir / f"lpdd_{date}_daily.json"
            with open(daily_json, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
        daily_path = write_daily_from_json(
            json_path=str(daily_json),
            date=date,
            vault_path=vault_path,
            templates_dir=templates_dir
        )
        written["daily"] = str(daily_path)

    result = {
        "status": "success",
        "date": date,
        "total_fetched": len(papers),
        "min_score": min_score,
        "count": len(items),
        "json_path": str(out_path) if out_path else None,
        "written": written if args.write else None,
        "model": model,
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

    # digest 子命令（完整流程，適合 automation）
    digest_parser = subparsers.add_parser("digest", help="完整每日流程：抓取/篩選/分析/輸出 JSON/寫入 Obsidian")
    digest_parser.add_argument("--top", type=int, default=10, help="取 Top N 篇進行分析")
    digest_parser.add_argument("--date", type=str, help="指定日期 (YYYY-MM-DD) 或 today")
    digest_parser.add_argument("--min-score", type=int, help="最低分數（覆蓋 config.yaml）")
    digest_parser.add_argument("--out", type=str, help="輸出 JSON 檔案路徑（陣列格式）")
    digest_parser.add_argument("--write", action="store_true", help="寫入 Obsidian（論文筆記 + Topics + Daily）")
    digest_parser.add_argument("--vault", type=str, help="Obsidian Vault 路徑（覆蓋 config/env）")
    digest_parser.add_argument("--model", type=str, help="OpenAI model（覆蓋 config.yaml）")
    digest_parser.add_argument("--max-tokens", type=int, help="max_completion_tokens（覆蓋 config.yaml）")
    digest_parser.add_argument("--require-api-key", action="store_true", help="若缺少 OPENAI_API_KEY 則視為錯誤並退出")
    digest_parser.add_argument("--no-download-pdfs", action="store_true", help="寫入 Obsidian 時不下載 PDF")
    digest_parser.add_argument("--tmp-dir", type=str, help="寫入流程使用的暫存 JSON 目錄（預設 /tmp）")
    digest_parser.set_defaults(func=cmd_digest)

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
