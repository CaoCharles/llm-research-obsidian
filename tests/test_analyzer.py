from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import json
import sys
import unittest


LPDD = Path(__file__).resolve().parents[1] / "lpdd"
sys.path.insert(0, str(LPDD))

from analyzer import AnalysisError, analyze_paper, extract_json  # noqa: E402
from models import Paper  # noqa: E402


def sample_paper() -> Paper:
    return Paper(
        arxiv_id="2607.00001",
        title="Evaluation Paper",
        abstract="We introduce a reproducible benchmark for evaluating language models.",
        authors=["Author"],
        categories=["cs.CL"],
        published=datetime(2026, 7, 19, tzinfo=timezone.utc),
        pdf_url="https://arxiv.org/pdf/2607.00001",
    )


def valid_analysis() -> dict:
    return {
        "abstract_zh": "我們提出一個可重現的語言模型評測基準。",
        "problem_statement": "現有評測缺少一致且可重現的比較方式。",
        "proposed_solution": "作者提出標準化資料集與評分流程。",
        "methodology": "方法包含資料清理、多模型推理、統一指標計算與可重現的實驗設定。",
        "key_results": "| 方法 | 分數 |\n|---|---:|\n| Proposed | 90 |",
        "core_contributions": ["建立新基準", "公開評測流程", "提供實驗分析"],
        "insights": ["應固定資料版本", "應記錄推理參數", "應比較多種指標"],
        "limitations": "資料集的語言與領域範圍仍有限。",
        "tags": ["benchmark", "llm-as-judge"],
        "relevance": 4,
        "related_topics": ["evaluation"],
        "category": "benchmark",
    }


class FakeCompletions:
    def __init__(self, content: str, finish_reason: str = "stop"):
        self.content = content
        self.finish_reason = finish_reason
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        message = SimpleNamespace(content=self.content, refusal=None)
        choice = SimpleNamespace(message=message, finish_reason=self.finish_reason)
        return SimpleNamespace(choices=[choice])


class FakeClient:
    def __init__(self, completions: FakeCompletions):
        self.chat = SimpleNamespace(completions=completions)


class AnalyzerTests(unittest.TestCase):
    def test_extracts_fenced_json(self):
        self.assertEqual(extract_json('```json\n{"ok": true}\n```'), {"ok": True})

    def test_uses_luna_structured_output_and_validates_result(self):
        completions = FakeCompletions(json.dumps(valid_analysis(), ensure_ascii=False))
        result = analyze_paper(sample_paper(), FakeClient(completions), strict=True)

        self.assertEqual(result.category, "benchmark")
        request = completions.requests[0]
        self.assertEqual(request["model"], "gpt-5.6-luna")
        self.assertEqual(request["response_format"]["type"], "json_schema")
        self.assertTrue(request["response_format"]["json_schema"]["strict"])
        self.assertEqual(request["reasoning_effort"], "low")
        self.assertIn("arXiv 摘要", request["messages"][0]["content"])

    def test_includes_full_pdf_text_when_available(self):
        completions = FakeCompletions(json.dumps(valid_analysis(), ensure_ascii=False))
        analyze_paper(
            sample_paper(),
            FakeClient(completions),
            strict=True,
            full_text="Methods: We evaluate three baselines and report exact results.",
        )

        prompt = completions.requests[0]["messages"][0]["content"]
        self.assertIn("完整 PDF 文字", prompt)
        self.assertIn("We evaluate three baselines", prompt)
        self.assertIn("不得推測", prompt)

    def test_strict_mode_raises_instead_of_publishing_placeholder(self):
        completions = FakeCompletions('{"abstract_zh": "未完成"', finish_reason="length")

        with self.assertRaises(AnalysisError):
            analyze_paper(
                sample_paper(), FakeClient(completions), max_retries=0, strict=True
            )

    def test_strict_mode_requires_a_client(self):
        with self.assertRaises(AnalysisError):
            analyze_paper(sample_paper(), None, strict=True)


if __name__ == "__main__":
    unittest.main()
