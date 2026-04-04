#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import build_wechat_page as wechat


ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "articles"
ARTICLE_RE = re.compile(r"^(?P<day>\d{4}-\d{2}-\d{2})：(?P<title>.+)\.md$")
PENDING_RE = re.compile(r"^未排期：(?P<title>.+)\.md$")


def _iter_article_paths() -> list[Path]:
    return sorted(
        [path for path in ARTICLES_DIR.rglob("*.md") if path.is_file() and path.name != ".DS_Store"],
        reverse=True,
    )


def load_article_list() -> list[dict[str, str]]:
    scheduled_by_month: dict[str, list[dict[str, str]]] = {}
    pending: list[dict[str, str]] = []
    for path in _iter_article_paths():
        match = ARTICLE_RE.match(path.name)
        if match:
            month = match.group("day")[:7]
            scheduled_by_month.setdefault(month, []).append(
                {
                    "date": match.group("day"),
                    "title": match.group("title"),
                    "file": path.relative_to(ARTICLES_DIR).as_posix(),
                    "month": month,
                    "pending": False,
                }
            )
            continue
        pending_match = PENDING_RE.match(path.name)
        if pending_match:
            pending.append(
                {
                    "date": "未排期",
                    "title": pending_match.group("title"),
                    "file": path.relative_to(ARTICLES_DIR).as_posix(),
                    "month": "未排期",
                    "pending": True,
                }
            )

    current_month = date.today().isoformat()[:7]
    groups: list[dict[str, object]] = []
    if pending:
        groups.append({"label": "候选", "expanded": True, "articles": pending})
    for month in sorted(scheduled_by_month.keys(), reverse=True):
        groups.append(
            {
                "label": month,
                "expanded": month == current_month,
                "articles": scheduled_by_month[month],
            }
        )
    return groups


def load_article_payload(file_name: str) -> dict[str, str]:
    path = ARTICLES_DIR / file_name
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(file_name)

    match = ARTICLE_RE.match(path.name)
    pending_match = PENDING_RE.match(path.name)
    if not match and not pending_match:
        raise FileNotFoundError(file_name)

    blocks = wechat.markdown_to_blocks(path)
    title = match.group("title") if match else pending_match.group("title")
    for block in blocks:
        if block.startswith('<h1 class="article-title">'):
            title = re.sub(r"^<h1 class=\"article-title\">|</h1>$", "", block)
            title = re.sub(r"<.*?>", "", title)
            break

    return {
        "date": match.group("day") if match else "未排期",
        "title": title,
        "file": path.relative_to(ARTICLES_DIR).as_posix(),
        "html": "\n".join(blocks),
    }
def load_copy_payload(file_name: str) -> dict[str, str]:
    path = ARTICLES_DIR / file_name
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(file_name)

    match = ARTICLE_RE.match(path.name)
    pending_match = PENDING_RE.match(path.name)
    if not match and not pending_match:
        raise FileNotFoundError(file_name)

    html_payload = wechat.markdown_to_wechat_html(path)
    text_payload = path.read_text(encoding="utf-8")
    return {"html": html_payload, "text": text_payload}


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
      --bg-2: #f3eee4;
      --paper: rgba(255, 253, 247, 0.96);
      --paper-2: rgba(255, 252, 244, 0.98);
      --ink: #181818;
      --muted: #68635b;
      --line: rgba(66, 112, 255, 0.14);
      --line-strong: rgba(66, 112, 255, 0.24);
      --accent: #31cfff;
      --accent-2: #7f6fff;
      --glow: rgba(49, 207, 255, 0.12);
      --panel: rgba(255, 253, 247, 0.86);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: "SF Pro Display", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(49, 207, 255, 0.08), transparent 22%),
        radial-gradient(circle at 85% 12%, rgba(127, 111, 255, 0.08), transparent 20%),
        linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(24,24,24,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(24,24,24,0.022) 1px, transparent 1px);
      background-size: 22px 22px;
      mask-image: radial-gradient(circle at center, black 44%, transparent 100%);
      opacity: 0.22;
    }}
    .page {{
      width: min(1400px, calc(100vw - 32px));
      margin: 24px auto;
      display: grid;
      grid-template-columns: minmax(320px, 320px) minmax(0, 1fr);
      gap: 20px;
      align-items: start;
    }}
    .sidebar {{
      position: sticky;
      top: 20px;
      width: 320px;
      min-width: 320px;
      max-width: 320px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--panel);
      backdrop-filter: blur(16px);
      box-shadow:
        0 18px 44px rgba(38, 28, 10, 0.08),
        inset 0 0 0 1px rgba(255,255,255,0.55);
    }}
    .brand {{
      margin: 0 0 6px;
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.03em;
      color: #121212;
      text-shadow: 0 0 12px rgba(49, 207, 255, 0.14);
    }}
    .subtitle {{
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
    }}
    .list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      width: 100%;
      max-height: calc(100vh - 170px);
      overflow-y: scroll;
      overflow-x: hidden;
      padding-right: 6px;
      scrollbar-width: thin;
      scrollbar-color: transparent transparent;
    }}
    .list::-webkit-scrollbar {{
      width: 7px;
    }}
    .list::-webkit-scrollbar-track {{
      background: transparent;
    }}
    .list::-webkit-scrollbar-thumb {{
      border-radius: 999px;
      background: transparent;
      border: 2px solid transparent;
      background-clip: padding-box;
    }}
    .sidebar:hover .list {{
      scrollbar-color: rgba(66, 112, 255, 0.22) transparent;
    }}
    .sidebar:hover .list::-webkit-scrollbar-thumb {{
      background: linear-gradient(180deg, rgba(66, 112, 255, 0.30), rgba(49, 207, 255, 0.24));
      border: 2px solid transparent;
      background-clip: padding-box;
    }}
    .month-group {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .month-header {{
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border: 1px solid rgba(66, 112, 255, 0.12);
      border-radius: 16px;
      padding: 10px 12px;
      background: rgba(255,255,255,0.72);
      color: #244562;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.03em;
      cursor: pointer;
    }}
    .month-body {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .item {{
      width: 100%;
      text-align: left;
      border: 1px solid rgba(66, 112, 255, 0.12);
      background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,255,255,0.80));
      border-radius: 18px;
      padding: 14px 14px 12px;
      cursor: pointer;
      transition: transform 140ms ease, border-color 140ms ease, background 140ms ease;
    }}
    .item:hover {{
      transform: translateY(-1px);
      border-color: rgba(49, 207, 255, 0.28);
      background: linear-gradient(180deg, rgba(49,207,255,0.10), rgba(255,255,255,0.88));
    }}
    .item.active {{
      border-color: var(--line-strong);
      background: linear-gradient(180deg, rgba(49,207,255,0.14), rgba(127,111,255,0.10));
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.24);
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
      color: #171717;
    }}
    .viewer-shell {{ min-width: 0; }}
    .viewer-meta {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      margin-bottom: 14px;
      padding: 14px 18px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background: var(--panel);
      backdrop-filter: blur(16px);
    }}
    .viewer-meta-main {{
      min-width: 0;
      flex: 1;
    }}
    .viewer-title {{
      margin: 0;
      font-size: 15px;
      color: var(--muted);
      line-height: 1.5;
    }}
    .viewer-actions {{
      display: flex;
      gap: 10px;
      align-items: center;
      justify-content: flex-end;
      flex-wrap: wrap;
    }}
    .meta-button {{
      appearance: none;
      border-radius: 999px;
      padding: 10px 16px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 140ms ease, filter 140ms ease;
      white-space: nowrap;
    }}
    .meta-button:hover {{
      filter: brightness(1.03);
      transform: translateY(-1px);
    }}
    .meta-button-primary {{
      border: 0;
      background: linear-gradient(135deg, rgba(49, 207, 255, 0.92), rgba(127, 111, 255, 0.88));
      color: #04111d;
      box-shadow: 0 10px 24px rgba(49, 207, 255, 0.12);
    }}
    .meta-button-secondary {{
      border: 1px solid rgba(66, 112, 255, 0.18);
      background: rgba(255,255,255,0.8);
      color: #245177;
    }}
    .meta-button-tertiary {{
      border: 1px solid rgba(36,81,119,0.16);
      background: rgba(255,251,244,0.92);
      color: #244562;
    }}
    .article {{
      padding: 40px 28px 50px;
      background:
        linear-gradient(180deg, rgba(255, 253, 247, 0.98), rgba(255, 251, 244, 0.98));
      border: 1px solid var(--line);
      border-radius: 28px;
      box-shadow:
        0 24px 60px rgba(38, 28, 10, 0.08),
        inset 0 0 0 1px rgba(255,255,255,0.58);
    }}
    .article-title {{
      margin: 0 0 18px;
      font-size: 34px;
      line-height: 1.3;
      letter-spacing: -0.02em;
      color: #111111;
      text-shadow: 0 0 10px rgba(49, 207, 255, 0.08);
    }}
    .article-heading {{
      margin: 30px 0 10px;
      font-size: 24px;
      line-height: 1.4;
      color: #1b1b1b;
    }}
    .article-subheading {{
      margin: 26px 0 10px;
      font-size: 20px;
      line-height: 1.45;
      color: #202020;
    }}
    .article-paragraph {{
      margin: 0 0 20px;
      font-size: 16px;
      line-height: 1.8;
      color: #282828;
    }}
    .article strong {{
      font-weight: 800;
      color: #101010;
    }}
    .article code {{
      display: inline-block;
      padding: 0.08em 0.42em;
      margin: 0 0.08em;
      border-radius: 8px;
      background: rgba(49, 207, 255, 0.10);
      border: 1px solid rgba(49, 207, 255, 0.18);
      color: #0c5a72;
      font-size: 0.92em;
      font-family: "SFMono-Regular", "JetBrains Mono", "Menlo", monospace;
      vertical-align: baseline;
    }}
    .article-link {{
      color: var(--accent);
      text-decoration: none;
      border-bottom: 1px solid rgba(49, 207, 255, 0.28);
    }}
    .article-link:hover {{ border-bottom-color: var(--accent); }}
    .article-quote {{
      margin: 0 0 14px;
      padding: 12px 16px;
      background: linear-gradient(180deg, rgba(49,207,255,0.08), rgba(127,111,255,0.06));
      border-left: 4px solid var(--accent);
      border-radius: 16px;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.42);
    }}
    .article-quote p {{
      margin: 0;
      font-size: 15px;
      line-height: 1.7;
      color: #3c3730;
    }}
    .article-quote p + p {{ margin-top: 4px; }}
    .article-figure {{ margin: 34px 0; }}
    .article-image {{
      display: block;
      width: 100%;
      height: auto;
      border-radius: 18px;
      box-shadow: 0 12px 28px rgba(38, 28, 10, 0.10);
    }}
    .article-list {{
      margin: 0 0 20px;
      padding-left: 24px;
    }}
    .article-list-item {{
      font-size: 16px;
      line-height: 1.8;
      margin-bottom: 8px;
      color: #282828;
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
        padding: 24px 18px 34px;
        border-width: 3px;
        border-radius: 22px;
      }}
      .article-title {{ font-size: 28px; }}
      .article-paragraph,
      .article-list-item {{ font-size: 16px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <aside class="sidebar">
      <h1 class="brand">heyBill</h1>
      <p class="subtitle">直接读取 articles 下的文章，按时间倒排浏览，并一键复制富文本到微信公众号。</p>
      <div id="article-list" class="list"></div>
    </aside>

    <section class="viewer-shell">
      <div class="viewer-meta">
        <div class="viewer-meta-main">
          <p id="viewer-meta" class="viewer-title">正在加载文章…</p>
        </div>
        <div class="viewer-actions">
          <button id="schedule-button" class="meta-button meta-button-tertiary" type="button" style="display:none">分配发送日期</button>
          <button id="copy-title-button" class="meta-button meta-button-secondary" type="button">复制标题</button>
          <button id="copy-button" class="meta-button meta-button-primary" type="button">复制当前文章</button>
        </div>
      </div>
      <article id="article-root" class="article"></article>
    </section>
  </div>

  <script>
    let groups = [];
    let flatArticles = [];
    let currentIndex = 0;

    function flashButton(button, text) {{
      const original = button.dataset.originalText || button.textContent;
      button.dataset.originalText = original;
      button.textContent = text;
      window.setTimeout(() => {{
        button.textContent = original;
      }}, 1600);
    }}

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

      groups.forEach((group) => {{
        const wrapper = document.createElement("section");
        wrapper.className = "month-group";

        const header = document.createElement("button");
        header.type = "button";
        header.className = "month-header";
        header.setAttribute("data-expanded", group.expanded ? "true" : "false");
        header.innerHTML = `
          <span>${{group.label}}</span>
          <span>${{group.expanded ? "−" : "+"}}</span>
        `;

        const body = document.createElement("div");
        body.className = "month-body";
        if (!group.expanded) body.style.display = "none";

        header.addEventListener("click", () => {{
          group.expanded = !group.expanded;
          renderList();
        }});

        group.articles.forEach((article) => {{
          const index = flatArticles.findIndex((item) => item.file === article.file);
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
          body.appendChild(button);
        }});

        wrapper.appendChild(header);
        wrapper.appendChild(body);
        list.appendChild(wrapper);
      }});
    }}

    async function renderCurrentArticle() {{
      const current = flatArticles[currentIndex];
      const payload = await fetchJSON(`/api/article?file=${{encodeURIComponent(current.file)}}`);
      document.getElementById("article-root").innerHTML = payload.html;
      document.getElementById("viewer-meta").textContent = `${{payload.date}} · ${{payload.title}}`;
      const isPending = current.pending;
      document.getElementById("schedule-button").style.display = isPending ? "inline-flex" : "none";
      document.getElementById("copy-title-button").style.display = isPending ? "none" : "inline-flex";
      document.getElementById("copy-button").style.display = isPending ? "none" : "inline-flex";
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

    async function copyArticle() {{
      const current = flatArticles[currentIndex];
      const response = await fetch(`/api/copy-payload?file=${{encodeURIComponent(current.file)}}`);
      if (!response.ok) {{
        throw new Error("copy article failed");
      }}
      const payload = await response.json();

      if (window.ClipboardItem && navigator.clipboard?.write) {{
        const item = new ClipboardItem({{
          "text/html": new Blob([payload.html], {{ type: "text/html" }}),
          "text/plain": new Blob([payload.text], {{ type: "text/plain" }})
        }});
        await navigator.clipboard.write([item]);
        return;
      }}

      const listener = (event) => {{
        event.preventDefault();
        event.clipboardData.setData("text/html", payload.html);
        event.clipboardData.setData("text/plain", payload.text);
      }};
      document.addEventListener("copy", listener, {{ once: true }});
      const ok = document.execCommand("copy");
      if (!ok) {{
        throw new Error("copy article failed");
      }}
    }}

    async function copyTitle() {{
      const current = flatArticles[currentIndex];
      const text = current.title;
      if (navigator.clipboard && window.isSecureContext) {{
        await navigator.clipboard.writeText(text);
        return;
      }}

      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "readonly");
      textarea.style.position = "absolute";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(textarea);
      if (!ok) throw new Error("copy title failed");
    }}

    document.getElementById("copy-button").addEventListener("click", async () => {{
      const button = document.getElementById("copy-button");
      try {{
        await copyArticle();
        flashButton(button, "已复制");
      }} catch (error) {{
        console.error(error);
        flashButton(button, "复制失败");
      }}
    }});

    document.getElementById("copy-title-button").addEventListener("click", async () => {{
      const button = document.getElementById("copy-title-button");
      try {{
        await copyTitle();
        flashButton(button, "标题已复制");
      }} catch (error) {{
        console.error(error);
        flashButton(button, "复制失败");
      }}
    }});

    document.getElementById("schedule-button").addEventListener("click", async () => {{
      const current = flatArticles[currentIndex];
      const value = window.prompt("请输入发送日期（YYYY-MM-DD）");
      if (!value) return;
      const button = document.getElementById("schedule-button");
      try {{
        const response = await fetch("/api/schedule", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ file: current.file, date: value }})
        }});
        if (!response.ok) throw new Error("schedule failed");
        const result = await response.json();
        groups = await fetchJSON("/api/articles");
        flatArticles = groups.flatMap((group) => group.articles);
        currentIndex = Math.max(flatArticles.findIndex((item) => item.file === result.file), 0);
        await renderCurrentArticle();
        renderList();
        flashButton(button, "已分配");
      }} catch (error) {{
        console.error(error);
        flashButton(button, "分配失败");
      }}
    }});

    async function boot() {{
      groups = await fetchJSON("/api/articles");
      flatArticles = groups.flatMap((group) => group.articles);
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

        if parsed.path == "/api/copy-payload":
            file_name = parse_qs(parsed.query).get("file", [""])[0]
            try:
                payload = load_copy_payload(file_name)
            except FileNotFoundError:
                self._send(b'{"error":"not found"}', "application/json; charset=utf-8", HTTPStatus.NOT_FOUND)
                return
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send(body, "application/json; charset=utf-8")
            return

        self._send(b"Not Found", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/schedule":
            self._send(b"Not Found", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
            from publish_pipeline import schedule_article

            article_path = schedule_article(payload["file"], payload["date"])
            body = json.dumps(
                {
                    "file": article_path.relative_to(ARTICLES_DIR).as_posix(),
                    "date": payload["date"],
                },
                ensure_ascii=False,
            ).encode("utf-8")
            self._send(body, "application/json; charset=utf-8")
        except Exception:
            self._send(b'{"error":"schedule failed"}', "application/json; charset=utf-8", HTTPStatus.BAD_REQUEST)

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
