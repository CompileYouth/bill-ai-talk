from __future__ import annotations

import sys
import tempfile
import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_heybill
import wechat_publisher


class HeyBillCoverSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.articles_dir = self.root / "articles"
        self.articles_dir.mkdir(parents=True)
        self.state_dir = self.root / "article-state" / "articles"
        self.state_dir.mkdir(parents=True)

        self.original_root = run_heybill.ROOT
        self.original_articles_dir = run_heybill.ARTICLES_DIR
        self.original_state_dir = run_heybill.ARTICLE_STATE_DIR
        self.original_cover_path = run_heybill.COVER_SELECTIONS_PATH
        self.original_publisher_root = wechat_publisher.ROOT

        run_heybill.ROOT = self.root
        run_heybill.ARTICLES_DIR = self.articles_dir
        run_heybill.ARTICLE_STATE_DIR = self.state_dir
        run_heybill.COVER_SELECTIONS_PATH = self.root / ".publish" / "cover-selections.json"
        wechat_publisher.ROOT = self.root

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
        run_heybill.ARTICLE_STATE_DIR = self.original_state_dir
        run_heybill.COVER_SELECTIONS_PATH = self.original_cover_path
        wechat_publisher.ROOT = self.original_publisher_root
        self.temp_dir.cleanup()

    def test_save_and_load_cover_selection(self) -> None:
        file_name = "2026-04/2026-04-05：测试文章.md"
        selection = run_heybill.save_cover_selection(file_name, text="确定词", background="#123456")
        state_path = run_heybill.article_state_path(file_name)
        state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertTrue(state_path.exists())
        self.assertIsNotNone(selection)
        assert selection is not None
        self.assertEqual(selection["text"], "确定词")
        self.assertEqual(selection["background"], "#123456")
        self.assertIn("confirmed_at", selection)
        self.assertEqual(state["article_file"], file_name)
        self.assertEqual(state["packaging"]["cover"]["text"], "确定词")
        self.assertEqual(state["packaging"]["cover"]["background"], "#123456")

    def test_load_article_payload_includes_confirmed_cover(self) -> None:
        file_name = "2026-04/2026-04-05：测试文章.md"
        run_heybill.save_cover_selection(file_name, text="已确认", background="#abcdef")

        payload = run_heybill.load_article_payload(file_name)

        self.assertEqual(payload["savedCover"]["text"], "已确认")
        self.assertEqual(payload["savedCover"]["background"], "#abcdef")
        self.assertEqual(payload["state"]["article_file"], file_name)
        self.assertEqual(payload["state"]["article"]["title"], "测试文章")
        self.assertEqual(payload["state"]["article"]["tldr"], "这是摘要")
        self.assertTrue(payload["state"]["article"]["core_judgment"])
        self.assertEqual(payload["state"]["strategy"]["article_type"], "short_judgment")
        self.assertTrue(payload["state"]["strategy"]["target_reader"])

    def test_wechat_publisher_prefers_confirmed_cover_state(self) -> None:
        file_name = "2026-04/2026-04-05：测试文章.md"
        run_heybill.save_cover_selection(file_name, text="已确认", background="#abcdef")

        plan = wechat_publisher.load_cover_plan(self.article_file)

        self.assertEqual(plan["text"], "已确认")
        self.assertEqual(plan["background"], "#abcdef")

    def test_update_article_review_keeps_input_minimal(self) -> None:
        file_name = "2026-04/2026-04-05：测试文章.md"

        state = run_heybill.update_article_review(
            file_name,
            metrics={"reads": 123, "likes": 8},
            subjective_note="标题还可以更直接",
        )

        self.assertEqual(state["outcomes"]["reads"], 123)
        self.assertEqual(state["outcomes"]["likes"], 8)
        self.assertEqual(state["review"]["human_note"], "标题还可以更直接")
        self.assertTrue(state["review"]["next_adjustment"])
        self.assertEqual(state["article"]["title"], "测试文章")
        self.assertEqual(state["article"]["tldr"], "这是摘要")
        self.assertTrue(state["strategy"]["article_type"])
        self.assertTrue(state["strategy"]["target_reader"])


if __name__ == "__main__":
    unittest.main()
