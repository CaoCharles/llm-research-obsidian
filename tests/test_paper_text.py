from unittest.mock import Mock, patch
import unittest

from lpdd.paper_text import extract_pdf_text


class FakePage:
    def __init__(self, text: str):
        self.text = text

    def extract_text(self):
        return self.text


class PaperTextTests(unittest.TestCase):
    @patch("lpdd.paper_text.PdfReader")
    @patch("lpdd.paper_text.requests.get")
    def test_extracts_numbered_pdf_pages(self, get: Mock, reader: Mock):
        response = Mock(content=b"%PDF test")
        response.raise_for_status.return_value = None
        get.return_value = response
        reader.return_value.pages = [FakePage("Introduction"), FakePage("Results")]

        text = extract_pdf_text("https://arxiv.org/pdf/2607.00001")

        self.assertIn("Page 1", text)
        self.assertIn("Introduction", text)
        self.assertIn("Page 2", text)
        self.assertIn("Results", text)

    @patch("lpdd.paper_text.PdfReader")
    @patch("lpdd.paper_text.requests.get")
    def test_preserves_start_and_conclusion_when_truncated(self, get: Mock, reader: Mock):
        response = Mock(content=b"%PDF test")
        response.raise_for_status.return_value = None
        get.return_value = response
        reader.return_value.pages = [FakePage("A" * 120), FakePage("CONCLUSION")]

        text = extract_pdf_text("https://arxiv.org/pdf/2607.00001", max_chars=80)

        self.assertIn("A", text)
        self.assertIn("CONCLUSION", text)
        self.assertIn("因長度限制省略", text)


if __name__ == "__main__":
    unittest.main()
