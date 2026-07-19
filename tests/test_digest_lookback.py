from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


LPDD = Path(__file__).resolve().parents[1] / "lpdd"
sys.path.insert(0, str(LPDD))

from cli import _fetch_digest_candidates  # noqa: E402
from models import Paper  # noqa: E402


def paper(arxiv_id: str) -> Paper:
    return Paper(
        arxiv_id=arxiv_id,
        title=f"Paper {arxiv_id}",
        abstract="evaluation benchmark",
        authors=["Author"],
        categories=["cs.CL"],
        published=datetime(2026, 7, 17, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
    )


class DigestLookbackTests(unittest.TestCase):
    def test_looks_back_across_empty_weekend_and_deduplicates(self):
        by_date = {
            "2026-07-19": [],
            "2026-07-18": [],
            "2026-07-17": [paper("2607.00001"), paper("2607.00002")],
            "2026-07-16": [paper("2607.00002"), paper("2607.00003")],
        }

        with patch("cli.fetch_papers_by_date", side_effect=lambda date, **_: by_date[date]):
            papers, source_dates = _fetch_digest_candidates(
                categories=["cs.CL"],
                date="2026-07-19",
                lookback_days=4,
                max_results=200,
            )

        self.assertEqual(
            [item.arxiv_id for item in papers],
            ["2607.00001", "2607.00002", "2607.00003"],
        )
        self.assertEqual(source_dates, ["2026-07-17", "2026-07-16"])

    def test_always_fetches_target_date_at_least_once(self):
        with patch("cli.fetch_papers_by_date", return_value=[]) as fetch:
            papers, source_dates = _fetch_digest_candidates(
                categories=["cs.AI"],
                date="2026-07-19",
                lookback_days=0,
                max_results=50,
            )

        self.assertEqual(papers, [])
        self.assertEqual(source_dates, [])
        fetch.assert_called_once_with(
            categories=["cs.AI"], date="2026-07-19", max_results=50
        )


if __name__ == "__main__":
    unittest.main()
