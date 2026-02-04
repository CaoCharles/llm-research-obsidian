"""
關鍵字篩選模組
"""
import re
import yaml
from pathlib import Path
from models import Paper


def load_keywords(keywords_path: str = "keywords.yaml") -> dict[str, int]:
    """
    載入關鍵字權重配置
    
    Returns:
        關鍵字到權重的映射 dict
    """
    path = Path(keywords_path)
    if not path.exists():
        # 使用預設關鍵字
        return {
            "llm-as-judge": 5,
            "red team": 5,
            "jailbreak": 5,
            "prompt injection": 5,
            "faithfulness": 4,
            "hallucination": 4,
            "benchmark": 4,
            "rag": 3,
            "evaluation": 3,
            "retrieval-augmented": 3,
            "accuracy": 2,
            "consistency": 2,
        }
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    # 展平巢狀結構
    keywords = {}
    for category, items in data.items():
        if isinstance(items, dict):
            keywords.update(items)
    
    return keywords


def calculate_score(paper: Paper, keywords: dict[str, int]) -> int:
    """
    計算論文的關鍵字匹配分數
    
    Args:
        paper: 論文物件
        keywords: 關鍵字權重 dict
    
    Returns:
        匹配分數
    """
    text = f"{paper.title} {paper.abstract}".lower()
    score = 0
    
    for keyword, weight in keywords.items():
        # 使用正規表達式進行全字匹配
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, text):
            score += weight
    
    return score


def filter_papers(
    papers: list[Paper],
    keywords: dict[str, int],
    min_score: int = 5
) -> list[Paper]:
    """
    依關鍵字權重篩選論文
    
    Args:
        papers: 論文列表
        keywords: 關鍵字權重 dict
        min_score: 最低分數門檻
    
    Returns:
        篩選並排序後的論文列表（分數由高到低）
    """
    scored_papers = []
    
    for paper in papers:
        score = calculate_score(paper, keywords)
        if score >= min_score:
            paper.score = score
            scored_papers.append(paper)
    
    # 依分數排序
    scored_papers.sort(key=lambda p: p.score, reverse=True)
    
    return scored_papers


def get_top_papers(
    papers: list[Paper],
    keywords: dict[str, int],
    min_score: int = 5,
    top_n: int = 5
) -> list[Paper]:
    """
    取得分數最高的 Top N 論文

    Args:
        papers: 論文列表
        keywords: 關鍵字權重 dict
        min_score: 最低分數門檻
        top_n: 取前 N 篇

    Returns:
        Top N 論文列表
    """
    filtered = filter_papers(papers, keywords, min_score)
    return filtered[:top_n]


def search_by_keyword(
    papers: list[Paper],
    keyword: str,
    min_matches: int = 1
) -> list[Paper]:
    """
    搜尋包含特定關鍵字的論文

    Args:
        papers: 論文列表
        keyword: 搜尋關鍵字
        min_matches: 最少匹配次數（預設 1）

    Returns:
        包含關鍵字的論文列表
    """
    keyword_lower = keyword.lower()
    matched = []

    for paper in papers:
        text = f"{paper.title} {paper.abstract}".lower()
        # 使用正規表達式進行匹配
        pattern = r"\b" + re.escape(keyword_lower) + r"\b"
        matches = re.findall(pattern, text)

        if len(matches) >= min_matches:
            # 使用匹配數作為分數
            paper.score = len(matches)
            matched.append(paper)

    # 依匹配數排序
    matched.sort(key=lambda p: p.score, reverse=True)
    return matched


if __name__ == "__main__":
    # 測試篩選
    from fetcher import fetch_papers
    
    keywords = load_keywords()
    print(f"載入 {len(keywords)} 個關鍵字")
    
    papers = fetch_papers(
        categories=["cs.CL", "cs.AI"],
        hours=48,
        max_results=50
    )
    print(f"抓取到 {len(papers)} 篇論文")
    
    filtered = filter_papers(papers, keywords, min_score=3)
    print(f"篩選後 {len(filtered)} 篇")
    
    for p in filtered[:5]:
        print(f"- [{p.score}分] {p.title[:50]}...")
