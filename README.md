# Bill AI Talk

这个仓库用来持续沉淀和产出 AI 相关的公众号文章，并逐步演化成一个具备正向反馈链路的写作 agent 系统。

先看 [`AGENTS.md`](/Users/bytedance/Documents/my-projects/bill-ai-talk/AGENTS.md) 了解工作区边界和状态层，再用 skill `$bill-wechat-daily` 执行具体写作与发布流程。

当前默认工作流：

1. 先收集素材
   - 可以是和我在这里的对话整理
   - 也可以是你从别处粘贴过来的原文
2. 使用 `$bill-wechat-daily` 直接生成文章和配图，统一放在 `articles/` 中，本地站点会实时预览
3. 如果文章还没确定发送日期，就先保持“未排期”状态；确定日期后再进入正式排期和公众号发布链路

目录说明：

- `articles/`：正式文章，按月份分组保存；未排期文章直接放在根目录
- `article-state/`：每篇文章的封面、反馈、复盘等长期状态
- `assets/`：文章配图等静态资源
- `heybill`：从 `articles/` 实时渲染的本地预览与复制入口
- `scripts/`：通用工具脚本
- `skills/`：随仓库保存的 Codex skill 镜像
- `publishing-tracker.md`：标题、发送日期与文章数据记录

其中关键入口：

- `/Users/bytedance/.codex/skills/bill-wechat-daily/SKILL.md`：公众号日更 skill
- `skills/bill-wechat-daily/`：用于远程持久化和跨设备同步的 skill 副本
- `AGENTS.md`：仓库级边界、目录职责和规则优先级入口
- `scripts/build_wechat_page.py`：把 Markdown 文章转成可复制到公众号的本地网页
- `scripts/run_heybill.py`：启动 `heyBill` 本地服务，直接读取 `articles/` 并一键复制富文本
- `scripts/shift_publish_dates.py`：当插入新文章时，顺延后续文章的发送日期
- `scripts/publish_pipeline.py`：未排期文章转正式文章并更新排期
- `scripts/publish_candidate.py`：一条命令完成未排期文章排期，并可继续触发公众号发布
- `scripts/wechat_publisher.py`：公众号后台与封面图自动发布辅助脚本
- 每篇文章对应的配图生成模板放在各自的 `assets/<date-slug>/render.swift`

跨设备使用方式：

1. 在新电脑上拉取这个仓库
2. 将 `skills/bill-wechat-daily/` 复制到本机 `~/.codex/skills/bill-wechat-daily/`
3. 之后即可像当前机器一样使用 `$bill-wechat-daily`

当前默认交付：

- `articles/` 中统一保存文章；已排期文章放在 `articles/YYYY-MM/YYYY-MM-DD：标题.md`，未排期文章使用 `articles/未排期：标题.md`
- `assets/` 中保存正文配图和公众号横版封面
- `article-state/` 中保存封面确认、反馈数据和复盘记忆
- 每篇文章默认提供 1 张 `2.35:1` 的公众号封面图
- 每篇文章默认额外复制 3 张上传用图片到本地 `~/Downloads`
- 默认提供一个本地 `heyBill` 服务，用于统一浏览和复制文章
- 本地预览默认从 `articles/` 实时渲染，不再单独保存 `preview/*.html`
- 每篇文章生成后默认做一次“是否具备传播潜力”的 review
- 文章日期默认表示公众号发送日期，而不是创作日期
- 未排期文章确定发送日期后，默认复用 Chrome 默认用户登录态自动配置公众号后台

建议协作方式：

- 你可以直接说一个主题，让我和你一起聊
- 也可以把一段聊天记录或原文贴给我，我来整理
- 后续写作与发布规则优先更新到 `$bill-wechat-daily` 及其 references
- 仓库边界和状态层约定更新到 `AGENTS.md`

如需手动导出单篇 HTML：

```bash
python3 scripts/build_wechat_page.py "articles/2026-03-17：今天的 AI，就像当年的预制菜.md" --output /tmp/article.html
```

本地预览和复制默认从 `articles/` 实时渲染，不再需要为每篇文章单独生成 `preview/*.html`。
