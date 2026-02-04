"""
arXiv 論文抓取模組
"""
import arxiv
from datetime import datetime, timedelta, timezone
from models import Paper


def fetch_papers(
    categories: list[str],
    hours: int = 24,
    max_results: int = 200
) -> list[Paper]:
    """
    從 arXiv 抓取指定分類的最新論文
    
    Args:
        categories: 論文分類列表，如 ["cs.CL", "cs.AI", "cs.CR"]
        hours: 回溯時數，預設 24 小時
        max_results: 最大結果數量
    
    Returns:
        論文列表
    """
    # 建立查詢條件
    category_query = " OR ".join([f"cat:{cat}" for cat in categories])
    
    # 計算時間範圍
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # 建立 arXiv 搜尋
    search = arxiv.Search(
        query=category_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    
    papers = []
    client = arxiv.Client()
    
    for result in client.results(search):
        # 確保 published 是 timezone-aware
        published = result.published
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
            
        # 過濾時間範圍內的論文
        if published < cutoff_time:
            continue
        
        # 從 arXiv URL 提取 ID
        arxiv_id = result.entry_id.split("/")[-1]
        # 移除版本號 (如 v1, v2)
        if "v" in arxiv_id:
            arxiv_id = arxiv_id.rsplit("v", 1)[0]
        
        paper = Paper(
            arxiv_id=arxiv_id,
            title=result.title.replace("\n", " "),
            abstract=result.summary.replace("\n", " "),
            authors=[author.name for author in result.authors],
            categories=[cat for cat in result.categories],
            published=published,
            pdf_url=result.pdf_url,
        )
        papers.append(paper)
    
    return papers


def fetch_papers_by_date(
    categories: list[str],
    date: str,
    max_results: int = 200
) -> list[Paper]:
    """
    抓取特定日期的論文
    
    Args:
        categories: 論文分類列表
        date: 日期字串，格式 YYYY-MM-DD
        max_results: 最大結果數量
    
    Returns:
        論文列表
    """
    target_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    next_date = target_date + timedelta(days=1)
    
    # 建立查詢條件
    category_query = " OR ".join([f"cat:{cat}" for cat in categories])
    
    search = arxiv.Search(
        query=category_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    
    papers = []
    client = arxiv.Client()
    
    for result in client.results(search):
        published = result.published
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        
        # 只取指定日期的論文
        if published < target_date or published >= next_date:
            continue
        
        arxiv_id = result.entry_id.split("/")[-1]
        if "v" in arxiv_id:
            arxiv_id = arxiv_id.rsplit("v", 1)[0]
        
        paper = Paper(
            arxiv_id=arxiv_id,
            title=result.title.replace("\n", " "),
            abstract=result.summary.replace("\n", " "),
            authors=[author.name for author in result.authors],
            categories=[cat for cat in result.categories],
            published=published,
            pdf_url=result.pdf_url,
        )
        papers.append(paper)
    
    return papers


def fetch_paper_by_id(arxiv_id: str) -> Paper | None:
    """
    根據 arXiv ID 抓取單篇論文

    Args:
        arxiv_id: arXiv 論文 ID（如 "2502.00123"）

    Returns:
        Paper 物件，若找不到則返回 None
    """
    # 移除可能的版本號
    clean_id = arxiv_id
    if "v" in clean_id:
        clean_id = clean_id.rsplit("v", 1)[0]

    search = arxiv.Search(id_list=[clean_id])
    client = arxiv.Client()

    try:
        results = list(client.results(search))
        if not results:
            return None

        result = results[0]
        published = result.published
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)

        # 從 arXiv URL 提取 ID
        result_id = result.entry_id.split("/")[-1]
        if "v" in result_id:
            result_id = result_id.rsplit("v", 1)[0]

        return Paper(
            arxiv_id=result_id,
            title=result.title.replace("\n", " "),
            abstract=result.summary.replace("\n", " "),
            authors=[author.name for author in result.authors],
            categories=[cat for cat in result.categories],
            published=published,
            pdf_url=result.pdf_url,
        )
    except Exception:
        return None


if __name__ == "__main__":
    # 測試抓取
    papers = fetch_papers(
        categories=["cs.CL", "cs.AI"],
        hours=24,
        max_results=10
    )
    print(f"抓取到 {len(papers)} 篇論文")
    for p in papers[:3]:
        print(f"- {p.arxiv_id}: {p.title[:60]}...")
