from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch


LPDD = Path(__file__).resolve().parents[1] / "lpdd"
sys.path.insert(0, str(LPDD))

import arxiv  # noqa: E402
from fetcher import _fetch_results  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
