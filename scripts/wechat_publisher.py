#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import shlex
import subprocess
import textwrap
import time
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_wechat_page as wechat


ROOT = SCRIPT_DIR.parent
DEFAULTS = {
    "author": "编译青春",
    "reward": True,
    "original": True,
    "collection": "AI闲谈",
    "publish_time": "08:00",
    "cover_generator": "/Users/bytedance/Desktop/Generate Cover.html",
}

COVER_TEXT_RULES = [
    ("顶级 AI 产品", "顶级模型"),
    ("谁最强", "顶级模型"),
    ("能力层次", "能力层次"),
    ("软件工程", "软工更重"),
]


class PublisherError(RuntimeError):
    pass


def run_osascript(*lines: str) -> str:
    cmd = ["osascript"]
    for line in lines:
        cmd.extend(["-e", line])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise PublisherError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def chrome_exec_in_tab(url_fragment: str, script: str) -> str:
    encoded = base64.b64encode(script.encode("utf-8")).decode("ascii")
    wrapper = textwrap.dedent(
        f"""
        (() => {{
          const bytes = Uint8Array.from(atob({json.dumps(encoded)}), ch => ch.charCodeAt(0));
          const decoded = new TextDecoder().decode(bytes);
          return eval(decoded);
        }})()
        """
    ).strip()
    try:
        return run_osascript(
            'tell application "Google Chrome"',
            'repeat with w in windows',
            'repeat with i from 1 to count of tabs of w',
            'set t to tab i of w',
            'if (URL of t as text) contains ' + json.dumps(url_fragment) + ' then',
            'set active tab index of w to i',
            'set index of w to 1',
            'activate',
            'tell t to execute javascript ' + json.dumps(wrapper),
            'return result',
            'end if',
            'end repeat',
            'end repeat',
            'error "target-tab-not-found"',
            'end tell',
        )
    except PublisherError as exc:
        if "允许 Apple 事件中的 JavaScript" in str(exc):
            raise PublisherError(
                "Chrome 还没开启“允许 Apple 事件中的 JavaScript”。请在 Chrome 菜单栏打开：查看 > 开发者 > 允许 Apple 事件中的 JavaScript，然后再试。"
            ) from exc
        raise


def chrome_focus_tab(url_fragment: str) -> None:
    run_osascript(
        'tell application "Google Chrome"',
        'repeat with w in windows',
        'repeat with i from 1 to count of tabs of w',
        'set t to tab i of w',
        'if (URL of t as text) contains ' + json.dumps(url_fragment) + ' then',
        'set active tab index of w to i',
        'set index of w to 1',
        'activate',
        'return "ok"',
        'end if',
        'end repeat',
        'end repeat',
        'error "target-tab-not-found"',
        'end tell',
    )


def chrome_activate() -> None:
    run_osascript('tell application "Google Chrome" to activate')


def chrome_open_url(url: str) -> None:
    subprocess.run(
        f'open -a "Google Chrome" {shlex.quote(url)}',
        shell=True,
        check=True,
    )
    chrome_activate()


def editor_exec(script: str) -> str:
    return chrome_exec_in_tab("cgi-bin/appmsg?t=media/appmsg_edit_v2", script)


def current_title() -> str:
    return run_osascript('tell application "Google Chrome" to get title of active tab of front window')


def current_url() -> str:
    return run_osascript('tell application "Google Chrome" to get URL of active tab of front window')


def upload_file_in_front_dialog(file_path: Path) -> None:
    path_text = str(file_path.resolve())
    run_osascript(
        'tell application "Google Chrome" to activate',
        'tell application "System Events"',
        'keystroke "G" using {command down, shift down}',
        'delay 0.4',
        f'keystroke {json.dumps(path_text)}',
        'delay 0.2',
        'key code 36',
        'delay 0.4',
        'key code 36',
        'end tell',
    )


def wait_for(predicate, timeout: float = 15.0, interval: float = 0.5) -> None:
    end = time.time() + timeout
    while time.time() < end:
        if predicate():
            return
        time.sleep(interval)
    raise PublisherError("等待页面状态超时")


def render_cover(title: str, output_path: Path) -> Path:
    cover_uri = Path(DEFAULTS["cover_generator"]).resolve().as_uri()
    chrome_open_url(cover_uri)
    chrome_focus_tab(cover_uri)
    wait_for(lambda: "封面图生成器" in current_title(), timeout=10)
    js = textwrap.dedent(
        f"""
        (() => {{
          const input = document.getElementById('textInput');
          input.value = {json.dumps(title)};
          if (typeof drawPoster === 'function') {{
            drawPoster();
          }} else {{
            document.getElementById('generateBtn')?.click();
          }}
          return document.getElementById('posterCanvas').toDataURL('image/png');
        }})()
        """
    )
    data_uri = chrome_exec_in_tab(cover_uri, js)
    if not data_uri.startswith("data:image/png;base64,"):
        raise PublisherError("封面图生成失败")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(data_uri.split(",", 1)[1]))
    return output_path


def _safe_js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def derive_cover_text(title: str) -> str:
    for keyword, cover_text in COVER_TEXT_RULES:
        if keyword in title:
            return cover_text
    cleaned = (
        title.replace("AI", "")
        .replace("Agent", "")
        .replace("，", "")
        .replace("。", "")
        .replace("：", "")
        .replace(" ", "")
    )
    return cleaned[:4] or "AI文"


def extract_tldr_summary(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    in_tldr = False
    parts: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "> TL;DR":
            in_tldr = True
            continue
        if in_tldr:
            if stripped.startswith(">"):
                content = stripped[1:].strip()
                if content:
                    parts.append(content)
                continue
            break
    return " ".join(parts).replace("`", "").strip()


def build_fill_script(title: str, html_payload: str, author: str, collection: str, publish_date: str, publish_time: str, summary: str) -> str:
    return textwrap.dedent(
        f"""
        (() => {{
          const fireInput = (el) => {{
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
          }};
          const setNativeValue = (el, value) => {{
            const proto = Object.getPrototypeOf(el);
            const desc = Object.getOwnPropertyDescriptor(proto, 'value');
            if (desc && desc.set) desc.set.call(el, value);
            else el.value = value;
            fireInput(el);
          }};
          const visible = (el) => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
          const clickByContains = (text) => {{
            const hit = Array.from(document.querySelectorAll('button, a, div, span, label'))
              .find((el) => visible(el) && ((el.innerText || el.textContent || '').replace(/\\s+/g, ' ').includes(text)));
            if (!hit) return false;
            hit.click();
            return true;
          }};
          const setEditorHtml = (html) => {{
            const editable = document.querySelector('.ProseMirror[contenteditable=\"true\"]')
              || Array.from(document.querySelectorAll('[contenteditable=\"true\"], [role=\"textbox\"]'))
                .find((el) => visible(el) && el.clientHeight > 180);
            if (!editable) return '';
            editable.focus();
            editable.innerHTML = html;
            editable.dispatchEvent(new Event('input', {{ bubbles: true }}));
            editable.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return 'contenteditable';
          }};

          const titleInput = document.getElementById('title')
            || document.querySelector('textarea.js_title')
            || Array.from(document.querySelectorAll('textarea'))
              .find((el) => visible(el) && ((el.placeholder || '').includes('标题') || (el.id || '').includes('title')));
          const authorInput = document.getElementById('author')
            || document.querySelector('input.js_author')
            || Array.from(document.querySelectorAll('input'))
              .find((el) => visible(el) && ((el.placeholder || '').includes('作者') || (el.name || '') === 'author'));
          const summaryInput = document.getElementById('js_description')
            || Array.from(document.querySelectorAll('textarea, input'))
              .find((el) => visible(el) && (((el.placeholder || '') + ' ' + (el.getAttribute('name') || '') + ' ' + (el.id || '')).includes('摘要')));

          if (titleInput) {{
            titleInput.focus();
            setNativeValue(titleInput, {_safe_js_string(title)});
          }}

          if (authorInput) {{
            authorInput.focus();
            setNativeValue(authorInput, {_safe_js_string(author)});
          }}

          if (summaryInput) {{
            summaryInput.focus();
            setNativeValue(summaryInput, {_safe_js_string(summary)});
          }}

          const result = {{
            title: !!titleInput,
            author: !!authorInput,
            editor: setEditorHtml({_safe_js_string(html_payload)}),
            originalEntry: clickByContains('原创'),
            rewardEntry: !!document.querySelector('.js_reward_setting_checkbox'),
            collectionEntry: !!document.querySelector('.js_article_tags'),
            scheduleEntry: !!document.getElementById('js_send'),
            publishDate: {_safe_js_string(publish_date)},
            publishTime: {_safe_js_string(publish_time)},
            collection: {_safe_js_string(collection)},
            titleValue: titleInput ? titleInput.value : '',
            authorValue: authorInput ? authorInput.value : '',
            summaryValue: summaryInput ? summaryInput.value : '',
          }};
          return JSON.stringify(result);
        }})()
        """
    )


def build_inspect_script() -> str:
    return textwrap.dedent(
        """
        (() => {
          const visible = (el) => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
          const text = (el) => (el?.innerText || el?.textContent || '').replace(/\\s+/g, ' ').trim();
          const dialogs = Array.from(document.querySelectorAll('.weui-desktop-dialog__wrp'))
            .filter(visible)
            .map((el, index) => ({
              index,
              className: el.className,
              text: text(el).slice(0, 500),
              html: el.innerHTML.slice(0, 4000),
              radios: Array.from(el.querySelectorAll('input[type="radio"]')).map((r) => ({
                value: r.value,
                checked: r.checked,
              })),
              searchItems: Array.from(el.querySelectorAll('.search-result__wrp li, .weui-desktop-search__panel li, .search-result__item, .weui-desktop-dropdown__item'))
                .map((item) => text(item))
                .filter(Boolean),
            }));
          const collectionLabel = text(document.querySelector('.js_article_tags_label'));
          const originalLabel = text(document.querySelector('.js_original_status'));
          const rewardLabel = text(document.querySelector('.js_reward_setting_tips'));
          const rewardSwitch = !!document.querySelector('.js_reward_setting_checkbox');
          const originalSwitch = !!document.querySelector('.js_ori_setting_checkbox');
          const titleValue = document.querySelector('textarea.js_title')?.value || '';
          const authorValue = document.querySelector('input.js_author')?.value || '';
          const coverAreaText = Array.from(document.querySelectorAll('body *'))
            .filter(visible)
            .map(text)
            .filter(Boolean)
            .find((t) => t.includes('拖拽或选择封面') || t.includes('/120')) || '';
          const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map((el, index) => ({
            index,
            accept: el.getAttribute('accept') || '',
            id: el.id || '',
            className: el.className || '',
          }));
          const textareas = Array.from(document.querySelectorAll('textarea')).map((el, index) => ({
            index,
            id: el.id || '',
            className: el.className || '',
            placeholder: el.placeholder || '',
            value: el.value || '',
            visible: visible(el),
          }));
          const inputs = Array.from(document.querySelectorAll('input')).slice(0, 120).map((el, index) => ({
            index,
            type: el.type || '',
            id: el.id || '',
            className: el.className || '',
            placeholder: el.placeholder || '',
            name: el.name || '',
            value: el.value || '',
            visible: visible(el),
          }));
          const contenteditables = Array.from(document.querySelectorAll('[contenteditable="true"]')).map((el, index) => ({
            index,
            tagName: el.tagName,
            className: el.className || '',
            role: el.getAttribute('role') || '',
            text: text(el).slice(0, 300),
            visible: visible(el),
            width: el.clientWidth,
            height: el.clientHeight,
          }));
          const imageControls = Array.from(document.querySelectorAll('button, a, div, span, label'))
            .filter(visible)
            .map((el) => text(el))
            .filter((t) => t && (t.includes('图片') || t.includes('上传') || t.includes('插入')))
            .slice(0, 50);
          const imageNodes = Array.from(document.querySelectorAll('button, a, div, span, label'))
            .filter((el) => visible(el) && ['添加图片', '从图片库选择', '微信扫码上传', '合集', '未添加'].includes(text(el)))
            .map((el, index) => ({
              index,
              tagName: el.tagName,
              className: el.className || '',
              text: text(el),
              html: (el.outerHTML || '').slice(0, 1000),
              parentHtml: (el.parentElement?.outerHTML || '').slice(0, 1200),
            }));
          const rewardNode = document.querySelector('.js_reward_setting_checkbox');
          const originalNode = document.querySelector('.js_ori_setting_checkbox');
          const collectionNode = document.querySelector('.js_article_tags_label');
          return JSON.stringify({
            url: location.href,
            titleValue,
            authorValue,
            dialogs,
            collectionLabel,
            originalLabel,
            rewardLabel,
            rewardSwitch,
            originalSwitch,
            coverAreaText,
            fileInputs,
            textareas,
            inputs,
            contenteditables,
            imageControls,
            imageNodes,
            rewardNodeHtml: (rewardNode?.outerHTML || '').slice(0, 1000),
            rewardNodeParentHtml: (rewardNode?.closest('label, .frm_control_group, .frm_checkbox_label, .frm_controls, .setting-group')?.outerHTML || rewardNode?.parentElement?.outerHTML || '').slice(0, 2000),
            originalNodeHtml: (originalNode?.outerHTML || '').slice(0, 1000),
            originalNodeParentHtml: (originalNode?.closest('label, .frm_control_group, .frm_checkbox_label, .frm_controls, .setting-group')?.outerHTML || originalNode?.parentElement?.outerHTML || '').slice(0, 2000),
            collectionNodeHtml: (collectionNode?.outerHTML || '').slice(0, 1000),
            collectionNodeParentHtml: (collectionNode?.closest('label, .frm_control_group, .frm_checkbox_label, .frm_controls, .setting-group')?.outerHTML || collectionNode?.parentElement?.outerHTML || '').slice(0, 2000),
          });
        })()
        """
    )


def build_finalize_script(collection: str, publish_date: str, publish_time: str) -> str:
    return textwrap.dedent(
        f"""
        (() => {{
          const visible = (el) => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
          const text = (el) => (el?.innerText || el?.textContent || '').replace(/\\s+/g, ' ').trim();
          const setNativeValue = (el, value) => {{
            const proto = Object.getPrototypeOf(el);
            const desc = Object.getOwnPropertyDescriptor(proto, 'value');
            if (desc && desc.set) desc.set.call(el, value);
            else el.value = value;
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
          }};
          const clickContains = (root, selector, needle) => {{
            const scope = root || document;
            const hit = Array.from(scope.querySelectorAll(selector))
              .find((el) => visible(el) && text(el).includes(needle));
            if (!hit) return false;
            hit.click();
            return true;
          }};
          const clickVisibleAncestor = (el) => {{
            if (!el) return false;
            let node = el;
            while (node && node !== document.body) {{
              if (visible(node)) {{
                node.click();
                return true;
              }}
              node = node.parentElement;
            }}
            return false;
          }};
          const clickLoose = (needle) => clickContains(document, 'button, a, div, span, label', needle);
          const result = {{}};

          const originalToggle = document.querySelector('.js_ori_setting_checkbox');
          const originalSection = originalToggle?.closest('label, .frm_control_group, .frm_checkbox_label') || originalToggle?.parentElement;
          if ((text(document.querySelector('.js_original_status')) || '').includes('未声明')) {{
            clickVisibleAncestor(originalSection) || clickLoose('原创');
          }}
          const originalDlg = Array.from(document.querySelectorAll('.weui-desktop-dialog__wrp, .weui-desktop-popover, .weui-desktop-dialog'))
            .find((el) => visible(el) && text(el).includes('原创') && (text(el).includes('文字原创') || text(el).includes('声明原创')));
          if (originalDlg) {{
            result.originalDialogBefore = text(originalDlg).slice(0, 200);
            const agree = originalDlg.querySelector('input[type="checkbox"]');
            if (agree && !agree.checked) agree.click();
            const confirmBtn =
              originalDlg.querySelector('.weui-desktop-btn_primary') ||
              Array.from(originalDlg.querySelectorAll('button, a, div, span, label')).find((el) => visible(el) && text(el) === '确定');
            if (confirmBtn) confirmBtn.click();
            const closeBtn = originalDlg.querySelector('.weui-desktop-dialog__close-btn');
            if (visible(originalDlg) && closeBtn) closeBtn.click();
          }}

          const rewardText = text(document.querySelector('.js_reward_setting_tips'));
          if (rewardText.includes('不开启')) {{
            const rewardSwitch = document.querySelector('.js_reward_setting_checkbox');
            const rewardSection = rewardSwitch?.closest('label, .frm_control_group, .frm_checkbox_label') || rewardSwitch?.parentElement;
            clickVisibleAncestor(rewardSection) || clickLoose('赞赏');
            const rewardDlg = Array.from(document.querySelectorAll('.weui-desktop-dialog__wrp, .weui-desktop-popover, .weui-desktop-dialog'))
              .find((el) => visible(el) && text(el).includes('赞赏'));
            if (rewardDlg) {{
              const authorRadio = Array.from(rewardDlg.querySelectorAll('input[type="radio"]')).find((el) => el.value === '1');
              if (authorRadio && !authorRadio.checked) authorRadio.click();
              const recent = Array.from(rewardDlg.querySelectorAll('div, span, a, label'))
                .find((el) => visible(el) && text(el) === '编译青春');
              if (recent) recent.click();
              const agree = rewardDlg.querySelector('input[type="checkbox"]');
              if (agree && !agree.checked) agree.click();
              const confirmBtn =
                rewardDlg.querySelector('.weui-desktop-btn_primary') ||
                Array.from(rewardDlg.querySelectorAll('button, a, div, span, label')).find((el) => visible(el) && text(el) === '确定');
              if (confirmBtn) confirmBtn.click();
              const closeBtn = rewardDlg.querySelector('.weui-desktop-dialog__close-btn');
              if (visible(rewardDlg) && closeBtn) closeBtn.click();
            }}
          }}

          if ((text(document.querySelector('.js_article_tags_label')) || '').includes('未添加')) {{
            const collectionLabel = document.querySelector('.js_article_tags_label');
            clickVisibleAncestor(collectionLabel) || clickLoose('合集');
            const dlg = Array.from(document.querySelectorAll('.weui-desktop-dialog__wrp, .weui-desktop-popover, .weui-desktop-dialog, .popover_inner'))
              .find((el) => visible(el) && (text(el).includes('合集') || text(el).includes('搜索合集') || text(el).includes('选择合集')));
            if (dlg) {{
              const input = Array.from(dlg.querySelectorAll('input')).find((el) => visible(el) || (el.type || '') === 'text');
              if (input) {{
                input.focus();
                setNativeValue(input, {_safe_js_string(collection)});
                input.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', bubbles: true }}));
                input.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', bubbles: true }}));
              }}
              const option = Array.from(dlg.querySelectorAll('li, .weui-desktop-dropdown__item, .option-item, .js_dropmenu_item, .weui-desktop-form__option, div, span, a, label'))
                .find((el) => visible(el) && text(el).includes({_safe_js_string(collection)}));
              if (option) option.click();
              clickContains(dlg, 'button, a, div, span, label', '确认') || clickContains(dlg, 'button, a, div, span, label', '完成');
            }}
          }}

          clickLoose('群发');
          clickLoose('定时群发');
          const sendDlg = Array.from(document.querySelectorAll('.weui-desktop-dialog__wrp'))
            .find((el) => visible(el) && (text(el).includes('定时群发') || text(el).includes('群发时间')));
          if (sendDlg) {{
            const dateInput = Array.from(sendDlg.querySelectorAll('input')).find((el) => (el.value || '').includes('-') || (el.placeholder || '').includes('日期'));
            const timeInput = Array.from(sendDlg.querySelectorAll('input')).find((el) => (el.value || '').includes(':') || (el.placeholder || '').includes('时间'));
            if (dateInput) {{
              dateInput.focus();
              dateInput.value = {_safe_js_string(publish_date)};
              dateInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
              dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            if (timeInput) {{
              timeInput.focus();
              timeInput.value = {_safe_js_string(publish_time)};
              timeInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
              timeInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            clickContains(sendDlg, 'button, a, div, span, label', '预览');
            clickContains(sendDlg, 'button, a, div, span, label', '定时群发');
            clickContains(sendDlg, 'button, a, div, span, label', '确认');
          }}

          return JSON.stringify({{
            dialogsAfter: Array.from(document.querySelectorAll('.weui-desktop-dialog__wrp')).filter(visible).map((el) => text(el).slice(0, 300)),
            collectionLabelAfter: text(document.querySelector('.js_article_tags_label')),
            rewardLabelAfter: text(document.querySelector('.js_reward_setting_tips')),
            originalLabelAfter: text(document.querySelector('.js_original_status')),
          }});
        }})()
        """
    )


def inspect_editor_state() -> dict:
    return json.loads(editor_exec(build_inspect_script()))


def finalize_publish(collection: str, publish_date: str, publish_time: str) -> dict:
    return json.loads(editor_exec(build_finalize_script(collection, publish_date, publish_time)))


def upload_cover_to_editor(cover_path: Path) -> dict:
    chrome_focus_tab("cgi-bin/appmsg?t=media/appmsg_edit_v2")
    open_script = textwrap.dedent(
        """
        (() => {
          const visible = (el) => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
          const text = (el) => (el?.innerText || el?.textContent || '').replace(/\\s+/g, ' ').trim();
          const clickExact = (needle) => {
            const hit = Array.from(document.querySelectorAll('button, a, div, span, label'))
              .find((el) => visible(el) && text(el) === needle);
            if (!hit) return false;
            hit.click();
            return true;
          };
          clickExact('关闭');
          clickExact('取消');
          if (clickExact('添加图片')) return 'add-image';
          if (clickExact('从图片库选择')) return 'from-library';
          const input = Array.from(document.querySelectorAll('input[type="file"]')).at(-1);
          if (input && typeof input.showPicker === 'function') {
            input.showPicker();
            return 'show-picker';
          }
          return 'not-found';
        })()
        """
    )
    editor_exec(open_script)
    time.sleep(1.2)
    upload_file_in_front_dialog(cover_path)
    finish_script = textwrap.dedent(
        """
        (() => {
          const visible = (el) => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
          const text = (el) => (el?.innerText || el?.textContent || '').replace(/\\s+/g, ' ').trim();
          const clickExact = (needle) => {
            const hit = Array.from(document.querySelectorAll('button, a, div, span, label'))
              .find((el) => visible(el) && text(el) === needle);
            if (!hit) return false;
            hit.click();
            return true;
          };
          const clickFirstThumb = () => {
            const thumb = Array.from(document.querySelectorAll('img, li, div, span'))
              .find((el) => visible(el) && (
                (el.tagName === 'IMG' && el.clientWidth > 40 && el.clientHeight > 40) ||
                (text(el).includes('原图') && !text(el).includes('AI图片'))
              ));
            if (!thumb) return false;
            thumb.click();
            return true;
          };
          clickFirstThumb();
          const clickedInsert = clickExact('插入');
          const clickedConfirm = clickExact('确认') || clickExact('完成');
          const coverText = Array.from(document.querySelectorAll('body *'))
            .filter(visible)
            .map(text)
            .find((t) => t.includes('拖拽或选择封面') || t.includes('/120')) || '';
          return JSON.stringify({ clickedInsert, clickedConfirm, coverText });
        })()
        """
    )
    time.sleep(4.0)
    editor_exec(finish_script)
    time.sleep(4.0)
    return inspect_editor_state()


def publish_article(article_path: Path, publish_date: str) -> Path:
    title = article_path.stem.split("：", 1)[1]
    markdown_text = article_path.read_text(encoding="utf-8")
    html_payload = wechat.markdown_to_wechat_html(article_path)
    summary = extract_tldr_summary(markdown_text)
    cover_path = article_path.parent.parent / "assets" / f"{publish_date}-{article_path.stem.split('：',1)[0]}" / "wechat-cover.png"
    # Correct to article-specific asset directory when possible.
    asset_prefix = f"../assets/"
    asset_dir = None
    for line in markdown_text.splitlines():
        if "../assets/" in line:
            segment = line.split("../assets/", 1)[1].split("/", 1)[0]
            asset_dir = ROOT / "assets" / segment
            break
    if asset_dir is None:
        raise PublisherError("文章里没有找到配图目录，无法生成封面")
    cover_path = asset_dir / "wechat-cover.png"
    render_cover(derive_cover_text(title), cover_path)

    chrome_open_url("https://mp.weixin.qq.com/")
    wait_for(lambda: "微信公众平台" in current_title() or "公众号" in current_title(), timeout=20)
    token = current_url().split("token=")[-1].split("&", 1)[0]
    edit_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&lang=zh_CN&token={token}"
    chrome_open_url(edit_url)
    chrome_focus_tab("cgi-bin/appmsg?t=media/appmsg_edit_v2")
    wait_for(lambda: "cgi-bin/appmsg?t=media/appmsg_edit_v2" in current_url(), timeout=20)
    result = chrome_exec_in_tab(
        "cgi-bin/appmsg?t=media/appmsg_edit_v2",
        build_fill_script(
            title=title,
            html_payload=html_payload,
            author=DEFAULTS["author"],
            collection=DEFAULTS["collection"],
            publish_date=publish_date,
            publish_time=DEFAULTS["publish_time"],
            summary=summary,
        )
    )
    bundle_path = ROOT / ".publish" / "last-publish-bundle.json"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(
        json.dumps(
            {
                "article": str(article_path),
                "title": title,
                "publish_date": publish_date,
                "publish_time": DEFAULTS["publish_time"],
                "cover": str(cover_path),
                "fill_result": json.loads(result),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return bundle_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WeChat publish helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cover_parser = subparsers.add_parser("render-cover", help="Render a WeChat cover image for a title")
    cover_parser.add_argument("title")
    cover_parser.add_argument("output")

    publish_parser = subparsers.add_parser("publish", help="Prepare and autofill WeChat article publishing")
    publish_parser.add_argument("article")
    publish_parser.add_argument("--date", required=True)
    subparsers.add_parser("inspect", help="Inspect current WeChat editor state")
    finalize_parser = subparsers.add_parser("finalize", help="Finish WeChat publish flow on current editor page")
    finalize_parser.add_argument("--date", required=True)
    upload_cover_parser = subparsers.add_parser("upload-cover", help="Upload generated cover to current WeChat editor page")
    upload_cover_parser.add_argument("cover")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "render-cover":
        path = render_cover(args.title, Path(args.output))
        print(path)
        return
    if args.command == "publish":
        bundle_path = publish_article(Path(args.article), args.date)
        print(bundle_path)
        return
    if args.command == "inspect":
        print(json.dumps(inspect_editor_state(), ensure_ascii=False, indent=2))
        return
    if args.command == "finalize":
        print(json.dumps(finalize_publish(DEFAULTS["collection"], args.date, DEFAULTS["publish_time"]), ensure_ascii=False, indent=2))
        return
    if args.command == "upload-cover":
        print(json.dumps(upload_cover_to_editor(Path(args.cover)), ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
