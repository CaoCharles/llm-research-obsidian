"""
arXiv 論文抓取模組
"""
import random
import time
from datetime import datetime, timedelta, timezone

import arxiv

from models import Paper


RETRYABLE_HTTP_STATUSES = {429, 500, 502, 503, 504}


def _fetch_results(
    search: arxiv.Search,
    *,
    max_attempts: int = 4,
    base_delay_seconds: float = 5.0,
) -> list:
    """Fetch one arXiv query with bounded exponential backoff.

    GitHub-hosted runners share outbound IP addresses and can receive transient
    429/5xx responses from arXiv. The library retries individual page requests;
    this outer retry restarts the complete query after a longer cool-down.
    """
    for attempt in range(max_attempts):
        try:
            client = arxiv.Client(
                page_size=50,
                delay_seconds=4.0,
                num_retries=2,
            )
            return list(client.results(search))
        except arxiv.HTTPError as exc:
            if exc.status not in RETRYABLE_HTTP_STATUSES or attempt + 1 >= max_attempts:
                raise
            delay = min(60.0, base_delay_seconds * (2**attempt))
            delay += random.uniform(0, min(3.0, delay * 0.2))
            print(
                f"arXiv 回應 HTTP {exc.status}，{delay:.1f} 秒後重試 "
                f"({attempt + 2}/{max_attempts})..."
            )
            time.sleep(delay)

    return []


def _paper_from_result(result) -> Paper:
    published = result.published
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    arxiv_id = result.entry_id.split("/")[-1]
    if "v" in arxiv_id:
        arxiv_id = arxiv_id.rsplit("v", 1)[0]

    return Paper(
        arxiv_id=arxiv_id,
        title=result.title.replace("\n", " "),
        abstract=result.summary.replace("\n", " "),
        authors=[author.name for author in result.authors],
        categories=list(result.categories),
        published=published,
        pdf_url=result.pdf_url,
    )


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
    for result in _fetch_results(search):
        published = result.published
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        # 過濾時間範圍內的論文
        if published < cutoff_time:
            continue
        papers.append(_paper_from_result(result))
    
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
        date: 日期字串，格式 YYYY-MM-DD（以本機時區的「當日」為準）
        max_results: 最大結果數量
    
    Returns:
        論文列表
    """
    return fetch_papers_by_date_range(
        categories=categories,
        start_date=date,
        end_date=date,
        max_results=max_results,
    )


def fetch_papers_by_date_range(
    categories: list[str],
    start_date: str,
    end_date: str,
    max_results: int = 200,
) -> list[Paper]:
    """Fetch a local-calendar date range with one arXiv search query."""
    local_tz = datetime.now().astimezone().tzinfo or timezone.utc
    start_local = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=local_tz)
    end_local_exclusive = (
        datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=local_tz)
        + timedelta(days=1)
    )
    start_utc = start_local.astimezone(timezone.utc)
    end_utc_exclusive = end_local_exclusive.astimezone(timezone.utc)

    category_query = " OR ".join(f"cat:{category}" for category in categories)
    # arXiv's submittedDate query uses minute precision and an inclusive upper
    # bound, so subtract one minute from our exclusive end timestamp.
    query_end = end_utc_exclusive - timedelta(minutes=1)
    submitted_range = (
        f"submittedDate:[{start_utc:%Y%m%d%H%M} TO {query_end:%Y%m%d%H%M}]"
    )
    search = arxiv.Search(
        query=f"({category_query}) AND {submitted_range}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    papers_by_id: dict[str, Paper] = {}
    for result in _fetch_results(search):
        paper = _paper_from_result(result)
        if start_utc <= paper.published < end_utc_exclusive:
            papers_by_id.setdefault(paper.arxiv_id, paper)
    return list(papers_by_id.values())


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
        results = _fetch_results(search)
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
