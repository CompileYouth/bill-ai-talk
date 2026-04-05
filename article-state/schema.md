# Article State Schema

Each article state file lives under `article-state/articles/` and is keyed by a stable `article_id`.
For readability, the filename also carries a date prefix:

- scheduled article: `YYYY-MM-DD__article_id.json`
- unscheduled article: `未排期__article_id.json`

Example shape:

```json
{
  "article_file": "2026-04/2026-04-05：AI 会做还不够，还得限制 AI 做什么.md",
  "article": {
    "title": "AI 会做还不够，还得限制 AI 做什么",
    "tldr": "一句可直接复用的摘要",
    "core_judgment": "这篇文章真正要读者记住的判断",
    "publish_date": "2026-04-05"
  },
  "strategy": {
    "article_type": "short_judgment",
    "topic_tags": ["agent", "workflow"],
    "target_reader": "ai_builders_and_engineers",
    "distribution_hook": "counterintuitive_reframe",
    "packaging_hypothesis": "为什么这个标题和封面可能有效"
  },
  "packaging": {
    "cover": {
      "text": "限制",
      "background": "#a023c8",
      "confirmed_at": "2026-04-05T11:22:57"
    },
    "images": []
  },
  "outcomes": {},
  "review": {
    "human_note": "",
    "what_worked": "",
    "what_failed": "",
    "next_adjustment": ""
  }
}
```

Field meanings:

- `article_file`: relative path under `articles/`
- `article`: content-side fields that can mostly be auto-filled from the article itself
- `strategy`: agent-inferred fields about audience, angle, and packaging intent
- `packaging.cover`: confirmed WeChat cover decision
- `packaging.images`: durable metadata for article images if needed later
- `outcomes`: publish metrics and reader feedback
- `review`: low-input retrospective output; only the human note should regularly need manual help

Rules:

- article body content stays in `articles/`, not here
- default to auto-filling content and strategy fields before asking the user
- keep manual input minimal: metrics plus one short subjective note should be enough to update review state
- state files should be stable enough for both humans and agents to read directly
