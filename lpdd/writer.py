"""
Obsidian 寫入模組（含 PDF 下載）
"""
import json
import os
import requests
from pathlib import Path
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from models import Paper, AnalysisResult, ProcessedPaper


def get_template_env(templates_dir: str = "templates") -> Environment:
    """取得 Jinja2 模板環境"""
    return Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def ensure_dir(path: Path) -> None:
    """確保目錄存在"""
    path.mkdir(parents=True, exist_ok=True)


def download_pdf(paper: Paper, vault_path: Path, verbose: bool = True) -> str | None:
    """
    下載論文 PDF 到 Obsidian Vault
    
    Args:
        paper: 論文物件
        vault_path: Vault 路徑
    
    Returns:
        PDF 檔名（相對於 Vault），失敗則返回 None
    """
    pdf_dir = vault_path / "PDFs"
    ensure_dir(pdf_dir)
    
    pdf_filename = f"{paper.arxiv_id}.pdf"
    pdf_path = pdf_dir / pdf_filename
    
    # 如果已存在則跳過下載
    if pdf_path.exists():
        if verbose:
            print(f"    📄 PDF 已存在: {pdf_filename}")
        return f"PDFs/{pdf_filename}"
    
    try:
        if verbose:
            print(f"    📥 下載 PDF: {paper.pdf_url}")
        
        response = requests.get(paper.pdf_url, timeout=60)
        response.raise_for_status()
        
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        
        if verbose:
            print(f"    ✅ 已儲存: {pdf_filename}")
        
        return f"PDFs/{pdf_filename}"
    
    except Exception as e:
        if verbose:
            print(f"    ⚠️ PDF 下載失敗: {e}")
        return None


def write_paper_note(
    paper: Paper,
    analysis: AnalysisResult,
    vault_path: Path,
    templates_dir: str = "templates",
    download_pdfs: bool = True,
    verbose: bool = True
) -> Path:
    """
    寫入論文筆記到 Obsidian
    
    Args:
        paper: 論文物件
        analysis: 分析結果
        vault_path: Obsidian Vault 路徑
        templates_dir: 模板目錄
        download_pdfs: 是否下載 PDF
        verbose: 是否顯示進度
    
    Returns:
        寫入的檔案路徑
    """
    env = get_template_env(templates_dir)
    template = env.get_template("paper.md")
    
    # 下載 PDF
    pdf_path = None
    pdf_filename = None
    if download_pdfs:
        pdf_path = download_pdf(paper, vault_path, verbose)
        if pdf_path:
            pdf_filename = pdf_path.split("/")[-1]
    
    # 準備模板資料
    data = {
        "arxiv_id": paper.arxiv_id,
        "title": paper.title,
        "safe_title": paper.safe_title,
        "date": paper.published.strftime("%Y-%m-%d"),
        "authors": paper.authors,
        "institution": "",
        "tags": analysis.tags,
        "category": analysis.category,
        "relevance": analysis.relevance,
        "arxiv_url": paper.arxiv_url,
        "pdf_url": paper.pdf_url,
        "abstract_zh": analysis.abstract_zh,
        "problem_statement": analysis.problem_statement,
        "proposed_solution": analysis.proposed_solution,
        "core_contributions": analysis.core_contributions,
        "methodology": analysis.methodology,
        "key_results": analysis.key_results,
        "insights": analysis.insights,
        "limitations": analysis.limitations,
        "related_topics": analysis.related_topics,
        "pdf_embed": pdf_path is not None,
        "pdf_filename": pdf_filename,
    }
    
    # 渲染模板
    content = template.render(**data)
    
    # 建立輸出路徑（使用論文標題作為檔名）
    output_dir = vault_path / "Papers"
    ensure_dir(output_dir)
    
    # 檔名格式: "[arXiv ID] 標題.md"
    safe_filename = f"[{paper.arxiv_id}] {paper.safe_title}.md"
    output_path = output_dir / safe_filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def load_topic_descriptions(topics_config_path: str = "topic_descriptions.yaml") -> dict:
    """載入主題說明配置"""
    path = Path(topics_config_path)
    if not path.exists():
        # 嘗試相對於此檔案的路徑
        path = Path(__file__).parent / topics_config_path
    
    if path.exists():
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def update_topic_page(
    topic: str,
    paper: Paper,
    analysis: AnalysisResult,
    vault_path: Path,
    templates_dir: str = "templates"
) -> Path:
    """
    更新主題頁面，加入新論文連結（含標題和分類）
    
    Args:
        topic: 主題名稱
        paper: 論文物件
        analysis: 分析結果
        vault_path: Obsidian Vault 路徑
        templates_dir: 模板目錄
    
    Returns:
        更新的檔案路徑
    """
    topics_dir = vault_path / "Topics"
    ensure_dir(topics_dir)
    
    topic_file = topics_dir / f"{topic}.md"
    
    # 新論文連結（含分類標籤和標題）
    date_str = paper.published.strftime("%Y-%m-%d")
    short_title = paper.title[:50] + "..." if len(paper.title) > 50 else paper.title
    # 使用標題作為連結（匹配新的檔名格式）
    link_name = f"[{paper.arxiv_id}] {paper.safe_title}"
    new_entry = f"- `[{analysis.category}]` [[{link_name}|{short_title}]] ({date_str})"
    
    if topic_file.exists():
        # 讀取現有內容
        with open(topic_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 檢查是否已存在
        if paper.arxiv_id in content:
            return topic_file
        
        # 在 "## 相關論文" 區塊後插入
        if "## 相關論文" in content:
            parts = content.split("## 相關論文")
            if len(parts) == 2:
                header = parts[0] + "## 相關論文\n"
                rest = parts[1]
                if rest.startswith("\n"):
                    rest = "\n" + new_entry + rest
                else:
                    rest = "\n" + new_entry + "\n" + rest
                content = header + rest
            else:
                content += f"\n{new_entry}"
        else:
            content += f"\n\n## 相關論文\n{new_entry}"
    else:
        # 建立新主題頁，使用主題說明配置
        topic_descriptions = load_topic_descriptions()
        topic_info = topic_descriptions.get(topic, {})
        
        env = get_template_env(templates_dir)
        template = env.get_template("topic.md")
        
        # 預設值
        default_title = topic.replace("-", " ").title()
        default_desc = f"{default_title} 相關研究的彙整頁面。"
        default_importance = "此領域持續有新的研究進展。"
        default_criteria = [
            f"標題或摘要含有 {topic} 相關關鍵字",
            "研究主題與此分類高度相關",
        ]
        default_directions = [
            {"name": "待補充", "desc": "歡迎補充研究方向"},
        ]
        default_related = ["benchmark"]
        
        content = template.render(
            title=topic_info.get("title", default_title),
            description=topic_info.get("description", default_desc),
            importance=topic_info.get("importance", default_importance),
            inclusion_criteria=topic_info.get("inclusion_criteria", default_criteria),
            research_directions=topic_info.get("research_directions", default_directions),
            related_topics=topic_info.get("related_topics", default_related),
            first_paper_entry=new_entry,
        )
    
    with open(topic_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    return topic_file


def write_daily_summary(
    processed_papers: list[tuple[Paper, AnalysisResult]],
    date: str,
    vault_path: Path,
    templates_dir: str = "templates"
) -> Path:
    """
    寫入每日摘要（含論文標題和分類標籤）
    
    Args:
        processed_papers: (論文, 分析結果) 的列表
        date: 日期字串 (YYYY-MM-DD)
        vault_path: Obsidian Vault 路徑
        templates_dir: 模板目錄
    
    Returns:
        寫入的檔案路徑
    """
    daily_dir = vault_path / "Daily"
    ensure_dir(daily_dir)
    
    env = get_template_env(templates_dir)
    template = env.get_template("daily.md")
    
    # 準備論文列表資料
    papers_data = []
    for paper, analysis in processed_papers:
        stars = "⭐" * analysis.relevance
        short_title = paper.title[:40] + "..." if len(paper.title) > 40 else paper.title
        # 使用標題作為連結（匹配新的檔名格式）
        link_name = f"[{paper.arxiv_id}] {paper.safe_title}"
        papers_data.append({
            "arxiv_id": paper.arxiv_id,
            "link_name": link_name,
            "title": short_title,
            "full_title": paper.title,
            "category": analysis.category,
            "topic": ", ".join(analysis.tags[:2]) if analysis.tags else "未分類",
            "relevance_stars": stars,
            "abstract_zh": analysis.abstract_zh,
        })
    
    # 找出重點發現
    highlights = []
    for paper, analysis in processed_papers[:3]:
        if analysis.insights:
            highlights.append(analysis.insights[0])
    
    content = template.render(
        date=date,
        paper_count=len(processed_papers),
        papers=papers_data,
        highlights=highlights,
    )
    
    output_path = daily_dir / f"{date}.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def init_vault_structure(vault_path: Path, topics: list[str]) -> None:
    """
    初始化 Obsidian Vault 目錄結構

    Args:
        vault_path: Vault 路徑
        topics: 主題列表
    """
    # 建立基本目錄
    (vault_path / "Papers").mkdir(parents=True, exist_ok=True)
    (vault_path / "Topics").mkdir(parents=True, exist_ok=True)
    (vault_path / "Daily").mkdir(parents=True, exist_ok=True)
    (vault_path / "PDFs").mkdir(parents=True, exist_ok=True)
    (vault_path / "templates").mkdir(parents=True, exist_ok=True)

    print(f"已初始化 Vault 結構: {vault_path}")


def write_from_json(
    json_path: str,
    vault_path: Path,
    templates_dir: str,
    download_pdfs: bool = True,
    verbose: bool = True
) -> Path:
    """
    從 JSON 檔案讀取分析結果並寫入 Obsidian

    JSON 格式需包含:
    - paper: 論文資訊 (arxiv_id, title, abstract, authors, categories, published, pdf_url)
    - analysis: 分析結果 (abstract_zh, problem_statement, proposed_solution, ...)

    Args:
        json_path: JSON 檔案路徑
        vault_path: Obsidian Vault 路徑
        templates_dir: 模板目錄
        download_pdfs: 是否下載 PDF
        verbose: 是否顯示進度

    Returns:
        寫入的檔案路徑
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 重建 Paper 物件
    paper_data = data["paper"]
    published = paper_data.get("published")
    if isinstance(published, str):
        published = datetime.fromisoformat(published)
    elif published is None:
        published = datetime.now(timezone.utc)

    paper = Paper(
        arxiv_id=paper_data["arxiv_id"],
        title=paper_data["title"],
        abstract=paper_data.get("abstract", ""),
        authors=paper_data.get("authors", []),
        categories=paper_data.get("categories", []),
        published=published,
        pdf_url=paper_data.get("pdf_url", f"https://arxiv.org/pdf/{paper_data['arxiv_id']}"),
    )

    # 重建 AnalysisResult 物件
    analysis = AnalysisResult.from_dict(data["analysis"])

    # 初始化 Vault 目錄
    ensure_dir(vault_path / "Papers")
    ensure_dir(vault_path / "Topics")
    ensure_dir(vault_path / "PDFs")

    # 寫入論文筆記
    note_path = write_paper_note(
        paper=paper,
        analysis=analysis,
        vault_path=vault_path,
        templates_dir=templates_dir,
        download_pdfs=download_pdfs,
        verbose=verbose
    )

    # 更新相關主題頁
    for topic in analysis.related_topics:
        update_topic_page(
            topic=topic,
            paper=paper,
            analysis=analysis,
            vault_path=vault_path,
            templates_dir=templates_dir
        )

    return note_path


def write_daily_from_json(
    json_path: str,
    date: str,
    vault_path: Path,
    templates_dir: str
) -> Path:
    """
    從 JSON 檔案讀取多篇論文分析結果並寫入每日摘要

    JSON 格式需為陣列，每個元素包含:
    - paper: 論文資訊
    - analysis: 分析結果

    Args:
        json_path: JSON 檔案路徑
        date: 日期字串 (YYYY-MM-DD)
        vault_path: Obsidian Vault 路徑
        templates_dir: 模板目錄

    Returns:
        寫入的檔案路徑
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 支援單一物件或陣列
    if isinstance(data, dict):
        items = [data]
    else:
        items = data

    processed_papers = []

    for item in items:
        paper_data = item["paper"]
        published = paper_data.get("published")
        if isinstance(published, str):
            published = datetime.fromisoformat(published)
        elif published is None:
            published = datetime.now(timezone.utc)

        paper = Paper(
            arxiv_id=paper_data["arxiv_id"],
            title=paper_data["title"],
            abstract=paper_data.get("abstract", ""),
            authors=paper_data.get("authors", []),
            categories=paper_data.get("categories", []),
            published=published,
            pdf_url=paper_data.get("pdf_url", f"https://arxiv.org/pdf/{paper_data['arxiv_id']}"),
        )

        analysis = AnalysisResult.from_dict(item["analysis"])
        processed_papers.append((paper, analysis))

    # 初始化 Vault 目錄
    ensure_dir(vault_path / "Daily")

    # 寫入每日摘要
    return write_daily_summary(
        processed_papers=processed_papers,
        date=date,
        vault_path=vault_path,
        templates_dir=templates_dir
    )


if __name__ == "__main__":
    from datetime import timezone
    
    # 測試寫入
    vault = Path("./test_vault")
    init_vault_structure(vault, ["llm-as-judge", "benchmark"])
    
    # 建立測試資料
    paper = Paper(
        arxiv_id="2502.00123",
        title="Small Models as LLM Judges: A Cost-Effective Alternative",
        abstract="Test abstract",
        authors=["Alice Chen", "Bob Smith"],
        categories=["cs.CL"],
        published=datetime.now(timezone.utc),
        pdf_url="https://arxiv.org/pdf/2502.00123",
    )
    
    analysis = AnalysisResult(
        abstract_zh="我們提出使用微調後的小模型作為大型語言模型評估任務的替代方案。我們的方法達到 GPT-4 評審能力的 95%，同時降低 90% 的成本。",
        core_contributions=["證明小模型經微調可達 GPT-4 評審能力的 95%"],
        methodology="使用 GPT-4 生成評審數據，對 Llama-2-7B 進行 SFT",
        key_results="| 模型 | 人類一致性 |\n|------|-----------|",
        insights=["評估導入小模型評審的可行性"],
        limitations="僅在英語資料集上測試",
        tags=["llm-as-judge", "benchmark"],
        relevance=5,
        related_topics=["llm-as-judge"],
        category="llm-as-judge",
    )
    
    print("測試需要 templates/ 目錄中的模板檔案")
