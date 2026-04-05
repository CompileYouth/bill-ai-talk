# Article State

`article-state/` is the long-lived state layer for this writing agent system.

What belongs here:

- packaging decisions that should survive article reloads
- per-article operational state that the agent should reuse
- post-publish outcomes and retrospective notes

What does not belong here:

- article body content itself
- transient runtime caches
- browser session state

Directory layout:

- `articles/`: one JSON file per article
- `schema.md`: field-level expectations for those JSON files
- `feedback-playbook.md`: how outcomes and retrospective notes should be captured

Source-of-truth boundaries:

- `articles/` remains the source of truth for article body content
- `article-state/` is the source of truth for packaging, outcomes, and review memory
- `.publish/` is runtime-only and should not become long-term memory
