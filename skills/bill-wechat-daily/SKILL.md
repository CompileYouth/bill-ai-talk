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
   - if there is any ambiguity, bias toward outline-only mode rather than drafting the article prematurely
   - even when the topic is detailed and article-like, still stop at outline first unless the user explicitly asks for the full article in the current turn
3. When the user explicitly asks for the article and has already specified a publish date, write it directly into `articles/YYYY-MM-DD：中文标题.md`.
4. When the user explicitly asks for the article but has not specified a publish date, write the first publishable draft into `candidates/`.
   - do not put an undated draft into `articles/`
   - candidate files should be easy to enumerate so the user can say “把候选里的第 2 篇排到 2026-03-31”
5. After the user assigns a publish date, promote that candidate into `articles/YYYY-MM-DD：中文标题.md`.
   - the `YYYY-MM-DD` part is the planned WeChat publish date, not the creation date
   - if the user inserts a new article into an earlier publish date, shift later publish dates as needed
6. Keep the article publish-ready:
   - article filename format: `YYYY-MM-DD：中文标题.md`
   - do not include the article title inside the article body; the body should start from `TL;DR` or正文内容 so copy/paste into WeChat does not duplicate the title
   - include `TL;DR` in the required 3-line blockquote format
   - keep the style sharp, readable, and shareable
7. Generate 1-2 shareable正文配图 into `assets/`.
8. Copy upload images to `~/Downloads/1.jpg`, `~/Downloads/2.jpg`, and `3.jpg` only when needed.
9. Generate the matching preview page with `scripts/build_wechat_page.py`, output under `preview/`.
10. After generating the article, do a short review focused on one thing only: does the piece have shareability and传播潜力, or is it too flat to get data.
   - Review not only the article, but also whether each image and its placement reinforce the article's real core judgment.
11. Once a candidate is assigned a publish date, update `publishing-tracker.md` with publish date, title, file paths, and leave metric fields ready for the user to fill in.
12. After a candidate is assigned a publish date, default to automatically configuring the WeChat backend using Chrome default profile, existing login state, and the repo's publish defaults.
    - author: `编译青春`
    - reward: enabled
    - original: enabled
    - collection: `AI闲谈`
    - scheduled publish time: `08:00`
    - only stop for user input when the Chrome login state has expired and scanning is required
13. If a new preference is stable rather than article-specific, update this skill immediately.
    - always update both copies: the live local skill under `~/.codex/skills/` and the mirrored copy under `skills/bill-wechat-daily/`
   - do not wait for an extra reminder; after each substantial discussion, proactively extract and store stable rules, priorities, and strategic judgments
14. When the user says `提交`, treat it as `commit + push` without asking again.

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
- The same proactive rule applies to memory: if the user has clarified something that is obviously stable and reusable, store it immediately instead of waiting to be told.
- Remove obvious throwaway test artifacts proactively once they are no longer needed; do not leave fake article rows, fake preview pages, or placeholder publish records behind waiting for the user to notice.

## Writing Rules That Matter Most

- The post should state the final judgment directly, not replay the conversation.
- When using acronyms or abbreviations that a general公众号读者 may not know, always write the full term the first time it appears before using the short form.
- Background provided by the user is for your understanding; only keep what strengthens the reader-facing argument.
- Distinguish strictly between writing requirements and article content. Explanations about why a claim is safer, what evidence standard is being used, or what the model is trying to avoid are internal guidance unless they naturally belong to the reader-facing argument.
- Never leak backstage framing into the article. Sentences that sound like “I say this because…”, “the point here is…”, or “the real basis is…” are often process notes in disguise and should be cut unless the reader genuinely needs them.
- For short观点文, prefer 3-4 compact sections or paragraphs.
- There are two default article modes:
- Short judgment post: for casual daily观点文, default to about 500 Chinese characters.
- Deep explanatory post: when the topic is clearly about explaining a framework, technical evolution, or a layered model, default to writing it through clearly even without the 500-character limit.
- For short judgment posts, default behavior is to compress, not to elaborate. Keep only the sharpest judgment, one strong analogy or example, and one strong closing line.
- For deep explanatory posts, optimize first for clarity, structure, and getting the thing fully explained; do not mechanically force it back into a short post shape.
- In deep explanatory posts, the opening hook is only a hook. Once the topic is introduced, stop repeating the hook and drive the body around the real thesis.
- Do not let a lead-in example, comment, or trigger phrase steal the article's center of gravity. The body should quickly pivot to the main framework and stay there.
- In deep explanatory posts, title, body, headings, and images must all point at the same thesis. If any one of them is still orbiting the hook instead of the thesis, the piece is structurally wrong.
- Do not write section headings as writing-process labels like “再回头看...” or “最后落到...”. Headings must carry information, not narrate the author's structure.
- Do not add an image just to reach a count. A weak second image is worse than having only one strong image.
- For deep posts, check explicitly for four failure modes before considering the draft acceptable: the hook stealing focus, repeated restatement of the hook, empty section headings, and decorative images with no information gain.
- In deep posts, control is often more important than adding material. Ask first what should be deleted, not only what else could be explained.
- Do not “explain more” when the real problem is structure. Fix thesis, paragraph roles, headings, and image purpose before adding any new exposition.
- Before showing a deep post to the user, self-check whether any sentence is quietly judging the reader instead of only stating the author's view.
- Do not hand the user a structural half-draft. A deep post should be checked for title-body alignment, hook retreat, heading information value, and image necessity before it is shown.
- The operating order for deep posts is fixed: first lock the thesis, then delete distractions, then build structure, and only then polish sentences. Do not reverse this order.
- Important claims may be bolded, but only when they are truly the central takeaway.
- Inline code / backticks must be used sparingly. Do not wrap every product name or common term in backticks; keep them only for genuinely necessary emphasis, exact identifiers, commands, paths, or terms that would otherwise be ambiguous.
- The article should make readers feel the account has a clear direction, not just a diary of thoughts.
- After drafting, review whether the piece actually has a sharp enough shareable sentence and enough emotional or judgmental tension to spread.
- The account's north star is not generic AI commentary; it is to build recognizable influence around AI-era individual upgrading and the road toward a one-person company.
- When evaluating topics, prefer pieces that strengthen a repeatable account identity over isolated “interesting thoughts”.
- When the user changes an article title, treat it as a full propagation change: update the article filename, preview filename, tracker entry, and any local site entry points in one pass before saying the change is done.
- Do not use weak proxies like user scale or vendor self-description as proof that a product is first-tier. If an article makes a first-tier or ranking claim, prefer third-party cross-model evaluations and keep the wording restrained.
- Meta-instructions about evidence standard, compliance, tone, or framing are writing constraints by default, not article sentences.
- For product-comparison articles, prefer concrete product positioning and the user's real usage split over generic “who is strongest” framing.
- When the user changes an article title, treat it as a full propagation change: update the article filename, preview filename, tracker entry, and anything the local site uses in one pass before saying it is changed.
- Do not use user-growth, vendor self-description, or other weak proxies as proof that something is first-tier. If the article makes a ranking or first-tier claim, prefer third-party cross-model evaluations and keep the wording restrained.
- When the user gives meta-instructions about evidence standard, compliance, tone, or framing, treat them as writing constraints by default, not as sentences for the article.
- For product-comparison articles, prefer concrete product positioning and the user's real usage split over generic "who is strongest" framing.

## Image Rules That Matter Most

- Images are for传播, not for re-explaining the whole article.
- WeChat cover text should be extremely compressed: no more than 4 Chinese characters by default, and it should capture the article's core judgment as precisely as possible.
- One image should carry one central judgment.
- Prefer the article's real center of gravity, not a local example detail.
- If an image sentence only restates a case detail, it is usually the wrong sentence.
- A strong image should feel worth saving or forwarding on its own.
- Good image copy should give the reader a reusable hook they may want to revisit later, not just explain what happened in one anecdote.
- Text on images should stay sparse and decisive.
- Prefer plain, instantly understood wording on images; avoid internal jargon like “高摩擦任务” unless the reader can understand it at a glance.
- If the reader would need the surrounding article context to understand the image sentence, the image copy is probably too weak.
- When the article's center of gravity is an action path or direction, the image should not stop at a half-judgment reminder; it should carry both the problem and the direction.
- Place each image near the paragraph block it is actually reinforcing; do not insert an abstract image while the local text is still on a concrete example.
- Do not cluster images together by default; distribute them across the article so each image lands on its own semantic beat.
- Default to one unified background tone across article images unless a specific article truly needs an exception.
- Keep image text colors consistent within the same article. Do not introduce a one-off highlight color unless there is a clear, deliberate article-wide color rule.
- When fixing rendering issues in an image, preserve the repository's established house style. Do not switch to a temporary font or visual system that makes the new image feel unrelated to the rest of the account.
- Image line spacing must be judged visually, not mechanically. When adjacent lines use different font sizes, adjust spacing by perceived visual gap rather than equal numeric offsets.
- Watermark must be `@Bill的精神时光屋`.
- Watermark should stay near the bottom-right corner while preserving a safe margin from borders and content.
- Default to one consistent watermark position across same-style images; only move it when needed to avoid borders or content.

## Distribution Heuristics

- The goal comes before the tactic.
- Group triggering, title design, and share hooks are distribution methods, not the strategic objective.
- First clarify the target recognition position, then use content and distribution to strengthen it.
- Do not think only about writing; think about trigger design.
- For external distribution, especially AI groups, optimize for three reader actions: follow, save, and forward.
- Group distribution should start from audience psychology, not from the author's desire to express a view.
- The most common triggers in AI groups are:
  - fear of falling behind
  - desire for immediate efficiency gain
  - desire to become an early adopter inside their circle
  - desire to get low-cost ready-made answers instead of trial-and-error
- Content sent into groups should usually satisfy at least two of the following:
  - “this is directly about me”
  - “this is worth saving for later”
  - “I should follow this person because more of this is coming”
- Prefer messages and titles that are reader-triggering rather than author-expressive.
- A good group-distribution asset is not just an article link; it is usually:
  - one sharp judgment
  - one shareable image
  - one line that signals this is part of an ongoing series

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
