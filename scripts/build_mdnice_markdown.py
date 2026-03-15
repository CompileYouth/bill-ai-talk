#!/opt/homebrew/bin/python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


JSDELIVR_TEMPLATE = "https://cdn.jsdelivr.net/gh/{repo}@{ref}/{path}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an mdnice-ready Markdown file with GitHub CDN image URLs."
    )
    parser.add_argument("source", help="Source markdown file path")
    parser.add_argument(
        "--repo",
        default="CompileYouth/bill-ai-talk",
        help="GitHub repo in owner/name format",
    )
    parser.add_argument(
        "--ref",
        default="main",
        help="Git ref to use in CDN URLs, usually main",
    )
    parser.add_argument(
        "--output",
        help="Output markdown path. Defaults to publishing/<source>-mdnice.md",
    )
    return parser.parse_args()


def rewrite_image_paths(content: str, source_path: Path, repo: str, ref: str) -> str:
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    def replace(match: re.Match[str]) -> str:
        alt = match.group(1)
        raw_path = match.group(2).strip()
        if raw_path.startswith(("http://", "https://")):
            return match.group(0)
        if raw_path.startswith("/"):
            return match.group(0)

        resolved = (source_path.parent / raw_path).resolve()
        repo_root = Path.cwd().resolve()
        rel_path = resolved.relative_to(repo_root).as_posix()
        url = JSDELIVR_TEMPLATE.format(repo=repo, ref=ref, path=rel_path)
        return f"![{alt}]({url})"

    return pattern.sub(replace, content)


def main() -> int:
    args = parse_args()
    source = Path(args.source).resolve()
    if args.output:
        output = Path(args.output).resolve()
    else:
        output = Path.cwd().resolve() / "publishing" / f"{source.stem}-mdnice{source.suffix}"

    content = source.read_text(encoding="utf-8")
    rewritten = rewrite_image_paths(content, source, args.repo, args.ref)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rewritten, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
