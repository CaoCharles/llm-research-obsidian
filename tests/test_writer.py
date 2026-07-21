from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from lpdd.models import AnalysisResult, Paper
from lpdd.writer import safe_topic_name, update_topic_page, write_paper_note


class WriterTests(unittest.TestCase):
    def test_ai_generated_topic_is_safe_filename_component(self):
        self.assertEqual(safe_topic_name("5G/6G AI-native networks"), "5G-6G AI-native networks")

    def test_topic_with_slash_is_written_as_one_file(self):
        paper = Paper(
            arxiv_id="2607.00002", title="Network Agents", abstract="Abstract",
            authors=["Author"], categories=["cs.AI"],
            published=datetime(2026, 7, 20, tzinfo=timezone.utc),
            pdf_url="https://arxiv.org/pdf/2607.00002",
        )
        analysis = AnalysisResult(
            abstract_zh="摘要", problem_statement="問題", proposed_solution="方案",
            core_contributions=["一"], methodology="方法", key_results="結果",
            insights=["一"], limitations="限制", tags=["agent-evaluation"],
            relevance=4, related_topics=["5G/6G AI-native networks"], category="Agent",
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = update_topic_page(
                "5G/6G AI-native networks", paper, analysis, Path(tmp),
                templates_dir=str(Path(__file__).parents[1] / "lpdd" / "templates"),
            )
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "5G-6G AI-native networks.md")

    def test_remote_pdf_preview_is_rendered_without_local_download(self):
        paper = Paper(
            arxiv_id="2607.00001",
            title="Evaluation Paper",
            abstract="Abstract",
            authors=["Author"],
            categories=["cs.CL"],
            published=datetime(2026, 7, 19, tzinfo=timezone.utc),
            pdf_url="https://arxiv.org/pdf/2607.00001",
        )
        analysis = AnalysisResult(
            abstract_zh="摘要", problem_statement="問題", proposed_solution="方案",
            core_contributions=["一", "二", "三"], methodology="方法",
            key_results="結果", insights=["一", "二", "三"], limitations="限制",
            tags=["benchmark"], relevance=4, related_topics=["Benchmark"],
            category="Benchmark",
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = write_paper_note(
                paper,
                analysis,
                Path(tmp),
                templates_dir=str(Path(__file__).parents[1] / "lpdd" / "templates"),
                download_pdfs=False,
                verbose=False,
            )
            content = path.read_text(encoding="utf-8")

        self.assertIn("## 論文預覽", content)
        self.assertIn("https://arxiv.org/pdf/2607.00001#navpanes", content)
        self.assertIn('class="paper-pdf-embed"', content)
        self.assertNotIn("本地 PDF", content)


if __name__ == "__main__":
    unittest.main()
