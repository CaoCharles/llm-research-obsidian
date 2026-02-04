"""
資料模型定義
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Paper:
    """arXiv 論文資料結構"""
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str]
    categories: list[str]
    published: datetime
    pdf_url: str
    score: int = 0
    pdf_path: Optional[str] = None
    
    @property
    def year(self) -> str:
        return self.published.strftime("%Y")
    
    @property
    def month(self) -> str:
        return self.published.strftime("%m")
    
    @property
    def arxiv_url(self) -> str:
        return f"https://arxiv.org/abs/{self.arxiv_id}"
    
    @property
    def safe_title(self) -> str:
        """取得安全的檔名用標題"""
        safe = self.title.replace("/", "-").replace("\\", "-")
        safe = safe.replace(":", " -").replace("?", "").replace("*", "")
        safe = safe.replace('"', "'").replace("<", "").replace(">", "")
        safe = safe.replace("|", "-")
        if len(safe) > 80:
            safe = safe[:80] + "..."
        return safe


@dataclass
class AnalysisResult:
    """AI 分析結果（詳細版）"""
    abstract_zh: str              # 摘要中文翻譯
    problem_statement: str        # 解決什麼問題
    proposed_solution: str        # 提出的解決方案
    core_contributions: list[str] # 核心貢獻
    methodology: str              # 技術方法詳述
    key_results: str              # 關鍵結果
    insights: list[str]           # 啟發
    limitations: str              # 限制
    tags: list[str]               # 標籤
    relevance: int                # 相關度
    related_topics: list[str]     # 相關主題
    category: str                 # 主分類
    
    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisResult":
        """從 dict 建立"""
        return cls(
            abstract_zh=data.get("abstract_zh", ""),
            problem_statement=data.get("problem_statement", ""),
            proposed_solution=data.get("proposed_solution", ""),
            core_contributions=data.get("core_contributions", []),
            methodology=data.get("methodology", ""),
            key_results=data.get("key_results", ""),
            insights=data.get("insights", []),
            limitations=data.get("limitations", ""),
            tags=data.get("tags", []),
            relevance=data.get("relevance", 3),
            related_topics=data.get("related_topics", []),
            category=data.get("category", data.get("tags", ["benchmark"])[0] if data.get("tags") else "benchmark"),
        )


@dataclass
class ProcessedPaper:
    """處理完成的論文"""
    paper: Paper
    analysis: AnalysisResult
