# Feedback Playbook

Use `article-state/` to store durable post-publish feedback that the writing agent can reuse later.

Principle:

- auto-fill anything that can be extracted or inferred
- only ask the human for information that materially changes the next writing decision

## Outcomes

Recommended outcome fields:

- `outcomes.reads`
- `outcomes.likes`
- `outcomes.watches`
- `outcomes.shares`
- `outcomes.reader_feedback`
- `outcomes.notes`

## Review

Recommended review fields:

- `review.what_worked`
- `review.what_failed`
- `review.next_adjustment`
- `review.distribution_takeaway`
- `review.human_note`

## Rule Of Thumb

- `publishing-tracker.md` is the human-readable overview.
- `article-state/` is the machine- and agent-readable feedback layer.
- If a later writing or packaging decision should be informed by this article's performance, store that reasoning in the article state file.
- The minimal human input should usually be: a few metrics and one short subjective note.
