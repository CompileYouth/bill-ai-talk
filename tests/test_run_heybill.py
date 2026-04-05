from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_heybill


class HeyBillCoverSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.articles_dir = self.root / "articles"
        self.articles_dir.mkdir(parents=True)
        self.publish_dir = self.root / ".publish"
        self.publish_dir.mkdir(parents=True)

        self.original_root = run_heybill.ROOT
        self.original_articles_dir = run_heybill.ARTICLES_DIR
        self.original_cover_path = run_heybill.COVER_SELECTIONS_PATH

        run_heybill.ROOT = self.root
        run_heybill.ARTICLES_DIR = self.articles_dir
        run_heybill.COVER_SELECTIONS_PATH = self.publish_dir / "cover-selections.json"

        article_dir = self.articles_dir / "2026-04"
        article_dir.mkdir(parents=True)
        self.article_file = article_dir / "2026-04-05：测试文章.md"
        self.article_file.write_text(
            "# 测试文章\n\n> TL;DR\n> 这是摘要\n\n正文。",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        run_heybill.ROOT = self.original_root
        run_heybill.ARTICLES_DIR = self.original_articles_dir
        run_heybill.COVER_SELECTIONS_PATH = self.original_cover_path
        self.temp_dir.cleanup()

    def test_save_and_load_cover_selection(self) -> None:
        file_name = "2026-04/2026-04-05：测试文章.md"
        run_heybill.save_cover_selection(file_name, text="确定词", background="#123456")

        selection = run_heybill.load_cover_selection(file_name)

        self.assertIsNotNone(selection)
        assert selection is not None
        self.assertEqual(selection["text"], "确定词")
        self.assertEqual(selection["background"], "#123456")
        self.assertIn("confirmed_at", selection)

    def test_load_article_payload_includes_confirmed_cover(self) -> None:
        file_name = "2026-04/2026-04-05：测试文章.md"
        run_heybill.save_cover_selection(file_name, text="已确认", background="#abcdef")

        payload = run_heybill.load_article_payload(file_name)

        self.assertEqual(payload["savedCover"]["text"], "已确认")
        self.assertEqual(payload["savedCover"]["background"], "#abcdef")


if __name__ == "__main__":
    unittest.main()
