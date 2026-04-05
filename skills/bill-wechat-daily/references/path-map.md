# Path Map

Core workspace:

- `/Users/bytedance/Documents/my-projects/bill-ai-talk`

Important directories:

- `articles/`: all markdown articles; scheduled articles are grouped by month, unscheduled articles stay at the root
- `article-state/`: long-lived per-article packaging, outcome, and review state
- `assets/`: image assets grouped by article asset stem
- `scripts/`: image renderers, publish pipeline, and local preview server
- `publishing-tracker.md`: publish schedule and post-performance tracking

Important repo rules:

- scheduled articles use `articles/YYYY-MM/YYYY-MM-DD：中文标题.md`; unscheduled articles use `articles/未排期：中文标题.md`
- no standalone `preview/*.html` files are required; the local site renders directly from article markdown
- packaging decisions and post-publish feedback should live in `article-state/`, not only in runtime files
- article date prefixes represent publish dates, not creation dates
- image upload copies go to `~/Downloads`
- the local site reads articles directly, so there is no tracked preview artifact per article
- if a rule is stable, update the skill instead of leaving it only in one article

Useful scripts:

- `/Users/bytedance/Documents/my-projects/bill-ai-talk/scripts/build_wechat_page.py`
- `/Users/bytedance/Documents/my-projects/bill-ai-talk/scripts/shift_publish_dates.py`
