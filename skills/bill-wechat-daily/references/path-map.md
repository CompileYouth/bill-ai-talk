# Path Map

Core workspace:

- `/Users/bytedance/Documents/my-projects/bill-ai-talk`

Important directories:

- `articles/`: final Markdown articles only
- `assets/`: image assets grouped by article asset stem
- `preview/`: generated local HTML preview pages
- `scripts/`: image renderers and preview-page builder
- `publishing-tracker.md`: publish schedule and post-performance tracking

Important repo rules:

- `articles/*.md` uses `YYYY-MM-DD：中文标题.md` and is final publish-ready copy
- each article should also have a matching `preview/*.html`
- article date prefixes represent publish dates, not creation dates
- image upload copies go to `~/Downloads`
- preview HTML is tracked in git with the article
- if a rule is stable, update the skill instead of leaving it only in one article

Useful scripts:

- `/Users/bytedance/Documents/my-projects/bill-ai-talk/scripts/build_wechat_page.py`
- `/Users/bytedance/Documents/my-projects/bill-ai-talk/scripts/shift_publish_dates.py`
