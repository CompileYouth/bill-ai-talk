#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import build_wechat_page as wechat


ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "articles"
ARTICLE_RE = re.compile(r"^(?P<day>\d{4}-\d{2}-\d{2})：(?P<title>.+)\.md$")


def load_article_list() -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for path in sorted(ARTICLES_DIR.glob("*.md"), reverse=True):
        if path.name == ".DS_Store":
            continue
        match = ARTICLE_RE.match(path.name)
        if not match:
            continue
        items.append(
            {
                "date": match.group("day"),
                "title": match.group("title"),
                "file": path.name,
            }
        )
    return items


def load_article_payload(file_name: str) -> dict[str, str]:
    path = ARTICLES_DIR / file_name
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(file_name)

    match = ARTICLE_RE.match(path.name)
    if not match:
        raise FileNotFoundError(file_name)

    blocks = wechat.markdown_to_blocks(path)
    title = match.group("title")
    for block in blocks:
        if block.startswith('<h1 class="article-title">'):
            title = re.sub(r"^<h1 class=\"article-title\">|</h1>$", "", block)
            title = re.sub(r"<.*?>", "", title)
            break

    return {
        "date": match.group("day"),
        "title": title,
        "file": path.name,
        "html": "\n".join(blocks),
    }


def shell_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>heyBill</title>
  <style>
    :root {{
      --bg: #f7f3ea;
      --paper: #fffdf7;
      --ink: #181818;
      --muted: #676056;
      --line: #1f1f1f;
      --accent: #d94f2b;
      --panel: rgba(255, 253, 247, 0.88);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(217, 79, 43, 0.10), transparent 24%),
        linear-gradient(180deg, #f8f3e8 0%, #f4efe3 100%);
    }}
    .page {{
      width: min(1400px, calc(100vw - 32px));
      margin: 24px auto;
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      gap: 20px;
      align-items: start;
    }}
    .sidebar {{
      position: sticky;
      top: 20px;
      padding: 18px;
      border: 2px solid rgba(31, 31, 31, 0.12);
      border-radius: 24px;
      background: var(--panel);
      backdrop-filter: blur(8px);
      box-shadow: 0 14px 40px rgba(38, 28, 10, 0.08);
    }}
    .brand {{
      margin: 0 0 6px;
      font-size: 30px;
      font-weight: 800;
      letter-spacing: -0.03em;
    }}
    .subtitle {{
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
    }}
    .copy-button {{
      width: 100%;
      appearance: none;
      border: 0;
      border-radius: 999px;
      padding: 13px 18px;
      background: var(--ink);
      color: #fff;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      margin-bottom: 18px;
    }}
    .copy-button:hover {{ background: #000; }}
    .list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-height: calc(100vh - 220px);
      overflow: auto;
      padding-right: 4px;
    }}
    .item {{
      width: 100%;
      text-align: left;
      border: 2px solid rgba(31, 31, 31, 0.10);
      background: #fffdf8;
      border-radius: 18px;
      padding: 14px 14px 12px;
      cursor: pointer;
      transition: transform 140ms ease, border-color 140ms ease, background 140ms ease;
    }}
    .item:hover {{
      transform: translateY(-1px);
      border-color: rgba(31, 31, 31, 0.24);
    }}
    .item.active {{
      border-color: var(--ink);
      background: #fff6eb;
    }}
    .item-date {{
      display: block;
      margin-bottom: 6px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .item-title {{
      font-size: 15px;
      line-height: 1.6;
      font-weight: 700;
      color: var(--ink);
    }}
    .viewer-shell {{ min-width: 0; }}
    .viewer-meta {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      margin-bottom: 14px;
      padding: 14px 18px;
      border: 2px solid rgba(31, 31, 31, 0.12);
      border-radius: 20px;
      background: var(--panel);
      backdrop-filter: blur(8px);
    }}
    .viewer-title {{
      margin: 0;
      font-size: 15px;
      color: var(--muted);
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
    .article-link {{
      color: var(--accent);
      text-decoration: none;
      border-bottom: 1px solid rgba(217, 79, 43, 0.36);
    }}
    .article-link:hover {{ border-bottom-color: var(--accent); }}
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
    .article-quote p + p {{ margin-top: 8px; }}
    .article-figure {{ margin: 28px 0; }}
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
    @media (max-width: 980px) {{
      .page {{ grid-template-columns: 1fr; }}
      .sidebar {{ position: static; }}
      .list {{ max-height: none; }}
    }}
    @media (max-width: 700px) {{
      .page {{
        width: min(100vw - 20px, 1400px);
        margin: 14px auto 24px;
      }}
      .article {{
        padding: 28px 22px 36px;
        border-width: 3px;
        border-radius: 22px;
      }}
      .article-title {{ font-size: 28px; }}
      .article-paragraph,
      .article-list-item {{ font-size: 17px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <aside class="sidebar">
      <h1 class="brand">heyBill</h1>
      <p class="subtitle">直接读取 articles 下的文章，按时间倒排浏览，并一键复制富文本到微信公众号。</p>
      <button id="copy-button" class="copy-button" type="button">复制当前文章</button>
      <div id="article-list" class="list"></div>
    </aside>

    <section class="viewer-shell">
      <div class="viewer-meta">
        <p id="viewer-meta" class="viewer-title">正在加载文章…</p>
      </div>
      <article id="article-root" class="article"></article>
    </section>
  </div>

  <script>
    let articles = [];
    let currentIndex = 0;

    async function fetchJSON(url) {{
      const response = await fetch(url);
      if (!response.ok) {{
        throw new Error(`Request failed: ${{response.status}}`);
      }}
      return response.json();
    }}

    function renderList() {{
      const list = document.getElementById("article-list");
      list.innerHTML = "";

      articles.forEach((article, index) => {{
        const button = document.createElement("button");
        button.type = "button";
        button.className = `item${{index === currentIndex ? " active" : ""}}`;
        button.innerHTML = `
          <span class="item-date">${{article.date}}</span>
          <span class="item-title">${{article.title}}</span>
        `;
        button.addEventListener("click", async () => {{
          currentIndex = index;
          await renderCurrentArticle();
          renderList();
        }});
        list.appendChild(button);
      }});
    }}

    async function renderCurrentArticle() {{
      const current = articles[currentIndex];
      const payload = await fetchJSON(`/api/article?file=${{encodeURIComponent(current.file)}}`);
      document.getElementById("article-root").innerHTML = payload.html;
      document.getElementById("viewer-meta").textContent = `${{payload.date}} · ${{payload.title}}`;
    }}

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
        if (!ok) throw new Error("execCommand copy failed");
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

    async function boot() {{
      articles = await fetchJSON("/api/articles");
      await renderCurrentArticle();
      renderList();
    }}

    boot().catch((error) => {{
      console.error(error);
      document.getElementById("viewer-meta").textContent = "加载失败";
      document.getElementById("article-root").innerHTML = `<p class="article-paragraph">${html.escape("heyBill 启动失败，请检查本地服务是否正在运行。")}</p>`;
    }});
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path in {"/", "/index.html"}:
            body = shell_html().encode("utf-8")
            self._send(body, "text/html; charset=utf-8")
            return

        if parsed.path == "/api/articles":
            body = json.dumps(load_article_list(), ensure_ascii=False).encode("utf-8")
            self._send(body, "application/json; charset=utf-8")
            return

        if parsed.path == "/api/article":
            file_name = parse_qs(parsed.query).get("file", [""])[0]
            try:
                payload = load_article_payload(file_name)
            except FileNotFoundError:
                self._send(b'{"error":"not found"}', "application/json; charset=utf-8", HTTPStatus.NOT_FOUND)
                return
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send(body, "application/json; charset=utf-8")
            return

        self._send(b"Not Found", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run heyBill local article browser.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4868)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
