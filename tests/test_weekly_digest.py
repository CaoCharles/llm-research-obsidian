import json
from datetime import date
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_weekly_digest import build_weekly_digest  # noqa: E402


def record(arxiv_id: str, title: str, relevance: int, category: str) -> dict:
    return {
        "paper": {
            "arxiv_id": arxiv_id,
            "title": title,
            "published": "2026-07-18",
        },
        "analysis": {
            "relevance": relevance,
            "category": category,
            "insights": [f"{title} insight"],
        },
    }


class WeeklyDigestTests(unittest.TestCase):
    def test_builds_weekly_digest_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "DailyJSON"
            output_dir = root / "Weekly"
            input_dir.mkdir()
            (input_dir / "2026-07-18.json").write_text(
                json.dumps(
                    [
                        record("2607.00001", "Paper A", 3, "RAG"),
                        record("2607.00002", "Paper B", 5, "Safety"),
                    ]
                ),
                encoding="utf-8",
            )
            (input_dir / "2026-07-19.json").write_text(
                json.dumps([record("2607.00001", "Paper A", 4, "RAG")]),
                encoding="utf-8",
            )

            output = build_weekly_digest(
                input_dir, output_dir, date(2026, 7, 19)
            )
            text = output.read_text(encoding="utf-8")

            self.assertEqual(output.name, "2026-W29.md")
            self.assertIn("paper_count: 2", text)
            self.assertEqual(text.count("https://arxiv.org/abs/2607.00001"), 2)
            self.assertLess(text.index("Paper B"), text.index("Paper A"))

    def test_builds_an_empty_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = build_weekly_digest(
                root / "DailyJSON", root / "Weekly", date(2026, 7, 19)
            )
            text = output.read_text(encoding="utf-8")

            self.assertIn("paper_count: 0", text)
            self.assertIn("本期尚無可用論文摘要", text)

    def test_can_skip_an_empty_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = build_weekly_digest(
                root / "DailyJSON",
                root / "Weekly",
                date(2026, 7, 19),
                skip_empty=True,
            )

            self.assertIsNone(output)
            self.assertFalse((root / "Weekly").exists())


if __name__ == "__main__":
    unittest.main()
