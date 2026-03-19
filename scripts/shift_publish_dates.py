#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


ARTICLE_RE = re.compile(r"^(?P<day>\d{4}-\d{2}-\d{2})-(?P<slug>.+)\.md$")
TITLE_RE = re.compile(r"^# (?P<day>\d{4}-\d{2}-\d{2}): (?P<title>.+)$", re.MULTILINE)
@dataclass
class ArticleItem:
    old_date: date
    slug: str

    @property
    def old_stem(self) -> str:
        return f"{self.old_date.isoformat()}-{self.slug}"

    def new_stem(self, new_date: date) -> str:
        return f"{new_date.isoformat()}-{self.slug}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Shift publish dates for articles on or after a date.")
    parser.add_argument("start_date", help="Start publish date in YYYY-MM-DD")
    parser.add_argument("days", type=int, help="Shift day count. Positive values push later.")
    return parser.parse_args()


def load_articles(root: Path) -> list[ArticleItem]:
    items: list[ArticleItem] = []
    for path in sorted((root / "articles").glob("*.md")):
        match = ARTICLE_RE.match(path.name)
        if match:
            items.append(
                ArticleItem(
                    old_date=date.fromisoformat(match.group("day")),
                    slug=match.group("slug"),
                )
            )
    return items


def update_heading(text: str, new_day: date) -> str:
    return TITLE_RE.sub(lambda m: f"# {new_day.isoformat()}: {m.group('title')}", text, count=1)


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    start_day = date.fromisoformat(args.start_date)
    delta = timedelta(days=args.days)

    items = [item for item in load_articles(root) if item.old_date >= start_day]
    if not items:
        print("No articles to shift.")
        return

    mappings: list[tuple[ArticleItem, date]] = [(item, item.old_date + delta) for item in items]

    for item, new_day in sorted(mappings, key=lambda pair: pair[0].old_date, reverse=args.days > 0):
        old_stem = item.old_stem
        new_stem = item.new_stem(new_day)

        old_article = root / "articles" / f"{old_stem}.md"
        new_article = root / "articles" / f"{new_stem}.md"
        old_assets = root / "assets" / old_stem
        new_assets = root / "assets" / new_stem
        old_preview = root / "preview" / f"{old_stem}.html"
        new_preview = root / "preview" / f"{new_stem}.html"

        if old_assets.exists():
            old_assets.rename(new_assets)
        if old_preview.exists():
            old_preview.rename(new_preview)
        if old_article.exists():
            old_article.rename(new_article)

    tracker_path = root / "publishing-tracker.md"
    tracker_text = tracker_path.read_text(encoding="utf-8") if tracker_path.exists() else ""

    for item, new_day in mappings:
        old_stem = item.old_stem
        new_stem = item.new_stem(new_day)
        article_path = root / "articles" / f"{new_stem}.md"

        text = article_path.read_text(encoding="utf-8")
        text = update_heading(text, new_day)
        text = text.replace(old_stem, new_stem)
        article_path.write_text(text, encoding="utf-8")

        if tracker_text:
            pattern = re.compile(
                rf"^\| {re.escape(item.old_date.isoformat())} \|(?P<title>.+?)\| `articles/{re.escape(old_stem)}\.md` \| `preview/{re.escape(old_stem)}\.html` \|(?P<tail>.*)$",
                re.MULTILINE,
            )
            tracker_text = pattern.sub(
                rf"| {new_day.isoformat()} |\g<title>| `articles/{new_stem}.md` | `preview/{new_stem}.html` |\g<tail>",
                tracker_text,
                count=1,
            )

    if tracker_text:
        tracker_path.write_text(tracker_text, encoding="utf-8")

    print(f"Shifted {len(mappings)} article(s) by {args.days} day(s).")


if __name__ == "__main__":
    main()
