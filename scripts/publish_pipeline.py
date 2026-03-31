#!/usr/bin/env python3

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_wechat_page as wechat


ROOT = SCRIPT_DIR.parent
CANDIDATES_DIR = ROOT / "candidates"
ARTICLES_DIR = ROOT / "articles"
ASSETS_DIR = ROOT / "assets"
PREVIEW_DIR = ROOT / "preview"
TRACKER_PATH = ROOT / "publishing-tracker.md"

CANDIDATE_RE = re.compile(r"^(?P<id>\d{8}-\d{6})：(?P<title>.+)\.md$")
ARTICLE_RE = re.compile(r"^(?P<day>\d{4}-\d{2}-\d{2})：(?P<title>.+)\.md$")
TRACKER_ROW_RE = re.compile(
    r"^\| (?P<date>\d{4}-\d{2}-\d{2}) \| (?P<title>.+?) \| `(?P<article>articles/.+?\.md)` \| `(?P<preview>preview/.+?\.html)` \| (?P<metrics>.+) \|$"
)


@dataclass
class CandidateItem:
    candidate_id: str
    title: str
    markdown_path: Path

    @property
    def asset_dir(self) -> Path:
        return ASSETS_DIR / "candidates" / self.candidate_id

    @property
    def preview_path(self) -> Path:
        return PREVIEW_DIR / "candidates" / f"{self.candidate_id}.html"


def ensure_candidate_dirs() -> None:
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "candidates").mkdir(parents=True, exist_ok=True)
    (PREVIEW_DIR / "candidates").mkdir(parents=True, exist_ok=True)


def list_candidates() -> list[CandidateItem]:
    ensure_candidate_dirs()
    items: list[CandidateItem] = []
    for path in sorted(CANDIDATES_DIR.glob("*.md"), reverse=True):
        match = CANDIDATE_RE.match(path.name)
        if not match:
            continue
        items.append(
            CandidateItem(
                candidate_id=match.group("id"),
                title=match.group("title"),
                markdown_path=path,
            )
        )
    return items


def candidate_by_name(file_name: str) -> CandidateItem:
    path = CANDIDATES_DIR / file_name
    match = CANDIDATE_RE.match(path.name)
    if not path.exists() or not match:
        raise FileNotFoundError(f"Candidate not found: {file_name}")
    return CandidateItem(
        candidate_id=match.group("id"),
        title=match.group("title"),
        markdown_path=path,
    )


def build_preview(markdown_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    blocks = wechat.markdown_to_blocks(markdown_path)
    title = markdown_path.stem.split("：", 1)[1] if "：" in markdown_path.stem else markdown_path.stem
    html = wechat.build_html(blocks, title)
    output_path.write_text(html, encoding="utf-8")


def _insert_tracker_row(publish_date: str, title: str, article_path: Path, preview_path: Path) -> None:
    if not TRACKER_PATH.exists():
        raise FileNotFoundError("publishing-tracker.md not found")

    lines = TRACKER_PATH.read_text(encoding="utf-8").splitlines()
    header: list[str] = []
    rows: list[str] = []
    seen_table = False
    for line in lines:
        if line.startswith("| "):
            seen_table = True
            if TRACKER_ROW_RE.match(line):
                rows.append(line)
            else:
                header.append(line)
        else:
            if not seen_table or not rows:
                header.append(line)
            else:
                # No extra content currently expected after table.
                pass

    new_row = (
        f"| {publish_date} | {title} | "
        f"`articles/{article_path.name}` | `preview/{preview_path.name}` |  |  |  |  |  |  |"
    )
    rows = [row for row in rows if f"`articles/{article_path.name}`" not in row]
    rows.append(new_row)

    def row_date(row: str) -> str:
        match = TRACKER_ROW_RE.match(row)
        return match.group("date") if match else "9999-99-99"

    rows.sort(key=row_date)
    TRACKER_PATH.write_text("\n".join(header + rows) + "\n", encoding="utf-8")


def _shift_if_needed(publish_date: str) -> None:
    target_article = ARTICLES_DIR / f"{publish_date}："
    if any(path.name.startswith(target_article.name) for path in ARTICLES_DIR.glob("*.md")):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "shift_publish_dates.py"), publish_date, "1"],
            cwd=ROOT,
            check=True,
        )


def promote_candidate(candidate_file: str, publish_date: str) -> tuple[Path, Path]:
    item = candidate_by_name(candidate_file)
    _shift_if_needed(publish_date)

    article_name = f"{publish_date}：{item.title}.md"
    article_path = ARTICLES_DIR / article_name
    asset_stem = f"{publish_date}-{item.candidate_id}"
    asset_dir = ASSETS_DIR / asset_stem
    preview_path = PREVIEW_DIR / f"{publish_date}：{item.title}.html"

    text = item.markdown_path.read_text(encoding="utf-8")
    old_asset_prefix = f"../assets/candidates/{item.candidate_id}/"
    new_asset_prefix = f"../assets/{asset_stem}/"
    text = text.replace(old_asset_prefix, new_asset_prefix)
    article_path.write_text(text, encoding="utf-8")

    if item.asset_dir.exists():
        if asset_dir.exists():
            shutil.rmtree(asset_dir)
        asset_dir.parent.mkdir(parents=True, exist_ok=True)
        item.asset_dir.rename(asset_dir)

    build_preview(article_path, preview_path)
    _insert_tracker_row(publish_date, item.title, article_path, preview_path)

    if item.preview_path.exists():
        item.preview_path.unlink()
    item.markdown_path.unlink()

    return article_path, preview_path
