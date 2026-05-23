---
name: nuscale-monitor
description: >
  Monitor and analyze recent events related to NuScale Power (纽斯凯尔电力, NYSE: SMR), storing structured impact analyses in the `events/nuscale/` directory of the current project. Use this skill whenever the user asks to track, monitor, analyze, or research NuScale news, events, announcements, market movements, or any activity involving NuScale small modular reactors — even if they don't use the word "monitor". Triggered by: "分析NuScale最新事件", "NuScale news analysis", "SMR stock news", "纽斯凯尔动态", "追踪NuScale", "small modular reactor SMR news", or any request involving NuScale intelligence gathering.
---

# NuScale Power 事件监控与分析 Skill

This skill searches for recent events related to NuScale Power Corporation (NYSE: SMR), analyzes the impact of each event on the company, stores results in structured markdown files, and deduplicates to avoid re-analyzing events already on record.

NuScale Power is a small modular reactor (SMR) company and the first to receive NRC design approval for its VOYGR SMR technology. The full knowledge base for NuScale is in @NuScale-power.md — use it as the primary reference for all impact assessments.

---

## Step 1 — Set up directory structure

Ensure these paths exist in the current working directory:

```
events/nuscale/
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
# NuScale Power 事件分析索引

| 日期 | 标题 | 影响评级 | 文件 |
|------|------|----------|------|
```

---

## Step 2 — Search for recent events

Use **multiple search queries** to cast a wide net. Run 3–5 of these:

- `NuScale Power SMR stock news latest 2026`
- `NuScale VOYGR reactor contract customer 2026`
- `NuScale Power NRC license COL update`
- `NuScale international project Romania Poland update 2026`
- `"NuScale" site:reuters.com OR site:bloomberg.com OR site:ft.com`
- `NuScale DOE funding contract nuclear 2026`

Collect all results. For each result, record:
- **title** (标题)
- **date** (日期, ISO format if available, else approximate)
- **source** (来源)
- **url** (链接)
- **summary** (摘要, 1–2 sentences from the search result)

---

## Step 3 — Deduplicate

Read `events/nuscale/analyzed_events.json`. For each collected event:

- Check if the URL already appears in `analyzed_events.json["events"][*]["url"]`
- Also check for near-duplicate titles: if the title is >80% similar to an existing title, skip it
- Only proceed with **genuinely new** events not yet in the registry

If all events are already analyzed, report this and stop.

---

## Step 4 — Analyze each new event

For each new event, produce a structured impact analysis:

- **What happened**: A factual summary (2–4 sentences)
- **Direct impact**: Immediate effect on NuScale's project pipeline, regulatory progress, or financials
- **Strategic implications**: Longer-term consequences for NuScale's path to first commercial deployment
- **Investor angle**: How this might affect NYSE: SMR stock price, sentiment, or valuation
- **Risk / Opportunity**: Net positive, negative, or neutral? Why?
- **Impact rating**: 🔴 High Negative / 🟡 Neutral / 🟢 High Positive / ⚪ Low Impact

Key dimensions to assess for every event:
- **项目进展**: 新增客户、LOI、MOU、EPC合同是最高优先级正面催化剂
- **国际项目**: 罗马尼亚（RoPower）、波兰、约旦等项目里程碑
- **NRC/监管**: COL申请进展、监管政策变化
- **融资**: DOE拨款、私募融资、股权融资（注意稀释风险）
- **现金消耗**: 季报中的现金余量和 burn rate 是生存能力指标
- **竞品影响**: Oklo、TerraPower 等重大进展是否挤压 NuScale 的叙事空间

---

## Step 5 — Write event files

For each analyzed event, create a file at:
```
events/nuscale/events/YYYY-MM-DD_<slug>.md
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

[Immediate effects on NuScale's project pipeline, regulatory progress, or financials]

---

## 战略意义 / Strategic Implications

[Longer-term consequences for first commercial deployment timeline and competitive position]

---

## 投资者视角 / Investor Angle

[How this may affect NYSE: SMR stock price, valuation, or investor sentiment]

---

## 风险与机遇 / Risk & Opportunity

**Overall:** [Positive / Negative / Neutral]  
[1–3 sentences on net assessment]
```

---

## Step 6 — Update the registry and index

**Update `events/nuscale/analyzed_events.json`:**

```json
{
  "events": [
    {
      "url": "https://...",
      "title": "Event title",
      "date": "YYYY-MM-DD",
      "file": "events/nuscale/events/YYYY-MM-DD_slug.md",
      "impact_rating": "High Positive",
      "analyzed_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}
```

**Update `events/nuscale/index.md`:**

```markdown
| YYYY-MM-DD | [Event title](events/YYYY-MM-DD_slug.md) | 🟢 High Positive | [link](events/YYYY-MM-DD_slug.md) |
```

---

## Step 7 — Report to the user

```
## 本次监控结果 / Monitoring Results

发现 X 个新事件，已跳过 Y 个重复事件。

### 新分析事件：
1. **[事件标题]** — [Impact Rating] — `events/nuscale/events/...md`
2. ...

所有分析已保存至 `events/nuscale/` 目录。
```

---

## Step 8 — Send Feishu notification (if configured)

```bash
python3 scripts/feishu_notify.py \
  --title "🔬 NuScale Power (SMR) 事件监控报告" \
  --item "发现 X 个新事件，跳过 Y 个重复" \
  --item "🟢 [事件标题1]" \
  --item "🔴 [事件标题2]" \
  --footer "📁 详情: ~/stock-analysis/events/nuscale/"
```

- If no new events: `--item "✅ 今日无新事件（已跳过 Y 个重复）"`
- Skip silently if `scripts/feishu_notify.py` or `.env` is missing

---

## Important notes

- **Source credibility**: Prefer Reuters, Bloomberg, FT, NuScale IR (nuscalepower.com/investors), NRC.gov, DOE.gov, World Nuclear News (WNN). Flag low-credibility sources.
- **CFPP cancellation context**: NuScale's first commercial project (UAMPS/CFPP) was cancelled in late 2023. Any new project announcements must be assessed against this history — market will scrutinize project viability carefully.
- **Cash runway is critical**: SMR is pre-revenue; monitor cash position and DOE funding milestones. A cash crunch event is an existential risk signal.
- **NRC design cert is the moat**: NuScale's only commercial SMR with NRC design approval — preserve this narrative signal in analysis.
- **Deduplication priority**: When in doubt, skip.
