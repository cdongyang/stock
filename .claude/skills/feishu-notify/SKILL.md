---
name: feishu-notify
description: >
  Send a structured notification to a user or group via the Feishu (飞书) App API. Use this skill whenever any monitoring, analysis, or scheduled task needs to push results to Feishu — including but not limited to stock monitoring, event analysis, CI/CD alerts, or any workflow that produces a summary for the user. Triggered when another skill's workflow reaches a "notify" or "report" step, or when the user says anything like "发飞书通知", "send feishu message", "通知我", "推送结果到飞书", or asks to set up Feishu alerts for any task.
---

# 飞书应用通知 Skill

Send structured messages via the Feishu Open Platform App API. This skill is designed to be called by other skills at the end of their workflow.

## Prerequisites

### 1. Config (`.env` in project root)

```
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_RECEIVE_ID=ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_RECEIVE_ID_TYPE=open_id
```

`FEISHU_RECEIVE_ID_TYPE` options: `open_id` (default, send to individual), `chat_id` (send to group), `user_id`, `email`.

### 2. Script

The project must have `scripts/feishu_notify.py`. If it doesn't exist, copy it from this skill:

```bash
cp <skill-path>/scripts/feishu_notify.py <project-root>/scripts/feishu_notify.py
```

## How to call from another skill

At the end of your skill's workflow, invoke:

```bash
python3 scripts/feishu_notify.py \
  --title "📊 报告标题" \
  --item "🟢 事件一" \
  --item "🔴 事件二" \
  --footer "📁 详情路径或说明"
```

Or from Python:

```python
from scripts.feishu_notify import send_notification
send_notification(
    title="📊 报告标题",
    items=["🟢 事件一", "🔴 事件二"],
    footer="📁 详情路径",
)
```

## Message format

The notification will be rendered in Feishu as a rich-text post:

```
📊 报告标题
────────────────────
🕐 2026-04-09 08:00
🟢 事件一
🔴 事件二
────────────────────
📁 详情路径
```

## Error handling

- If config is missing, log a warning and skip silently (don't fail the parent skill)
- If the API call fails, log the error but do not raise — the parent skill's output should still be saved

## Troubleshooting

| 问题 | 原因 | 解决 |
|------|------|------|
| `app not authorized` | 应用未开通消息权限 | 飞书开放平台 → 应用 → 权限管理 → 开通 `im:message:send_as_bot` |
| `invalid receive_id` | open_id 填错 | 开放平台接口调试工具重新获取 |
| `tenant_access_token` 失败 | App ID/Secret 有误 | 核对凭证与基础信息页面 |
