# Path Map

Core workspace:

- `/Users/bytedance/Documents/my-projects/bill-ai-talk`

Important directories:

- `articles/`: final Markdown articles only
- `assets/`: image assets grouped by article slug
- `preview/`: generated local HTML preview pages
- `scripts/`: image renderers and preview-page builder
- `publishing-tracker.md`: publish schedule and post-performance tracking

Inside each `assets/<date-slug>/` directory:

- generated `.jpg` files
- article-specific `render.swift`

Important repo rules:

- `articles/*.md` is final publish-ready copy
- each article should also have a matching `preview/*.html`
- article date prefixes represent publish dates, not creation dates
- image upload copies go to `~/Downloads`
- preview HTML is tracked in git with the article
- if a rule is stable, update the skill instead of leaving it only in one article

Useful scripts:

- `/Users/bytedance/Documents/my-projects/bill-ai-talk/scripts/build_wechat_page.py`
- `/Users/bytedance/Documents/my-projects/bill-ai-talk/scripts/shift_publish_dates.py`
- `/Users/bytedance/Documents/my-projects/bill-ai-talk/assets/2026-03-16-by-agent-or-for-agent/render.swift`
- `/Users/bytedance/Documents/my-projects/bill-ai-talk/assets/2026-03-17-ai-like-precooked-meals/render.swift`
- `/Users/bytedance/Documents/my-projects/bill-ai-talk/assets/2026-03-18-ai-does-not-equal-profit/render.swift`
- `/Users/bytedance/Documents/my-projects/bill-ai-talk/assets/2026-03-19-why-i-start-daily-again/render.swift`
- `/Users/bytedance/Documents/my-projects/bill-ai-talk/assets/2026-03-20-only-ai-growth-counts/render.swift`
