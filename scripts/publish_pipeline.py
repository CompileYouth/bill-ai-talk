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


def _shift_if_needed(publish_date: str) -> None:
    if any(path.name.startswith(f"{publish_date}：") for path in ARTICLES_DIR.glob("*.md")):
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

    new_row = f"| {publish_date} | {title} | `articles/{article_path.name}` |  |  |  |  |  |  |"
    rows = [row for row in rows if f"`articles/{article_path.name}`" not in row]
    rows.append(new_row)
    rows.sort(key=lambda row: TRACKER_ROW_RE.match(row).group("date") if TRACKER_ROW_RE.match(row) else "9999-99-99")
    TRACKER_PATH.write_text("\n".join(header + rows) + "\n", encoding="utf-8")


def schedule_article(article_file: str, publish_date: str) -> Path:
    old_path = ARTICLES_DIR / article_file
    match = PENDING_RE.match(old_path.name)
    if not old_path.exists() or not match:
        raise FileNotFoundError(f"Unscheduled article not found: {article_file}")

    title = match.group("title")
    _shift_if_needed(publish_date)
    new_path = ARTICLES_DIR / f"{publish_date}：{title}.md"
    old_path.rename(new_path)
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
