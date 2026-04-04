#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import publish_pipeline
import wechat_publisher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assign a publish date to an unscheduled article and optionally publish it.")
    parser.add_argument("article_file", help="Unscheduled markdown filename under articles/")
    parser.add_argument("--date", required=True, help="Publish date in YYYY-MM-DD")
    parser.add_argument("--publish", action="store_true", help="Also prepare/fill the article in WeChat backend")
    return parser.parse_args()


def main() -> None:
    article_path = publish_pipeline.schedule_article(args.article_file, args.date)
    if args.publish:
        bundle = wechat_publisher.publish_article(article_path, args.date)
        print(bundle)
    else:
        print(article_path)


if __name__ == "__main__":
    args = parse_args()
    main()
