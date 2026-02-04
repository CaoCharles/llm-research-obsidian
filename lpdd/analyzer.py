"""
OpenAI GPT 分析模組（詳細版）
"""
import os
import json
import re
import time
from openai import OpenAI
from models import Paper, AnalysisResult


ANALYSIS_PROMPT = """你是 LLM 評測專家。請詳細分析這篇論文：

標題: {title}
摘要: {abstract}
作者: {authors}
分類: {categories}

請用繁體中文回答，**只輸出 JSON，不要加任何其他文字**：
{{
    "abstract_zh": "摘要的完整中文翻譯（保留技術術語英文，約200-300字）",
    
    "problem_statement": "論文解決什麼問題？現有方法有什麼不足？（100-150字）",
    
    "proposed_solution": "作者提出什麼解決方案或框架？核心創新點是什麼？（150-200字）",
    
    "methodology": "技術方法詳細說明：包含模型架構、演算法步驟、資料處理方式、評估指標等（300-400字）",
    
    "key_results": "關鍵實驗結果，使用 Markdown 表格呈現主要數據對比",
    
    "core_contributions": ["核心貢獻1（具體描述）", "核心貢獻2", "核心貢獻3"],
    
    "insights": ["對我們的啟發1（可實際應用的見解）", "啟發2", "啟發3"],
    
    "limitations": "論文的限制、不足或未來工作方向（80-100字）",
    
    "tags": ["tag1", "tag2", "tag3"],
    "relevance": 4,
    "related_topics": ["topic1", "topic2"],
    "category": "最主要的分類標籤"
}}

可用的 tags（請選擇 2-3 個）: 
llm-as-judge, rag-evaluation, red-teaming, prompt-injection, 
faithfulness, hallucination, benchmark, safety, alignment, agent-evaluation

relevance 評分（1-5）：
5=突破性研究, 4=有實用價值, 3=可參考, 2=間接相關, 1=相關性低

重要：直接輸出 JSON 物件，開頭必須是 {{ ，結尾必須是 }}。"""


def extract_json(text: str) -> dict:
    """從回應文字中提取 JSON（強化版）"""
    text = text.strip()
    
    # 1. 直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 2. 移除 markdown 標記
    cleaned = re.sub(r'^```json?\s*', '', text)
    cleaned = re.sub(r'\s*```\s*$', '', cleaned)
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # 3. 括號配對提取
    brace_count = 0
    start_idx = None
    for i, char in enumerate(text):
        if char == '{':
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx is not None:
                json_str = text[start_idx:i+1]
                json_str = fix_json_string(json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
                start_idx = None
    
    # 4. 正規表達式
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        json_str = fix_json_string(json_match.group())
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"無法解析 JSON: {text[:300]}...")


def fix_json_string(json_str: str) -> str:
    """修復常見 JSON 格式問題"""
    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    return json_str


def analyze_paper(
    paper: Paper,
    client: OpenAI,
    model: str = "gpt-5-mini",
    max_tokens: int = 3500,
    max_retries: int = 2
) -> AnalysisResult:
    """使用 OpenAI GPT 分析論文（含重試機制）"""
    prompt = ANALYSIS_PROMPT.format(
        title=paper.title,
        abstract=paper.abstract,
        authors=", ".join(paper.authors[:5]),
        categories=", ".join(paper.categories),
    )
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                max_completion_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.choices[0].message.content
            data = extract_json(response_text)
            
            # 驗證並補充必要欄位
            if "abstract_zh" not in data or not data["abstract_zh"]:
                data["abstract_zh"] = paper.abstract[:500]
            if "problem_statement" not in data:
                data["problem_statement"] = ""
            if "proposed_solution" not in data:
                data["proposed_solution"] = ""
            if "tags" not in data or not data["tags"]:
                data["tags"] = ["benchmark"]
            if "category" not in data or not data["category"]:
                data["category"] = data["tags"][0] if data["tags"] else "benchmark"
            
            return AnalysisResult.from_dict(data)
            
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(f"    ⚠️ 第 {attempt + 1} 次解析失敗，重試中...")
                time.sleep(1)
            continue
    
    print(f"    ❌ 分析失敗（已重試 {max_retries} 次）: {last_error}")
    
    return AnalysisResult(
        abstract_zh=paper.abstract[:800],
        problem_statement="（請手動補充）",
        proposed_solution="（請手動補充）",
        core_contributions=["（請手動補充核心貢獻）"],
        methodology="（請手動補充方法）",
        key_results="（請手動補充結果）",
        insights=["（請手動補充啟發）"],
        limitations="（請手動補充限制）",
        tags=guess_tags_from_abstract(paper.abstract),
        relevance=3,
        related_topics=["benchmark"],
        category="benchmark",
    )


def guess_tags_from_abstract(abstract: str) -> list[str]:
    """從摘要中猜測標籤"""
    abstract_lower = abstract.lower()
    tags = []
    
    tag_keywords = {
        "llm-as-judge": ["judge", "evaluator", "evaluation model"],
        "rag-evaluation": ["rag", "retrieval", "retrieval-augmented"],
        "red-teaming": ["red team", "adversarial", "attack"],
        "prompt-injection": ["prompt injection", "jailbreak"],
        "faithfulness": ["faithful", "faithfulness", "grounding"],
        "hallucination": ["hallucination", "factual"],
        "benchmark": ["benchmark", "evaluation", "dataset"],
        "safety": ["safety", "safe", "harm"],
        "alignment": ["alignment", "align"],
        "agent-evaluation": ["agent", "multi-agent", "agentic"],
    }
    
    for tag, keywords in tag_keywords.items():
        for kw in keywords:
            if kw in abstract_lower:
                tags.append(tag)
                break
    
    return tags[:3] if tags else ["benchmark"]


def analyze_papers(
    papers: list[Paper],
    client: OpenAI,
    model: str = "gpt-5-mini",
    max_tokens: int = 3500,
    verbose: bool = True
) -> list[tuple[Paper, AnalysisResult]]:
    """批次分析多篇論文"""
    results = []
    
    for i, paper in enumerate(papers, 1):
        if verbose:
            print(f"[{i}/{len(papers)}] 分析中: {paper.title[:50]}...")
        
        analysis = analyze_paper(paper, client, model, max_tokens)
        results.append((paper, analysis))
        
        if verbose:
            print(f"  → 相關度: {analysis.relevance}, 標籤: {', '.join(analysis.tags)}")
    
    return results


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("請設定 OPENAI_API_KEY 環境變數")
        exit(1)
    
    client = OpenAI(api_key=api_key)
    
    from datetime import datetime, timezone
    test_paper = Paper(
        arxiv_id="2502.00123",
        title="Test Paper",
        abstract="Test abstract",
        authors=["Alice"],
        categories=["cs.CL"],
        published=datetime.now(timezone.utc),
        pdf_url="https://arxiv.org/pdf/2502.00123",
    )
    
    result = analyze_paper(test_paper, client)
    print(f"分析結果: {result.abstract_zh[:100]}...")
