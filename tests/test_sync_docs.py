from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import sync_docs  # noqa: E402
from sync_docs import replace_pdf_embeds  # noqa: E402


class SyncDocsTests(unittest.TestCase):
    def test_converts_obsidian_arxiv_embed_to_remote_link(self):
        converted = replace_pdf_embeds(
            "![[2607.01234.pdf]]",
            Path("docs/Papers/example.md"),
            {},
        )
        self.assertEqual(
            converted,
            "[開啟 arXiv PDF](https://arxiv.org/pdf/2607.01234)",
        )

    def test_converts_generated_local_pdf_paths_to_arxiv(self):
        converted = replace_pdf_embeds(
            "[PDF](../PDFs/2607.01234.pdf)\n"
            "![preview](../PDFs/2607.01234.pdf#navpanes=0&toolbar=0)",
            Path("docs/Papers/example.md"),
            {},
        )
        self.assertNotIn("../PDFs/", converted)
        self.assertEqual(converted.count("https://arxiv.org/pdf/2607.01234"), 2)

    def test_generates_research_home_daily_and_filterable_paper_indexes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            (root / "Papers").mkdir()
            (root / "Daily").mkdir()
            (root / "DailyJSON").mkdir()
            (root / "Topics").mkdir()
            (root / "ppt").mkdir()
            (root / "ppt" / "LLM_Evaluation_and_Safety_Guide.pdf").write_bytes(
                b"%PDF-1.4 test guide"
            )
            (root / "Papers" / "[2607.12345] A New Evaluation Benchmark.md").write_text(
                """---
arxiv_id: "2607.12345"
title: "A New Evaluation Benchmark"
date: 2026-07-19
tags:
  - benchmark
  - llm-as-judge
category: "benchmark"
relevance: 5
---
# A New Evaluation Benchmark

## 摘要（中文翻譯）

這是用來驗證首頁與論文卡片的中文摘要。
""",
                encoding="utf-8",
            )
            (root / "Daily" / "2026-07-19.md").write_text(
                "# 2026-07-19 論文摘要\n\n今日分析 **1** 篇 LLM 評測相關論文。\n",
                encoding="utf-8",
            )
            (root / "DailyJSON" / "2026-07-19.json").write_text(
                json.dumps([{
                    "paper": {
                        "arxiv_id": "2607.12345",
                        "title": "A New Evaluation Benchmark",
                        "published": "2026-07-19T00:00:00+00:00",
                        "arxiv_url": "https://arxiv.org/abs/2607.12345",
                        "pdf_url": "https://arxiv.org/pdf/2607.12345",
                    },
                    "analysis": {
                        "category": "benchmark",
                        "relevance": 5,
                        "tags": ["benchmark", "llm-as-judge"],
                        "problem_statement": "這是一個適合快速閱讀的研究重點。",
                        "abstract_zh": "這是完整的中文摘要。",
                        "insights": ["這是一項重要洞察。"],
                    },
                }], ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "Topics" / "benchmark.md").write_text(
                "# benchmark\n", encoding="utf-8"
            )

            with patch.object(sync_docs, "ROOT", root), patch.object(
                sync_docs, "DOCS_DIR", docs
            ):
                sync_docs.main()

            home = (docs / "index.md").read_text(encoding="utf-8")
            papers = (docs / "Papers" / "index.md").read_text(encoding="utf-8")
            daily = (docs / "Daily" / "index.md").read_text(encoding="utf-8")
            daily_detail = (docs / "Daily" / "2026-07-19.md").read_text(encoding="utf-8")

            self.assertIn("LLM 評測知識庫", home)
            self.assertIn("A New Evaluation Benchmark", home)
            self.assertIn("NotebookLM 評測與安全指南", home)
            self.assertIn("assets/guides/LLM_Evaluation_and_Safety_Guide.pdf", home)
            self.assertIn("1</strong><span>篇論文", home)
            self.assertIn('id="paper-search"', papers)
            self.assertIn('data-category="benchmark"', papers)
            self.assertIn("這是用來驗證", papers)
            self.assertIn("2026-07-19", daily)
            self.assertIn("1 篇論文", daily)
            self.assertIn('class="daily-paper-card"', daily_detail)
            self.assertIn("這是一個適合快速閱讀的研究重點", daily_detail)
            self.assertIn("展開完整中文摘要", daily_detail)
            self.assertIn("閱讀完整分析", daily_detail)
            self.assertNotIn("| 分類 | 論文 |", daily_detail)
            self.assertNotIn("[[[", daily_detail)
            self.assertEqual(
                (docs / "assets/guides/LLM_Evaluation_and_Safety_Guide.pdf").read_bytes(),
                b"%PDF-1.4 test guide",
            )


if __name__ == "__main__":
    unittest.main()
