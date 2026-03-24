#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import re
from pathlib import Path


IMAGE_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
LINK_RE = re.compile(r"\[(.+?)\]\((.+?)\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a clean HTML preview page with a copy button for WeChat pasting."
    )
    parser.add_argument("markdown_file", help="Markdown article file under articles/")
    parser.add_argument(
        "--output",
        help="Optional output HTML path. Defaults to preview/<article-name>.html",
    )
    return parser.parse_args()


def escape(text: str) -> str:
    return html.escape(text, quote=False)


def inline_markup(text: str) -> str:
    tokens: list[tuple[str, str]] = []

    def store_link(match: re.Match[str]) -> str:
        tokens.append((match.group(1), match.group(2)))
        return f"@@LINK{len(tokens) - 1}@@"

    escaped = escape(LINK_RE.sub(store_link, text))
    escaped = BOLD_RE.sub(r"<strong>\1</strong>", escaped)

    for idx, (label, href) in enumerate(tokens):
        escaped = escaped.replace(
            f"@@LINK{idx}@@",
            f'<a class="article-link" href="{html.escape(href, quote=True)}">{escape(label)}</a>',
        )
    return escaped


def image_to_data_uri(markdown_file: Path, image_path: str) -> str:
    resolved = (markdown_file.parent / image_path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    mime_type, _ = mimetypes.guess_type(resolved.name)
    if mime_type is None:
        mime_type = "application/octet-stream"

    encoded = base64.b64encode(resolved.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def flush_paragraph(paragraph_lines: list[str], blocks: list[str]) -> None:
    if not paragraph_lines:
        return
    text = " ".join(line.strip() for line in paragraph_lines).strip()
    if text:
        blocks.append(f'<p class="article-paragraph">{inline_markup(text)}</p>')
    paragraph_lines.clear()


def markdown_to_blocks(markdown_file: Path) -> list[str]:
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    quote_lines: list[str] = []
    in_list = False
    list_items: list[str] = []

    lines = markdown_file.read_text(encoding="utf-8").splitlines()

    def flush_quote() -> None:
        nonlocal quote_lines
        if not quote_lines:
            return
        rendered = []
        for line in quote_lines:
            content = line[1:].lstrip()
            if content:
                rendered.append(f"<p>{inline_markup(content)}</p>")
            else:
                rendered.append("<p>&nbsp;</p>")
        blocks.append(f'<blockquote class="article-quote">{"".join(rendered)}</blockquote>')
        quote_lines = []

    def flush_list() -> None:
        nonlocal list_items, in_list
        if not list_items:
            return
        items_html = "".join(
            f'<li class="article-list-item">{inline_markup(item)}</li>' for item in list_items
        )
        blocks.append(f'<ul class="article-list">{items_html}</ul>')
        list_items = []
        in_list = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph(paragraph_lines, blocks)
            flush_quote()
            flush_list()
            continue

        if stripped.startswith(">"):
            flush_paragraph(paragraph_lines, blocks)
            flush_list()
            quote_lines.append(stripped)
            continue

        if stripped.startswith("# "):
            flush_paragraph(paragraph_lines, blocks)
            flush_quote()
            flush_list()
            blocks.append(f'<h1 class="article-title">{inline_markup(stripped[2:].strip())}</h1>')
            continue

        if stripped.startswith("## "):
            flush_paragraph(paragraph_lines, blocks)
            flush_quote()
            flush_list()
            blocks.append(f'<h2 class="article-heading">{inline_markup(stripped[3:].strip())}</h2>')
            continue

        if stripped.startswith("### "):
            flush_paragraph(paragraph_lines, blocks)
            flush_quote()
            flush_list()
            blocks.append(f'<h3 class="article-subheading">{inline_markup(stripped[4:].strip())}</h3>')
            continue

        image_match = IMAGE_RE.fullmatch(stripped)
        if image_match:
            flush_paragraph(paragraph_lines, blocks)
            flush_quote()
            flush_list()
            alt_text, image_path = image_match.groups()
            data_uri = image_to_data_uri(markdown_file, image_path)
            blocks.append(
                (
                    '<figure class="article-figure">'
                    f'<img class="article-image" src="{data_uri}" alt="{html.escape(alt_text, quote=True)}" />'
                    "</figure>"
                )
            )
            continue

        if stripped.startswith("- "):
            flush_paragraph(paragraph_lines, blocks)
            flush_quote()
            in_list = True
            list_items.append(stripped[2:].strip())
            continue

        if in_list:
            flush_list()

        paragraph_lines.append(stripped)

    flush_paragraph(paragraph_lines, blocks)
    flush_quote()
    flush_list()
    return blocks


def build_html(blocks: list[str], title: str) -> str:
    content = "\n        ".join(blocks)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title, quote=True)}</title>
  <style>
    :root {{
      --bg: #f7f3ea;
      --paper: #fffdf7;
      --ink: #181818;
      --muted: #616161;
      --line: #1f1f1f;
      --accent: #d94f2b;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(217, 79, 43, 0.10), transparent 28%),
        linear-gradient(180deg, #f8f3e8 0%, #f4efe3 100%);
      color: var(--ink);
      min-height: 100vh;
    }}

    .shell {{
      width: min(920px, calc(100vw - 32px));
      margin: 40px auto;
    }}

    .toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
      padding: 16px 18px;
      border: 2px solid rgba(31, 31, 31, 0.18);
      border-radius: 18px;
      background: rgba(255, 253, 247, 0.85);
      backdrop-filter: blur(10px);
    }}

    .toolbar-copy {{
      appearance: none;
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      background: var(--ink);
      color: #fff;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
    }}

    .toolbar-copy:hover {{
      background: #000;
    }}

    .toolbar-meta {{
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }}

    .article {{
      padding: 44px 40px 52px;
      background: var(--paper);
      border: 4px solid var(--line);
      border-radius: 28px;
      box-shadow: 0 20px 60px rgba(38, 28, 10, 0.08);
    }}

    .article-title {{
      margin: 0 0 18px;
      font-size: 34px;
      line-height: 1.3;
      letter-spacing: -0.02em;
    }}

    .article-heading {{
      margin: 30px 0 10px;
      font-size: 24px;
      line-height: 1.4;
    }}

    .article-subheading {{
      margin: 26px 0 10px;
      font-size: 20px;
      line-height: 1.45;
    }}

    .article-paragraph {{
      margin: 0 0 20px;
      font-size: 18px;
      line-height: 1.95;
      color: var(--ink);
    }}

    .article strong {{
      font-weight: 800;
      color: var(--ink);
    }}

    .article-quote {{
      margin: 0 0 24px;
      padding: 18px 20px;
      background: #f5efe2;
      border-left: 6px solid var(--accent);
      border-radius: 16px;
    }}

    .article-quote p {{
      margin: 0;
      font-size: 16px;
      line-height: 1.85;
      color: #403b35;
    }}

    .article-quote p + p {{
      margin-top: 8px;
    }}

    .article-figure {{
      margin: 28px 0;
    }}

    .article-image {{
      display: block;
      width: 100%;
      height: auto;
      border-radius: 18px;
    }}

    .article-list {{
      margin: 0 0 20px;
      padding-left: 24px;
    }}

    .article-list-item {{
      font-size: 18px;
      line-height: 1.9;
      margin-bottom: 8px;
    }}

    @media (max-width: 700px) {{
      .shell {{
        width: min(100vw - 20px, 920px);
        margin: 18px auto 28px;
      }}

      .toolbar {{
        flex-direction: column;
        align-items: stretch;
      }}

      .article {{
        padding: 28px 22px 36px;
        border-width: 3px;
        border-radius: 22px;
      }}

      .article-title {{
        font-size: 28px;
      }}

      .article-paragraph,
      .article-list-item {{
        font-size: 17px;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="toolbar">
      <div class="toolbar-meta">
        <div>本页用于预览和复制公众号文章。</div>
        <div>点击右侧按钮后，可直接粘贴到微信公众号编辑器。</div>
      </div>
      <button id="copy-button" class="toolbar-copy" type="button">复制到公众号</button>
    </div>

    <article id="article-root" class="article">
        {content}
    </article>
  </div>

  <script>
    function copyComputedStyles(sourceNode, targetNode) {{
      if (sourceNode.nodeType !== Node.ELEMENT_NODE || targetNode.nodeType !== Node.ELEMENT_NODE) {{
        return;
      }}

      const computed = window.getComputedStyle(sourceNode);
      const styleText = Array.from(computed).map((name) => `${{name}}:${{computed.getPropertyValue(name)}};`).join("");
      targetNode.setAttribute("style", styleText);

      const sourceChildren = Array.from(sourceNode.childNodes);
      const targetChildren = Array.from(targetNode.childNodes);
      for (let i = 0; i < sourceChildren.length; i += 1) {{
        copyComputedStyles(sourceChildren[i], targetChildren[i]);
      }}
    }}

    function buildPayload() {{
      const article = document.getElementById("article-root");
      const clone = article.cloneNode(true);
      copyComputedStyles(article, clone);

      const wrapper = document.createElement("div");
      wrapper.appendChild(clone);

      return {{
        htmlPayload: wrapper.innerHTML,
        textPayload: article.innerText
      }};
    }}

    async function copyArticle() {{
      const payload = buildPayload();

      const legacyCopy = () => {{
        const listener = (event) => {{
          event.preventDefault();
          event.clipboardData.setData("text/html", payload.htmlPayload);
          event.clipboardData.setData("text/plain", payload.textPayload);
        }};

        document.addEventListener("copy", listener, {{ once: true }});
        const ok = document.execCommand("copy");
        if (!ok) {{
          throw new Error("execCommand copy failed");
        }}
      }};

      if (navigator.clipboard && window.ClipboardItem && window.isSecureContext) {{
        await navigator.clipboard.write([
          new ClipboardItem({{
            "text/html": new Blob([payload.htmlPayload], {{ type: "text/html" }}),
            "text/plain": new Blob([payload.textPayload], {{ type: "text/plain" }})
          }})
        ]);
        return;
      }}

      legacyCopy();
    }}

    document.getElementById("copy-button").addEventListener("click", async () => {{
      const button = document.getElementById("copy-button");
      const original = button.textContent;
      try {{
        await copyArticle();
        button.textContent = "已复制";
      }} catch (error) {{
        console.error(error);
        button.textContent = "复制失败";
      }}
      window.setTimeout(() => {{
        button.textContent = original;
      }}, 1600);
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    markdown_file = Path(args.markdown_file).resolve()
    if not markdown_file.exists():
        raise SystemExit(f"Markdown not found: {markdown_file}")

    output = (
        Path(args.output).resolve()
        if args.output
        else markdown_file.parent.parent / "preview" / f"{markdown_file.stem}.html"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    blocks = markdown_to_blocks(markdown_file)
    title = markdown_file.stem
    for block in blocks:
        if block.startswith('<h1 class="article-title">'):
            title = re.sub(r"^<h1 class=\"article-title\">|</h1>$", "", block)
            title = re.sub(r"<.*?>", "", title)
            break

    output.write_text(build_html(blocks, title), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
