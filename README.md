# Bill AI Talk

这个仓库用来持续沉淀和产出 AI 相关的公众号文章。

从现在开始，这个仓库**不再维护本地规则文档**。  
写作规范、配图规则、提交约定、交付流程，统一以 skill `$bill-wechat-daily` 为准。

当前默认工作流：

1. 先收集素材
   - 可以是和我在这里的对话整理
   - 也可以是你从别处粘贴过来的原文
2. 使用 `$bill-wechat-daily` 生成公众号文章、配图和预览页
3. 成稿存入 `articles/`

目录说明：

- `articles/`：正式文章
- `assets/`：文章配图等静态资源
- `preview/`：文章对应的本地网页预览页，和文章一起入库
- `scripts/`：通用工具脚本
- `publishing-tracker.md`：标题、发送日期与文章数据记录

其中关键入口：

- `/Users/bytedance/.codex/skills/bill-wechat-daily/SKILL.md`：公众号日更 skill
- `scripts/build_wechat_page.py`：把 Markdown 文章转成可复制到公众号的本地网页
- `scripts/shift_publish_dates.py`：当插入新文章时，顺延后续文章的发送日期
- 每篇文章对应的配图生成模板放在各自的 `assets/<date-slug>/render.swift`

当前默认交付：

- `articles/` 中保存最终文章
- `assets/` 中保存正文配图和公众号横版封面
- 每篇文章默认提供 1 张 `2.35:1` 的公众号封面图
- 每篇文章默认额外复制 3 张上传用图片到本地 `~/Downloads`
- 每篇文章默认同步生成一个本地网页，并提供复制按钮用于直贴公众号
- `preview/` 下的网页默认和文章一起保存
- 每篇文章生成后默认做一次“是否具备传播潜力”的 review
- 文章日期默认表示公众号发送日期，而不是创作日期

建议协作方式：

- 你可以直接说一个主题，让我和你一起聊
- 也可以把一段聊天记录或原文贴给我，我来整理
- 后续规则变更统一更新到 `$bill-wechat-daily`，不再回写仓库文档

本地网页生成功能：

```bash
python3 scripts/build_wechat_page.py articles/2026-03-17-ai-does-not-equal-profit.md
```

我后续生成文章时，会同步产出 `preview/` 下的网页；需要手动补生时，也可以直接跑上面的命令。
