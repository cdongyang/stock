---
name: oklo-monitor
description: >
  Monitor and analyze recent events related to Oklo Inc. (奥克洛, NYSE: OKLO), storing structured impact analyses in the `events/oklo/` directory of the current project. Use this skill whenever the user asks to track, monitor, analyze, or research Oklo news, events, announcements, market movements, or any activity involving Oklo nuclear microreactors — even if they don't use the word "monitor". Triggered by: "分析Oklo最新事件", "Oklo news analysis", "OKLO stock news", "奥克洛动态", "追踪Oklo", "nuclear microreactor news", or any request involving Oklo intelligence gathering.
---

# Oklo Inc. 事件监控与分析 Skill

This skill searches for recent events related to Oklo Inc. (NYSE: OKLO), analyzes the impact of each event on the company, stores results in structured markdown files, and deduplicates to avoid re-analyzing events already on record.

Oklo is a next-generation nuclear fission company developing compact fast fission power plants (microreactors). The full knowledge base for Oklo is in @Oklo.md — use it as the primary reference for all impact assessments.

---

## Step 1 — Set up directory structure

Ensure these paths exist in the current working directory:

```
events/oklo/
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
# Oklo Inc. 事件分析索引

| 日期 | 标题 | 影响评级 | 文件 |
|------|------|----------|------|
```

---

## Step 2 — Search for recent events

Use **multiple search queries** to cast a wide net. Run 3–5 of these:

- `Oklo Inc OKLO stock news latest 2026`
- `Oklo nuclear microreactor NRC license update 2026`
- `Oklo Aurora powerhouse customer contract data center`
- `OKLO earnings announcement partnership 2026`
- `Oklo Sam Altman nuclear AI energy latest`
- `"Oklo" site:reuters.com OR site:bloomberg.com OR site:ft.com`

Collect all results. For each result, record:
- **title** (标题)
- **date** (日期, ISO format if available, else approximate)
- **source** (来源)
- **url** (链接)
- **summary** (摘要, 1–2 sentences from the search result)

---

## Step 3 — Deduplicate

Read `events/oklo/analyzed_events.json`. For each collected event:

- Check if the URL already appears in `analyzed_events.json["events"][*]["url"]`
- Also check for near-duplicate titles: if the title is >80% similar to an existing title (same event, different source), skip it
- Only proceed with **genuinely new** events not yet in the registry

If all events are already analyzed, report this and stop.

---

## Step 4 — Analyze each new event

For each new event, produce a structured impact analysis:

- **What happened**: A factual summary (2–4 sentences)
- **Direct impact**: Immediate effect on Oklo's business, regulatory progress, or financials
- **Strategic implications**: Longer-term consequences for Oklo's path to commercialization
- **Investor angle**: How this might affect NYSE: OKLO stock price, sentiment, or valuation
- **Risk / Opportunity**: Net positive, negative, or neutral? Why?
- **Impact rating**: 🔴 High Negative / 🟡 Neutral / 🟢 High Positive / ⚪ Low Impact

Key dimensions to assess for every event:
- **NRC进展**: 任何许可证审批更新是最高权重催化剂
- **客户/LOI**: 新增数据中心、政府或工业客户意向书
- **融资**: 新一轮融资、政府补贴（DOE）或股权稀释
- **竞品动态**: NuScale、TerraPower等重大进展是否影响Oklo竞争地位
- **Sam Altman/OpenAI关联**: AI+核能叙事的强化或弱化

---

## Step 5 — Write event files

For each analyzed event, create a file at:
```
events/oklo/events/YYYY-MM-DD_<slug>.md
```

Use this exact template:

```markdown
# [Event Title]

**日期 / Date:** YYYY-MM-DD  
**来源 / Source:** [Source Name](URL)  
**影响评级 / Impact Rating:** 🟢 High Positive *(or whichever applies)*

---

## 事件摘要 / Summary

[2–4 sentence factual description]

---

## 直接影响 / Direct Impact

[Immediate effects on Oklo's regulatory progress, business, or financials]

---

## 战略意义 / Strategic Implications

[Longer-term consequences for commercialization timeline and competitive position]

---

## 投资者视角 / Investor Angle

[How this may affect NYSE: OKLO stock price, valuation, or investor sentiment]

---

## 风险与机遇 / Risk & Opportunity

**Overall:** [Positive / Negative / Neutral]  
[1–3 sentences on net assessment]
```

---

## Step 6 — Update the registry and index

**Update `events/oklo/analyzed_events.json`:**

```json
{
  "events": [
    {
      "url": "https://...",
      "title": "Event title",
      "date": "YYYY-MM-DD",
      "file": "events/oklo/events/YYYY-MM-DD_slug.md",
      "impact_rating": "High Positive",
      "analyzed_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}
```

**Update `events/oklo/index.md`:**

```markdown
| YYYY-MM-DD | [Event title](events/YYYY-MM-DD_slug.md) | 🟢 High Positive | [link](events/YYYY-MM-DD_slug.md) |
```

---

## Step 7 — Report to the user

```
## 本次监控结果 / Monitoring Results

发现 X 个新事件，已跳过 Y 个重复事件。

### 新分析事件：
1. **[事件标题]** — [Impact Rating] — `events/oklo/events/...md`
2. ...

所有分析已保存至 `events/oklo/` 目录。
```

---

## Step 8 — Send Feishu notification (if configured)

```bash
python3 scripts/feishu_notify.py \
  --title "⚛️ Oklo (OKLO) 事件监控报告" \
  --item "发现 X 个新事件，跳过 Y 个重复" \
  --item "🟢 [事件标题1]" \
  --item "🔴 [事件标题2]" \
  --footer "📁 详情: ~/stock-analysis/events/oklo/"
```

- If no new events: `--item "✅ 今日无新事件（已跳过 Y 个重复）"`
- Skip silently if `scripts/feishu_notify.py` or `.env` is missing

---

## Important notes

- **Source credibility**: Prefer Reuters, Bloomberg, FT, Oklo IR (oklo.com/investors), NRC.gov, DOE.gov, Seeking Alpha (institutional analysis only). Flag low-credibility sources.
- **NRC is the critical path**: Any news touching NRC Combined License Application (COLA) or licensing timeline is highest priority regardless of other events.
- **Valuation context**: OKLO is a pre-revenue speculative growth stock; sentiment and narrative shifts can move it ±10–20% on a single day. Weight accordingly.
- **Deduplication priority**: When in doubt, skip.
