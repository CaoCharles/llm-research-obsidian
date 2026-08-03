from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch


LPDD = Path(__file__).resolve().parents[1] / "lpdd"
sys.path.insert(0, str(LPDD))

import arxiv  # noqa: E402
from fetcher import _fetch_results, fetch_papers_by_date_range  # noqa: E402


class FetchRetryTests(unittest.TestCase):
    @patch("fetcher.time.sleep")
    @patch("fetcher.random.uniform", return_value=0)
    @patch("fetcher.arxiv.Client")
    def test_retries_transient_http_errors(self, client_cls, _random, sleep):
        first = Mock()
        first.results.side_effect = arxiv.HTTPError("https://example.test", 2, 429)
        second = Mock()
        second.results.return_value = iter([])
        client_cls.side_effect = [first, second]

        results = _fetch_results(Mock(), max_attempts=2, base_delay_seconds=5)

        self.assertEqual(results, [])
        self.assertEqual(client_cls.call_count, 2)
        sleep.assert_called_once_with(5)

    @patch("fetcher.arxiv.Client")
    def test_does_not_retry_non_transient_http_errors(self, client_cls):
        client = Mock()
        client.results.side_effect = arxiv.HTTPError("https://example.test", 0, 400)
        client_cls.return_value = client

        with self.assertRaises(arxiv.HTTPError):
            _fetch_results(Mock(), max_attempts=3)

        self.assertEqual(client_cls.call_count, 1)

    @patch.dict(
        "os.environ",
        {"ARXIV_MAX_ATTEMPTS": "2", "ARXIV_RETRY_BASE_SECONDS": "7"},
    )
    @patch("fetcher.time.sleep")
    @patch("fetcher.random.uniform", return_value=0)
    @patch("fetcher.arxiv.Client")
    def test_retry_policy_can_be_configured_from_environment(
        self, client_cls, _random, sleep
    ):
        first = Mock()
        first.results.side_effect = arxiv.HTTPError("https://example.test", 2, 503)
        second = Mock()
        second.results.return_value = iter([])
        client_cls.side_effect = [first, second]

        self.assertEqual(_fetch_results(Mock()), [])
        sleep.assert_called_once_with(7)

    @patch("fetcher._fetch_results")
    def test_date_range_falls_back_to_recent_query_after_throttling(self, fetch):
        fetch.side_effect = [
            arxiv.HTTPError("https://example.test", 3, 429),
            [],
        ]

        papers = fetch_papers_by_date_range(
            categories=["cs.CL", "cs.AI"],
            start_date="2026-07-27",
            end_date="2026-08-02",
            max_results=30,
        )

        self.assertEqual(papers, [])
        self.assertEqual(fetch.call_count, 2)
        primary_search, fallback_search = (
            fetch.call_args_list[0].args[0],
            fetch.call_args_list[1].args[0],
        )
        self.assertIn("submittedDate:", primary_search.query)
        self.assertNotIn("submittedDate:", fallback_search.query)
        self.assertEqual(fallback_search.max_results, 30)


if __name__ == "__main__":
    unittest.main()
