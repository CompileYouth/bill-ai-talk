#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "articles"
TRACKER_PATH = ROOT / "publishing-tracker.md"

SCHEDULED_RE = re.compile(r"^(?P<day>\d{4}-\d{2}-\d{2})：(?P<title>.+)\.md$")
PENDING_RE = re.compile(r"^未排期：(?P<title>.+)\.md$")
TRACKER_ROW_RE = re.compile(
    r"^\| (?P<date>\d{4}-\d{2}-\d{2}) \| (?P<title>.+?) \| `(?P<article>articles/.+?\.md)` \| (?P<metrics>.+) \|$"
)
ASSET_PATH_RE = re.compile(r"(?P<prefix>\.\./assets/|\.\./\.\./assets/)(?P<stem>[^/]+)/")
DATE_PREFIX_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?P<rest>.*)$")
PENDING_ASSET_PREFIX_RE = re.compile(r"^未排期(?P<rest>.*)$")


def _shift_if_needed(publish_date: str) -> None:
    if any(path.name.startswith(f"{publish_date}：") for path in ARTICLES_DIR.rglob("*.md")):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "shift_publish_dates.py"), publish_date, "1"],
            cwd=ROOT,
            check=True,
        )


def _insert_tracker_row(publish_date: str, title: str, article_path: Path) -> None:
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

    rel_path = article_path.relative_to(ROOT).as_posix()
    new_row = f"| {publish_date} | {title} | `{rel_path}` |  |  |  |  |  |  |"
    rows = [row for row in rows if f"`{rel_path}`" not in row]
    rows.append(new_row)
    rows.sort(key=lambda row: TRACKER_ROW_RE.match(row).group("date") if TRACKER_ROW_RE.match(row) else "9999-99-99")
    TRACKER_PATH.write_text("\n".join(header + rows) + "\n", encoding="utf-8")


def schedule_article(article_file: str, publish_date: str) -> Path:
    old_path = ARTICLES_DIR / article_file
    match = PENDING_RE.match(old_path.name)
    if not old_path.exists() or not match:
        raise FileNotFoundError(f"Unscheduled article not found: {article_file}")

    title = match.group("title")
    original_text = old_path.read_text(encoding="utf-8")
    _shift_if_needed(publish_date)
    month_dir = ARTICLES_DIR / publish_date[:7]
    month_dir.mkdir(parents=True, exist_ok=True)
    new_path = month_dir / f"{publish_date}：{title}.md"

    asset_stems = list(dict.fromkeys(ASSET_PATH_RE.findall(original_text)))
    updated_text = original_text.replace("../assets/", "../../assets/")

    if asset_stems:
        old_asset_stem = asset_stems[0][1]
        date_match = DATE_PREFIX_RE.match(old_asset_stem)
        pending_match = PENDING_ASSET_PREFIX_RE.match(old_asset_stem)
        if date_match:
            new_asset_stem = f"{publish_date}{date_match.group('rest')}"
            old_asset_dir = ROOT / "assets" / old_asset_stem
            new_asset_dir = ROOT / "assets" / new_asset_stem
            if old_asset_dir.exists() and old_asset_dir != new_asset_dir:
                old_asset_dir.rename(new_asset_dir)
            updated_text = updated_text.replace(old_asset_stem, new_asset_stem)
        elif pending_match:
            new_asset_stem = f"{publish_date}{pending_match.group('rest')}"
            old_asset_dir = ROOT / "assets" / old_asset_stem
            new_asset_dir = ROOT / "assets" / new_asset_stem
            if old_asset_dir.exists() and old_asset_dir != new_asset_dir:
                old_asset_dir.rename(new_asset_dir)
            updated_text = updated_text.replace(old_asset_stem, new_asset_stem)

    new_path.write_text(updated_text, encoding="utf-8")
    old_path.unlink()
    _insert_tracker_row(publish_date, title, new_path)
    return new_path


def list_unscheduled() -> list[Path]:
    return sorted([path for path in ARTICLES_DIR.glob("未排期：*.md") if path.is_file()], reverse=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assign a publish date to an unscheduled article.")
    parser.add_argument("article_file", help="Unscheduled article filename under articles/")
    parser.add_argument("--date", required=True, help="Publish date in YYYY-MM-DD")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    article_path = schedule_article(args.article_file, args.date)
    print(article_path)


if __name__ == "__main__":
    main()
