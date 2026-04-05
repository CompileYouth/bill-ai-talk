# AGENTS

This workspace exists to run a high-feedback WeChat writing agent for `Bill的精神时光屋`.

## Primary Goal

Use this repository to turn discussions and source material into publishable公众号文章, package them for distribution, capture post-publish feedback, and improve future writing decisions from that feedback.

## Source Of Truth

- `articles/` is the source of truth for article body content.
- `article-state/` is the source of truth for per-article packaging decisions, outcomes, and retrospective notes.
- `skills/bill-wechat-daily/` defines the task workflow and detailed writing/publishing rules.

## Directory Roles

- `assets/`: rendered article images and WeChat cover assets
- `scripts/`: local preview, scheduling, packaging, and publishing helpers
- `publishing-tracker.md`: human-readable schedule and performance overview
- `.publish/`: runtime caches or temporary publish artifacts only, not long-term memory

## Guidance Priority

1. Direct user instructions
2. `AGENTS.md` for workspace boundaries and structural rules
3. `$bill-wechat-daily` for writing and publishing workflow
4. `README.md` for orientation and quickstart

## Working Rules

- Do not create alternate article sources outside `articles/`.
- When a packaging or feedback decision should be revisited later, store it in `article-state/`, not only in chat.
- When a stable workflow rule changes, update the skill and its references instead of scattering duplicate instructions elsewhere.
- Keep runtime noise out of version control.
