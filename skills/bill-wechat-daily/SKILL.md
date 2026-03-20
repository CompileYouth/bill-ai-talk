---
name: bill-wechat-daily
description: Use when working in /Users/bytedance/Documents/my-projects/bill-ai-talk to draft, revise, package, and publish-ready daily WeChat articles for Bill的精神时光屋, including article writing, image generation, preview-page generation, formatting-memory updates, and commit/push workflow.
---

# Bill Wechat Daily

Use this skill when the user wants to create or revise a daily公众号文章 in `/Users/bytedance/Documents/my-projects/bill-ai-talk`.

## What This Skill Covers

- turning a chat topic into a publishable WeChat article
- generating matching正文配图 and syncing upload copies to `~/Downloads`
- generating a local preview page with a copy button
- updating stable writing/formatting rules when a new preference should be remembered
- committing and pushing with the repo's required commit split

## Load These References First

- Read `/Users/bytedance/Documents/my-projects/bill-ai-talk/README.md`
- Read `/Users/bytedance/Documents/my-projects/bill-ai-talk/publishing-tracker.md`
- If needed, read `references/path-map.md` for the file layout and default scripts

## Default Workflow

1. Clarify the article's single core judgment. Do not turn the post into a discussion transcript.
2. Default mode is discussion only:
   - if the user is still exploring a topic, provide judgment, framing, and outline
   - do not generate the final article unless the user explicitly asks to `生成文章`, `写成文章`, or equivalent
3. Once the user explicitly asks for the article, write the final article directly into `articles/YYYY-MM-DD-slug.md`.
   - the `YYYY-MM-DD` part is the planned WeChat publish date, not the creation date
   - if the user inserts a new article into an earlier publish date, shift later publish dates as needed
4. Keep the article publish-ready:
   - title format: `# YYYY-MM-DD: 实际标题`
   - include `TL;DR` in the required 3-line blockquote format
   - keep the style sharp, readable, and shareable
5. Generate 1-2 shareable正文配图 into `assets/YYYY-MM-DD-slug/`.
6. Copy upload images to `~/Downloads/1.jpg`, `~/Downloads/2.jpg`, and `3.jpg` only when needed.
7. Generate the matching preview page with `scripts/build_wechat_page.py`, output under `preview/`.
8. After generating the article, do a short review focused on one thing only: does the piece have shareability and传播潜力, or is it too flat to get data.
9. Update `publishing-tracker.md` with publish date, title, file paths, and leave metric fields ready for the user to fill in.
10. If a new preference is stable rather than article-specific, update this skill immediately.
    - always update both copies: the live local skill under `~/.codex/skills/` and the mirrored copy under `skills/bill-wechat-daily/`
11. When the user says `提交`, treat it as `commit + push` without asking again.

## Writing Rules That Matter Most

- The post should state the final judgment directly, not replay the conversation.
- Background provided by the user is for your understanding; only keep what strengthens the reader-facing argument.
- For short观点文, prefer 3-4 compact sections or paragraphs.
- Important claims may be bolded, but only when they are truly the central takeaway.
- The article should make readers feel the account has a clear direction, not just a diary of thoughts.
- After drafting, review whether the piece actually has a sharp enough shareable sentence and enough emotional or judgmental tension to spread.

## Image Rules That Matter Most

- Images are for传播, not for re-explaining the whole article.
- One image should carry one central judgment.
- Text on images should stay sparse and decisive.
- Default to one unified background tone across article images unless a specific article truly needs an exception.
- Watermark must be `@Bill的精神时光屋`.
- Watermark should stay near the bottom-right corner while preserving a safe margin from borders and content.
- Default to one consistent watermark position across same-style images; only move it when needed to avoid borders or content.

## Commit Rules

- Stable repo-rule changes go in a separate commit with a descriptive message about the rule change.
- Daily article changes go in a separate commit with message format `YYYY.MM.DD: 实际标题`.
- When the user says `提交`, finish both commit and push if there are commits to push.
- For normal `git add`, `commit`, and `push`, execute directly and do not mention routine intermediate git steps in chat.
- Only pause to call out clearly risky git actions such as history rewrites, force-pushes, or destructive removals.

## Low-Risk File Operations

- For low-risk local file operations such as `mkdir`, `cp`, preview generation, and similar routine workspace preparation, execute directly.
- Do not interrupt the user or mention these routine actions in chat unless something actually fails.

## Key Scripts

- `scripts/build_wechat_page.py`: build the local preview HTML with copy button
- `scripts/shift_publish_dates.py`: shift later publish dates when a new article is inserted
- Image render templates may live with the corresponding article assets when needed.
- Treat those render files as implementation details of the current article, not as stable skill-level knowledge.
