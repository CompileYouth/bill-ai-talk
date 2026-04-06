# Publishing Rules

## Cover Image

- Cover images default to an ultra-minimal style: text plus solid-color background.
- WeChat cover text should usually be no more than 4 Chinese characters and must capture the article's core judgment.
- Cover candidates should be short judgment-like phrases, not mechanically sliced title or TL;DR fragments.

## Inline Article Images

- Default to two article images; use one only when a second image would be filler.
- Images are for传播, not for re-explaining the whole article.
- Keep image text sparse, decisive, and understandable without full article context.
- Do not repeat the same meaning across multiple article images.
- Let article image count follow information density; if one image is enough, stop at one.
- Image copy should read like a judgment, not like a diary line or流水账.
- Do not split image copy into too many tiny lines; prefer one clear sentence across two or three lines.
- If an image only restates the body without adding a memorable takeaway, do not use it.
- Article images must follow the body's argument order; do not show a judgment in an image before the body has reached that judgment.

## State And Tracking

- `publishing-tracker.md` is the human-readable schedule and metrics overview.
- `article-state/` stores durable packaging decisions, outcomes, and retrospective notes.
- When a user confirms cover text or background, save that decision into `article-state/`.

## Scheduling

- Scheduled article path: `articles/YYYY-MM/YYYY-MM-DD：中文标题.md`
- Unscheduled article path: `articles/未排期：中文标题.md`
- Article date prefixes represent WeChat publish dates, not creation dates.
- When inserting a new article into an earlier slot, shift later publish dates as needed.

## WeChat Backend Defaults

- Author: `编译青春`
- Reward: enabled
- Original: enabled
- Collection: `AI闲谈`
- Scheduled publish time: `08:00`
- Only stop for user input when the Chrome login state has expired and scanning is required.

## Operational Discipline

- Keep routine execution silent unless something fails.
- Copy upload images to `~/Downloads` only when needed.
- When a stable workflow rule changes, update both the live skill under `~/.codex/skills/` and the mirrored repo copy.
- When the user says `提交`, treat it as `commit + push`.
