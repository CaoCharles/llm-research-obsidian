"""
LLM Paper Daily Digest - 主程式

每日從 arXiv 抓取 LLM 評測相關論文，使用 GPT 分析，寫入 Obsidian。
"""
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

import yaml
from dotenv import load_dotenv
from openai import OpenAI

from models import Paper, AnalysisResult
from fetcher import fetch_papers, fetch_papers_by_date
from filter import load_keywords, get_top_papers
from analyzer import analyze_papers
from writer import (
    write_paper_note,
    update_topic_page,
    write_daily_summary,
    init_vault_structure,
)


def load_config(config_path: str = "config.yaml") -> dict:
    """載入設定檔"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    # 載入 .env 檔案
    load_dotenv()
    
    # 解析命令列參數
    parser = argparse.ArgumentParser(
        description="LLM Paper Daily Digest - 自動化論文摘要系統"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="指定日期 (YYYY-MM-DD)，預設為今天"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="設定檔路徑"
    )
    parser.add_argument(
        "--keywords",
        type=str,
        default="keywords.yaml",
        help="關鍵字設定檔路徑"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模擬執行，不實際寫入檔案"
    )
    parser.add_argument(
        "--vault",
        type=str,
        help="覆蓋設定檔中的 Obsidian Vault 路徑"
    )
    args = parser.parse_args()
    
    # 檢查 API Key（允許缺省，會改用手動補充模板）
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 未設定 OPENAI_API_KEY，將跳過 LLM 分析並產生待補充摘要")
    
    # 載入設定
    print("📋 載入設定...")
    config = load_config(args.config)
    keywords = load_keywords(args.keywords)
    print(f"  • 載入 {len(keywords)} 個關鍵字")
    
    # 設定 Vault 路徑
    vault_path = Path(
        args.vault or 
        os.environ.get("OBSIDIAN_VAULT_PATH") or 
        config["obsidian"]["vault_path"]
    ).expanduser()
    print(f"  • Vault 路徑: {vault_path}")
    
    # 決定日期
    if args.date:
        target_date = args.date
        print(f"  • 指定日期: {target_date}")
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")
        print(f"  • 今日日期: {target_date}")
    
    # 1. 抓取論文
    print("\n🔍 抓取 arXiv 論文...")
    categories = config["arxiv"]["categories"]
    
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
    
    print(f"  • 抓取到 {len(papers)} 篇論文")
    
    if not papers:
        print("\n⚠️ 沒有找到論文，結束執行")
        return
    
    # 2. 關鍵字篩選
    print("\n🎯 關鍵字篩選...")
    min_score = config["filter"]["min_score"]
    top_n = config["filter"]["top_n"]
    
    top_papers = get_top_papers(
        papers=papers,
        keywords=keywords,
        min_score=min_score,
        top_n=top_n
    )
    
    print(f"  • 篩選後 {len(top_papers)} 篇 (最低分數: {min_score})")
    
    if not top_papers:
        print("\n⚠️ 沒有符合條件的論文，結束執行")
        return
    
    for p in top_papers:
        print(f"    - [{p.score}分] {p.title[:50]}...")
    
    if args.dry_run:
        print("\n🧪 [Dry Run] 模擬模式，跳過 AI 分析和寫入")
        return
    
    # 3. AI 分析
    print("\n🤖 OpenAI GPT 分析...")
    client = OpenAI(api_key=api_key) if api_key else None
    
    results = analyze_papers(
        papers=top_papers,
        client=client,
        model=config["openai"]["model"],
        max_tokens=config["openai"]["max_tokens"],
        verbose=True
    )
    
    # 4. 初始化 Vault 結構
    print("\n📁 初始化 Obsidian Vault...")
    init_vault_structure(vault_path, config["topics"])
    
    # 5. 寫入 Obsidian
    print("\n📝 寫入 Obsidian...")
    
    # 取得腳本目錄作為模板目錄基礎
    script_dir = Path(__file__).parent
    templates_dir = str(script_dir / "templates")
    
    for paper, analysis in results:
        # 寫入論文筆記
        note_path = write_paper_note(
            paper=paper,
            analysis=analysis,
            vault_path=vault_path,
            templates_dir=templates_dir
        )
        print(f"  • 論文筆記: {note_path.name}")
        
        # 更新相關主題頁
        for topic in analysis.related_topics:
            if topic in config["topics"]:
                topic_path = update_topic_page(
                    topic=topic,
                    paper=paper,
                    analysis=analysis,
                    vault_path=vault_path,
                    templates_dir=templates_dir
                )
                print(f"    → 更新主題: {topic}")
    
    # 6. 寫入每日摘要
    print("\n📅 寫入每日摘要...")
    daily_path = write_daily_summary(
        processed_papers=results,
        date=target_date,
        vault_path=vault_path,
        templates_dir=templates_dir
    )
    print(f"  • 每日摘要: {daily_path.name}")
    
    # 完成
    print("\n✅ 完成！")
    print(f"  • 處理論文: {len(results)} 篇")
    print(f"  • Vault 路徑: {vault_path}")


if __name__ == "__main__":
    main()
