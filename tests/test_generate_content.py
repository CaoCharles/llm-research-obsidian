import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / ".agent/skills/chatbot-setup/assets/generate_content.py"
SPEC = importlib.util.spec_from_file_location("generate_content_hook", HOOK_PATH)
HOOK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(HOOK)


class GenerateContentTests(unittest.TestCase):
    def test_converts_wiki_link_without_display_text(self):
        converted = HOOK._fix_wiki_links(
            "See [[Topics/benchmark]]",
            "https://example.test/repo",
        )

        self.assertEqual(
            converted,
            "See [Topics/benchmark](https://example.test/repo/Topics/benchmark/)",
        )

    def test_converts_wiki_link_with_display_text(self):
        converted = HOOK._fix_wiki_links(
            "See [[Topics/benchmark|Benchmark]]",
            "https://example.test/repo",
        )

        self.assertEqual(
            converted,
            "See [Benchmark](https://example.test/repo/Topics/benchmark/)",
        )


if __name__ == "__main__":
    unittest.main()
