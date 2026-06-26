---
name: tencent-music-monitor
description: >
  Monitor and analyze recent events related to Tencent Music Entertainment Group (腾讯音乐娱乐集团, TME), storing structured impact analyses in the `events/tencent-music/` directory of the current project. Use this skill whenever the user asks to track, monitor, analyze, or research Tencent Music news, events, announcements, market movements, or any activity involving 腾讯音乐 — even if they don't use the word "monitor". Triggered by: "分析腾讯音乐最新事件", "帮我看看腾讯音乐最近有什么新闻", "tencent music news analysis", "腾讯音乐动态", "追踪TME事件", "search tencent music events", or any request involving Tencent Music intelligence gathering.
---

# 腾讯音乐娱乐集团事件监控与分析 Skill

This skill searches for recent events related to Tencent Music Entertainment Group (TME), analyzes the impact of each event on the company, stores results in structured markdown files, and deduplicates to avoid re-analyzing events already on record.

## Workflow Overview

1. **Search** for recent Tencent Music events using web search
2. **Deduplicate** against already-analyzed events
3. **Analyze** each new event's impact
4. **Store** results in `events/tencent-music/events/` as markdown files
5. **Update** the index and deduplication registry

---

## Step 1 — Set up directory structure

Ensure these paths exist in the current working directory:

```
events/tencent-music/
├── index.md              ← Running list of all analyzed events
├── analyzed_events.json  ← Deduplication registry
└── events/               ← One .md file per analyzed event
```

Create them if they don't exist. For `analyzed_events.json`, initialize as:
```json
{"events": []}
```

For `index.md`, initialize with a header:
```markdown
# 腾讯音乐娱乐集团事件分析索引

| 日期 | 标题 | 影响评级 | 文件 |
|------|------|----------|------|
```

---

## Step 2 — Search for recent events

Use **multiple search queries** to cast a wide net. Suggested queries (run 3–5 of these):

- `腾讯音乐 最新新闻 site:reuters.com OR site:bloomberg.com OR site:ft.com`
- `Tencent Music Entertainment TME latest news 2025 2026`
- `腾讯音乐 财报 订阅用户 版权 近期`
- `TME earnings announcement subscription growth licensing`
- `腾讯音乐 QQ音乐 酷狗 酷我 全民K歌 最新`
- `TME OR "腾讯音乐" OR "Tencent Music" news`

Collect all results. For each result, record:
- **title** (标题)
- **date** (日期, ISO format if available, else approximate)
- **source** (来源)
- **url** (链接)
- **summary** (摘要, 1–2 sentences from the search result)

---

## Step 3 — Deduplicate

Read `events/tencent-music/analyzed_events.json`. For each collected event:

- Check if the URL already appears in `analyzed_events.json["events"][*]["url"]`
- Also check for near-duplicate titles: if the title is >80% similar to an existing title (same event, different source), skip it
- Only proceed with **genuinely new** events not yet in the registry

If all events are already analyzed, report this to the user and stop.

---

## Step 4 — Analyze each new event

For each new event, produce a structured impact analysis. Think carefully about:

- **What happened**: A factual summary of the event (2–4 sentences)
- **Direct impact**: Immediate effect on TME's business, products, or financials
- **Strategic implications**: Longer-term consequences for TME's market position, partnerships, or competitive standing
- **Investor angle**: How this might affect TME stock price (HKEx: 1698.HK), earnings outlook, or investor sentiment
- **Risk / Opportunity**: Is this net positive, negative, or neutral for Tencent Music? Why?
- **Impact rating**: Choose one: 🔴 High Negative / 🟡 Neutral / 🟢 High Positive / ⚪ Low Impact

Consider Tencent Music's current strategic priorities when analyzing:
- Paid subscription growth (付费会员) for QQ音乐, 酷狗音乐, 酷我音乐
- Live streaming and online karaoke (全民K歌, 酷狗直播)
- AI music creation and recommendation features (AI音乐)
- Music content licensing and exclusive rights (版权)
- Long-form audio and podcast expansion (长音频)
- Competition with NetEase Cloud Music (网易云音乐)
- International expansion and partnerships

---

## Step 5 — Write event files

For each analyzed event, create a file at:
```
events/tencent-music/events/YYYY-MM-DD_<slug>.md
```

Where `<slug>` is a short kebab-case English title (e.g., `q1-earnings-beat`, `ai-music-launch`, `subscription-milestone`).

Use this exact template:

```markdown
# [Event Title in Chinese or English]

**日期 / Date:** YYYY-MM-DD  
**来源 / Source:** [Source Name]([URL])  
**影响评级 / Impact Rating:** 🟢 High Positive *(or whichever applies)*

---

## 事件摘要 / Summary

[2–4 sentence factual description of what happened]

---

## 直接影响 / Direct Impact

[Immediate business/financial/operational effects on Tencent Music]

---

## 战略意义 / Strategic Implications

[Longer-term competitive or strategic consequences]

---

## 投资者视角 / Investor Angle

[How this may affect HKEx: 1698.HK stock, earnings, or investor perception]

---

## 风险与机遇 / Risk & Opportunity

**Overall:** [Positive / Negative / Neutral]  
[1–3 sentences explaining the net assessment]
```

---

## Step 6 — Update the registry and index

**Update `events/tencent-music/analyzed_events.json`** — append each new event:

```json
{
  "events": [
    {
      "url": "https://...",
      "title": "Event title",
      "date": "YYYY-MM-DD",
      "file": "events/tencent-music/events/YYYY-MM-DD_slug.md",
      "impact_rating": "High Positive",
      "analyzed_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}
```

**Update `events/tencent-music/index.md`** — add a row to the table for each new event:

```markdown
| YYYY-MM-DD | [Event title](events/YYYY-MM-DD_slug.md) | 🟢 High Positive | [link](events/YYYY-MM-DD_slug.md) |
```

---

## Step 7 — Report to the user

After completing all analyses, provide a concise summary:

```
## 本次监控结果 / Monitoring Results

发现 X 个新事件，已跳过 Y 个重复事件。

### 新分析事件：
1. **[事件标题]** — [Impact Rating] — `events/tencent-music/events/...md`
2. ...

所有分析已保存至 `events/tencent-music/` 目录。
```

---

## Step 8 — Send Feishu notification (if configured)

After reporting to the user, send a Feishu notification using the **feishu-notify** skill. Run:

```bash
python3 scripts/feishu_notify.py \
  --title "🎵 腾讯音乐事件监控报告" \
  --item "发现 X 个新事件，跳过 Y 个重复" \
  --entry "event:[影响评级emoji] [事件标题1]" \
  --entry "detail:[核心事实或业务影响，1句话]" \
  --entry "detail:1698.HK 影响: [股价/估值/投资者关注点简述]" \
  --entry "event:[影响评级emoji] [事件标题2]" \
  --entry "detail:[核心事实]" \
  --entry "detail:1698.HK 影响: [简述]" \
  --footer "📁 详情: events/tencent-music/"
```

- For each event: always include 2 `--entry detail:` lines — one for the core business fact, one for the 1698.HK investor angle
- If no new events found: `--item "✅ 今日无新事件（已跳过 Y 个重复）"` (no `--entry` needed)
- If `scripts/feishu_notify.py` doesn't exist or `.env` is not configured, skip silently — don't fail the task
- See the **feishu-notify** skill for setup instructions

---

## Important notes

- **Language**: Write event files in bilingual format (Chinese + English headers as shown in template). Analysis content can be in Chinese for Chinese-focused projects.
- **Date handling**: If exact date is unknown, use the search result's publication date. If unavailable, use today's date with a note.
- **Source credibility**: Prefer authoritative sources (Reuters, Bloomberg, FT, official TME IR page, 新浪财经, 东方财富, 雪球). Flag if a source is low-credibility.
- **Scope**: Focus on events with material relevance — earnings releases, subscription milestones, licensing agreements, regulatory actions, product launches, major competitive moves. Avoid minor social media posts or obvious clickbait.
- **Deduplication priority**: When in doubt, skip. It is better to miss a duplicate than to re-analyze the same event twice.
