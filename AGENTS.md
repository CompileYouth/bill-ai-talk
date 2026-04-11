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
- When preparing commits, group by change type first, then split by day within that type.
- Do not batch multiple article days into one content commit unless the user explicitly asks for a bulk commit.
- Default article drafting flow is a two-agent loop:
  - spawn `bill-ai-talk-writer` to draft or revise the article
  - writer must return the full article text; on revision rounds it must also map changes back to reviewer suggestions
  - spawn `bill-ai-talk-reviewer` for read-only review
  - reviewer must not modify files; it returns `Blocking issues`, `Suggestions`, and `recommended_action`
  - if issues remain, send the numbered list back to writer and iterate on the same draft
  - stop when reviewer reports `no_issue`, or when the loop exceeds 5 rounds
  - if the loop exceeds 5 rounds, stop and surface the main blocker plus whether the next step should be `rewrite` or `change topic`

## Two-Agent Execution

When the user asks to write or rewrite an article, run the loop below instead of drafting directly in the main thread.

1. Prepare the task for `bill-ai-talk-writer`
   - Include the article date, topic, current goal, and any user constraints for tone, length, title direction, or images.
   - Point writer at the current sources of truth: `AGENTS.md`, `publishing-tracker.md`, and the writing/publishing references.
   - If this is a revision, also include the latest reviewer feedback and tell writer to revise the same draft instead of opening a parallel version.

2. Run `bill-ai-talk-writer`
   - Writer is responsible for the article draft itself.
   - Writer should update the relevant article file under `articles/`, sync `article-state/`, update `publishing-tracker.md`, and add or update image assets when needed.
   - Writer must return:
     - the chosen title and any alternate title candidates when relevant
     - the full current article text
     - the list of files changed
     - on revision rounds, a point-by-point response to reviewer suggestions

3. Run `bill-ai-talk-reviewer`
   - Reviewer is read-only and must not modify files.
   - Reviewer should inspect the original task, the current draft, the current packaging state, and the writer report.
   - Reviewer must return:
     - `recommended_action: no_issue | revise | rewrite`
     - `Blocking issues`
     - `Suggestions`
   - Reviewer suggestions must be concrete and numbered `1, 2, 3`.

4. If reviewer returns `revise` or `rewrite`
   - Send the numbered feedback back to writer.
   - Writer must revise the same draft, not fork a parallel draft.
   - Writer must reply point by point: fixed, partially fixed, or intentionally not applied, with a reason.
   - Then send the updated draft back to reviewer.

5. Stop conditions
   - Stop when reviewer returns `recommended_action: no_issue`.
   - If the loop exceeds 5 rounds, stop instead of patching forever.
   - When stopping after 5 rounds, surface:
     - the main blocker
     - whether the next step should be `rewrite` or `change topic`

6. Main-thread responsibility
   - The main agent is responsible for orchestrating this loop, checking that article path/state/tracker stay in sync, and reporting the final result to the user.
   - Do not skip the reviewer stage for article work unless the user explicitly asks to bypass it.
