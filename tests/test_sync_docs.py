from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

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


if __name__ == "__main__":
    unittest.main()
