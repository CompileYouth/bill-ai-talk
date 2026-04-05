---
name: bill-wechat-daily
description: Use when working in /Users/bytedance/Documents/my-projects/bill-ai-talk to draft, package, review, and publish daily WeChat articles for Bill的精神时光屋.
---

# Bill Wechat Daily

Use this skill when the user wants to create, revise, package, or publish a公众号文章 in `/Users/bytedance/Documents/my-projects/bill-ai-talk`.

## What This Skill Covers

- turning a discussion or source text into a publishable article
- generating article images and WeChat cover assets
- keeping `articles/`, `article-state/`, and publish metadata in sync
- preparing local preview and WeChat backend publishing
- committing and pushing when the user says `提交`

## Load These References First

- Read `/Users/bytedance/Documents/my-projects/bill-ai-talk/AGENTS.md`
- Read `/Users/bytedance/Documents/my-projects/bill-ai-talk/README.md`
- Read `/Users/bytedance/Documents/my-projects/bill-ai-talk/publishing-tracker.md`
- Read `references/path-map.md`
- Read `references/writing-rules.md`
- Read `references/publishing-rules.md`

## Default Workflow

1. Lock the article's single core judgment before drafting.
2. Stay in discussion mode until the user explicitly asks for the full article.
3. Write the article directly into `articles/`.
4. Keep article body content in `articles/` and packaging or outcome memory in `article-state/`.
5. When the user confirms a stable packaging decision, persist it instead of leaving it only in chat.
6. Keep the local preview and WeChat packaging flow usable from the current article files.
7. After drafting, review one thing first: does the piece have enough shareability and传播潜力 to generate signal?
8. When a stable cross-article rule changes, update both the live local skill under `~/.codex/skills/` and the mirrored repo copy under `skills/bill-wechat-daily/`.
9. When the user says `提交`, treat it as `commit + push`.

## Required Output Discipline

- Keep routine execution silent unless it fails.
- Do not create alternate article sources outside `articles/`.
- Do not leave durable packaging or feedback decisions only in runtime files.
- When a structural change affects files, scripts, trackers, preview, or skill rules, follow through in one pass before claiming completion.
