"""
OpenAI GPT 分析模組（詳細版）
"""
import os
import json
import re
import time
from openai import OpenAI
from typing import Optional
from models import Paper, AnalysisResult
from paper_text import extract_pdf_text


ALLOWED_TAGS = [
    "llm-as-judge", "rag-evaluation", "red-teaming", "prompt-injection",
    "faithfulness", "hallucination", "benchmark", "safety", "alignment",
    "agent-evaluation",
]

ANALYSIS_JSON_SCHEMA = {
    "name": "paper_analysis",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "abstract_zh": {"type": "string"},
            "problem_statement": {"type": "string"},
            "proposed_solution": {"type": "string"},
            "methodology": {"type": "string"},
            "key_results": {"type": "string"},
            "core_contributions": {
                "type": "array", "items": {"type": "string"},
                "minItems": 3, "maxItems": 3,
            },
            "insights": {
                "type": "array", "items": {"type": "string"},
                "minItems": 3, "maxItems": 3,
            },
            "limitations": {"type": "string"},
            "tags": {
                "type": "array",
                "items": {"type": "string", "enum": ALLOWED_TAGS},
                "minItems": 2, "maxItems": 3,
            },
            "relevance": {"type": "integer", "minimum": 1, "maximum": 5},
            "related_topics": {
                "type": "array", "items": {"type": "string"}, "minItems": 1,
            },
            "category": {"type": "string", "enum": ALLOWED_TAGS},
        },
        "required": [
            "abstract_zh", "problem_statement", "proposed_solution",
            "methodology", "key_results", "core_contributions", "insights",
            "limitations", "tags", "relevance", "related_topics", "category",
        ],
    },
}


class AnalysisError(RuntimeError):
    """論文分析無法產生可發布的結果。"""


ANALYSIS_PROMPT = """你是 LLM 評測專家。請根據提供的論文證據詳細分析這篇論文：

標題: {title}
摘要: {abstract}
作者: {authors}
分類: {categories}

分析依據: {source_scope}

論文內容：
{paper_content}

準確性規則：
1. 只能陳述論文內容中可以找到依據的主張、設定與數字。
2. 不得推測未提供的模型架構、資料規模、baseline 或實驗結果。
3. 若論文沒有提供具體數字，key_results 必須明確寫「論文未報告」，不可補造數據。
4. 區分作者的實驗結果、理論主張，以及你提出的實務洞察。

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


def validate_analysis(data: dict, paper: Paper) -> None:
    """拒絕空白、佔位或明顯未翻譯的分析。"""
    required_text = [
        "abstract_zh", "problem_statement", "proposed_solution", "methodology",
        "key_results", "limitations", "category",
    ]
    for field in required_text:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"分析缺少必要欄位: {field}")

    for field in ("core_contributions", "insights"):
        value = data.get(field)
        if not isinstance(value, list) or len(value) < 3 or any(
            not isinstance(item, str) or not item.strip() for item in value
        ):
            raise ValueError(f"分析欄位不完整: {field}")

    serialized = json.dumps(data, ensure_ascii=False)
    if "手動補充" in serialized or "未設定 API Key" in serialized:
        raise ValueError("分析含有不可發布的佔位內容")
    if data["abstract_zh"].strip() == paper.abstract.strip():
        raise ValueError("中文摘要未翻譯")


def analyze_paper(
    paper: Paper,
    client: Optional[OpenAI],
    model: str = "gpt-5.6-luna",
    max_tokens: int = 8000,
    max_retries: int = 2,
    strict: bool = False,
    full_text: str = "",
) -> AnalysisResult:
    """使用 OpenAI GPT 分析論文（含重試機制）"""
    if client is None:
        if strict:
            raise AnalysisError(f"論文 {paper.arxiv_id} 分析失敗: 未設定 API Key")
        return AnalysisResult(
            abstract_zh=paper.abstract[:800],
            problem_statement="（未設定 API Key，請手動補充）",
            proposed_solution="（未設定 API Key，請手動補充）",
            core_contributions=["（未設定 API Key，請手動補充核心貢獻）"],
            methodology="（未設定 API Key，請手動補充方法）",
            key_results="（未設定 API Key，請手動補充結果）",
            insights=["（未設定 API Key，請手動補充啟發）"],
            limitations="（未設定 API Key，請手動補充限制）",
            tags=guess_tags_from_abstract(paper.abstract),
            relevance=3,
            related_topics=["benchmark"],
            category="benchmark",
        )
    paper_content = full_text.strip() or paper.abstract
    source_scope = "完整 PDF 文字" if full_text.strip() else "arXiv 摘要（PDF 取文失敗或未啟用）"
    prompt = ANALYSIS_PROMPT.format(
        title=paper.title,
        abstract=paper.abstract,
        authors=", ".join(paper.authors[:5]),
        categories=", ".join(paper.categories),
        source_scope=source_scope,
        paper_content=paper_content,
    )
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            request = {
                "model": model,
                "max_completion_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": ANALYSIS_JSON_SCHEMA,
                },
            }
            # GPT-5 completion token 上限同時包含推理與可見輸出。
            # 此任務以結構化長文為主，使用 low 避免推理用完預算。
            if model.startswith("gpt-5"):
                request["reasoning_effort"] = "low"

            response = client.chat.completions.create(**request)

            choice = response.choices[0]
            message = choice.message
            if getattr(message, "refusal", None):
                raise ValueError(f"模型拒絕分析: {message.refusal}")
            if choice.finish_reason == "length":
                raise ValueError("模型輸出超過 token 上限")
            response_text = message.content
            if not response_text:
                raise ValueError("模型未回傳分析內容")
            data = extract_json(response_text)
            validate_analysis(data, paper)
            
            return AnalysisResult.from_dict(data)
            
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(f"    ⚠️ 第 {attempt + 1} 次解析失敗，重試中...")
                time.sleep(1)
            continue
    
    print(f"    ❌ 分析失敗（已重試 {max_retries} 次）: {last_error}")

    if strict:
        raise AnalysisError(f"論文 {paper.arxiv_id} 分析失敗: {last_error}") from last_error
    
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
    client: Optional[OpenAI],
    model: str = "gpt-5.6-luna",
    max_tokens: int = 8000,
    verbose: bool = True,
    strict: bool = False,
    use_full_text: bool = True,
) -> list[tuple[Paper, AnalysisResult]]:
    """批次分析多篇論文"""
    results = []
    
    for i, paper in enumerate(papers, 1):
        if verbose:
            print(f"[{i}/{len(papers)}] 分析中: {paper.title[:50]}...")
        
        full_text = ""
        if use_full_text:
            try:
                if verbose:
                    print("  → 擷取完整 PDF 文字...")
                full_text = extract_pdf_text(paper.pdf_url)
                if verbose:
                    print(f"  → 已取得 {len(full_text):,} 字元論文內容")
            except Exception as exc:
                if verbose:
                    print(f"  ⚠️ PDF 取文失敗，改用 arXiv 摘要: {exc}")

        analysis = analyze_paper(
            paper,
            client,
            model,
            max_tokens,
            strict=strict,
            full_text=full_text,
        )
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
