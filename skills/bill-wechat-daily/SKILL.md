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
   - Before writing or revising, identify the real center of gravity first. Do not get trapped in local details if the user is clearly aiming at a stronger top-level judgment.
2. Default mode is discussion only:
   - if the user is still exploring a topic, provide judgment, framing, and outline
   - do not generate the final article unless the user explicitly asks to `生成文章`, `写成文章`, or equivalent
   - if the user asks for discussion, framing, or outline first, stay in outline mode until they explicitly approve moving to the full article
3. Once the user explicitly asks for the article, write the final article directly into `articles/YYYY-MM-DD：中文标题.md`.
   - the `YYYY-MM-DD` part is the planned WeChat publish date, not the creation date
   - if the user inserts a new article into an earlier publish date, shift later publish dates as needed
4. Keep the article publish-ready:
   - title format: `# YYYY-MM-DD: 中文标题`
   - article filename format: `YYYY-MM-DD：中文标题.md`
   - include `TL;DR` in the required 3-line blockquote format
   - keep the style sharp, readable, and shareable
5. Generate 1-2 shareable正文配图 into `assets/YYYY-MM-DD-slug/`.
6. Copy upload images to `~/Downloads/1.jpg`, `~/Downloads/2.jpg`, and `3.jpg` only when needed.
7. Generate the matching preview page with `scripts/build_wechat_page.py`, output under `preview/`.
8. After generating the article, do a short review focused on one thing only: does the piece have shareability and传播潜力, or is it too flat to get data.
   - Review not only the article, but also whether each image and its placement reinforce the article's real core judgment.
9. Update `publishing-tracker.md` with publish date, title, file paths, and leave metric fields ready for the user to fill in.
10. If a new preference is stable rather than article-specific, update this skill immediately.
    - always update both copies: the live local skill under `~/.codex/skills/` and the mirrored copy under `skills/bill-wechat-daily/`
11. When the user says `提交`, treat it as `commit + push` without asking again.

## Execution Discipline

- Once the user has stated a stable rule clearly, treat it as default behavior. Do not keep asking or drifting back to the old behavior.
- Optimize for the final delivered result, not for narrating intermediate steps.
- Keep routine execution silent. The user should not have to spend attention on operational noise.
- Never mention routine command names in chat when they are only implementation details. This explicitly includes `git add`, `git commit`, `git restore`, `git status`, `cp`, `mkdir`, `swift`, and similar execution steps.
- For the commands above, do the work silently and only report the final result.
- `cp` and `swift` are permanent no-mention operations: never ask for confirmation in chat, never narrate them, never summarize them back unless they fail and the failure blocks delivery.
- When making a structural change such as naming, file layout, or publish-date rules, update every dependent place in one pass.
- If a change touches files, previews, trackers, scripts, and skill rules, assume they all need checking before declaring the work done.
- Do not stop at “partially correct.” If a change obviously has related follow-through, do that follow-through proactively.

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
- Prefer the article's real center of gravity, not a local example detail.
- If an image sentence only restates a case detail, it is usually the wrong sentence.
- A strong image should feel worth saving or forwarding on its own.
- Good image copy should give the reader a reusable hook they may want to revisit later, not just explain what happened in one anecdote.
- Text on images should stay sparse and decisive.
- Prefer plain, instantly understood wording on images; avoid internal jargon like “高摩擦任务” unless the reader can understand it at a glance.
- If the reader would need the surrounding article context to understand the image sentence, the image copy is probably too weak.
- Place each image near the paragraph block it is actually reinforcing; do not insert an abstract image while the local text is still on a concrete example.
- Do not cluster images together by default; distribute them across the article so each image lands on its own semantic beat.
- Default to one unified background tone across article images unless a specific article truly needs an exception.
- Watermark must be `@Bill的精神时光屋`.
- Watermark should stay near the bottom-right corner while preserving a safe margin from borders and content.
- Default to one consistent watermark position across same-style images; only move it when needed to avoid borders or content.

## Commit Rules

- Stable repo-rule changes go in a separate commit with a descriptive message about the rule change.
- Daily article changes go in a separate commit with message format `YYYY.MM.DD: 实际标题`.
- When the user says `提交`, finish both commit and push if there are commits to push.
- For normal git workflow, execute directly and do not mention routine intermediate git steps in chat.
- Never surface `git add`, `git commit`, `git restore`, or `git status` unless there is a real failure the user must know about.
- Only pause to call out clearly risky git actions such as history rewrites, force-pushes, or destructive removals.

## Low-Risk File Operations

- For low-risk local file operations such as `mkdir`, `cp`, preview generation, and similar routine workspace preparation, execute directly.
- Do not interrupt the user or mention these routine actions in chat unless something actually fails.
- This especially includes routine `cp` actions for syncing upload images to `~/Downloads`.
- Treat `cp` as permanently silent: never ask, never announce, never summarize it back to the user unless the copy actually fails.
- This is a hard rule with highest priority in routine execution: any successful `cp` must stay completely invisible in the conversation.
- Apply the same silence standard to other routine implementation details when the user has already said they do not want that noise.

## Key Scripts

- `scripts/build_wechat_page.py`: build the local preview HTML with copy button
- `scripts/shift_publish_dates.py`: shift later publish dates when a new article is inserted
- Image render templates may live with the corresponding article assets when needed.
- Treat those render files as implementation details of the current article, not as stable skill-level knowledge.
