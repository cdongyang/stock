---
name: memory-flash-monitor
description: >
  Monitor and analyze recent events related to the global memory and flash storage industry (内存/闪存), including NAND flash, DRAM, HBM, and key players such as Samsung, SK Hynix, Micron, Kioxia, YMTC (长江存储), and CXMT (合肥长鑫). Stores structured impact analyses in the `events/memory-flash/` directory of the current project. Use this skill whenever the user asks to track, monitor, analyze, or research memory chip news, flash storage events, DRAM/NAND price trends, supply-demand dynamics, or any activity involving 内存、闪存、存储芯片 — even if they don't use the word "monitor". Triggered by: "分析内存闪存最新事件", "帮我看看存储芯片近期动态", "NAND flash market news", "内存价格走势", "追踪闪存行业", "Micron SK Hynix Samsung memory news", "长江存储 合肥长鑫 动态", or any request involving memory/storage industry intelligence.
---

# 内存/闪存行业事件监控与分析 Skill

This skill searches for recent events related to the global memory and flash storage industry (NAND、DRAM、HBM及相关企业), analyzes the impact of each event on the industry and key players, stores results in structured markdown files, and deduplicates to avoid re-analyzing events already on record.

## Workflow Overview

1. **Search** for recent memory/flash industry events using web search
2. **Deduplicate** against already-analyzed events
3. **Analyze** each new event's impact
4. **Store** results in `events/memory-flash/events/` as markdown files
5. **Update** the index and deduplication registry

---

## Step 1 — Set up directory structure

Ensure these paths exist in the current working directory:

```
events/memory-flash/
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
# 内存/闪存行业事件分析索引

| 日期 | 标题 | 影响评级 | 文件 |
|------|------|----------|------|
```

---

## Step 2 — Search for recent events

Use **multiple search queries** to cast a wide net. Suggested queries (run 4–6 of these):

- `NAND flash DRAM memory market news 2025 2026`
- `内存 闪存 价格 供需 最新动态 2026`
- `Micron Samsung "SK Hynix" memory earnings results`
- `长江存储 合肥长鑫 YMTC CXMT 最新`
- `HBM high bandwidth memory AI chips supply 2026`
- `NAND flash price trend oversupply shortage 2026`
- `US export controls memory chips China ban`
- `闪存 NAND 涨价 降价 三星 海力士 美光 2026`

Collect all results. For each result, record:
- **title** (标题)
- **date** (日期, ISO format if available, else approximate)
- **source** (来源)
- **url** (链接)
- **summary** (摘要, 1–2 sentences from the search result)

---

## Step 3 — Deduplicate

Read `events/memory-flash/analyzed_events.json`. For each collected event:

- Check if the URL already appears in `analyzed_events.json["events"][*]["url"]`
- Also check for near-duplicate titles: if the title is >80% similar to an existing title (same event, different source), skip it
- Only proceed with **genuinely new** events not yet in the registry

If all events are already analyzed, report this to the user and stop.

---

## Step 4 — Analyze each new event

For each new event, produce a structured impact analysis. Think carefully about:

- **What happened**: A factual summary of the event (2–4 sentences)
- **Direct impact**: Immediate effect on memory/flash supply, pricing, or specific company financials
- **Strategic implications**: Longer-term consequences for industry structure, competitive dynamics, or China's memory self-sufficiency goals
- **Investor angle**: How this might affect key stocks — Micron (MU), Samsung Electronics (005930.KS), SK Hynix (000660.KS), Western Digital (WDC), Kioxia — and downstream consumers (smartphone OEMs, server/AI hardware makers)
- **Risk / Opportunity**: Is this net positive, negative, or neutral for the industry / specific players? Why?
- **Impact rating**: Choose one: 🔴 High Negative / 🟡 Neutral / 🟢 High Positive / ⚪ Low Impact

Consider the industry's current key dynamics when analyzing:
- **Price cycles**: NAND flash and DRAM are highly cyclical — note whether an event signals oversupply (price pressure) or undersupply (price recovery)
- **HBM/AI demand**: High Bandwidth Memory demand from AI accelerators (NVIDIA, AMD) is a major secular driver
- **China supply chain**: YMTC (长江存储) and CXMT (合肥长鑫/睿力集成) are expanding domestic capacity; US export controls create both risk and opportunity
- **Technology nodes**: Transitions to 3D NAND (200+ layers), DDR5, LPDDR5X, and CXL memory affect competitive positioning
- **Key customers**: Apple, Samsung Mobile, major cloud hyperscalers (AWS, Azure, Google), and AI server OEMs
- **Geopolitical risk**: US-China tech tensions, export control expansion, and supply chain diversification

---

## Step 5 — Write event files

For each analyzed event, create a file at:
```
events/memory-flash/events/YYYY-MM-DD_<slug>.md
```

Where `<slug>` is a short kebab-case English title (e.g., `nand-price-recovery`, `micron-earnings-beat`, `ymtc-export-ban`).

Use this exact template:

```markdown
# [Event Title in Chinese or English]

**日期 / Date:** YYYY-MM-DD  
**来源 / Source:** [Source Name]([URL])  
**影响评级 / Impact Rating:** 🟢 High Positive *(or whichever applies)*  
**主要影响方 / Key Players:** [e.g., Samsung, SK Hynix, Micron, YMTC, 全行业]

---

## 事件摘要 / Summary

[2–4 sentence factual description of what happened]

---

## 直接影响 / Direct Impact

[Immediate effects on memory/flash pricing, supply, or specific company operations]

---

## 战略意义 / Strategic Implications

[Longer-term consequences for industry structure, technology roadmap, or geopolitics]

---

## 投资者视角 / Investor Angle

[How this may affect MU / 005930.KS / 000660.KS / WDC and downstream chip consumers]

---

## 风险与机遇 / Risk & Opportunity

**Overall:** [Positive / Negative / Neutral]  
[1–3 sentences explaining the net assessment, noting which players benefit or are hurt]
```

---

## Step 6 — Update the registry and index

**Update `events/memory-flash/analyzed_events.json`** — append each new event:

```json
{
  "events": [
    {
      "url": "https://...",
      "title": "Event title",
      "date": "YYYY-MM-DD",
      "file": "events/memory-flash/events/YYYY-MM-DD_slug.md",
      "impact_rating": "High Positive",
      "analyzed_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}
```

**Update `events/memory-flash/index.md`** — add a row to the table for each new event:

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
1. **[事件标题]** — [Impact Rating] — `events/memory-flash/events/...md`
2. ...

所有分析已保存至 `events/memory-flash/` 目录。
```

---

## Step 8 — Send Feishu notification (if configured)

After reporting to the user, send a Feishu notification using the **feishu-notify** skill. Run:

```bash
python3 scripts/feishu_notify.py \
  --title "💾 内存/闪存行业监控报告" \
  --item "发现 X 个新事件，跳过 Y 个重复" \
  --entry "event:[影响评级emoji] [事件标题1]" \
  --entry "detail:[核心数据点或价格变动，1句话，含量级/幅度]" \
  --entry "detail:受益/承压: [具体公司或品种]" \
  --entry "event:[影响评级emoji] [事件标题2]" \
  --entry "detail:[核心数据点]" \
  --entry "detail:受益/承压: [具体公司或品种]" \
  --footer "📁 详情: ~/stock-analysis/events/memory-flash/"
```

- For each event: always include 2 `--entry detail:` lines — one for the key data point, one for key players affected
- If no new events found: `--item "✅ 今日无新事件（已跳过 Y 个重复）"` (no `--entry` needed)
- If `scripts/feishu_notify.py` doesn't exist or `.env` is not configured, skip silently — don't fail the task
- See the **feishu-notify** skill for setup instructions

---

## Important notes

- **Language**: Write event files in bilingual format (Chinese + English headers as shown in template). Analysis content can be in Chinese for Chinese-focused projects.
- **Date handling**: If exact date is unknown, use the search result's publication date. If unavailable, use today's date with a note.
- **Source credibility**: Prefer authoritative sources (Reuters, Bloomberg, FT, Nikkei, TrendForce, DRAMeXchange, 集微网, 新浪财经, 东方财富, official company IR pages). Flag if a source is low-credibility.
- **Scope**: Focus on events with material relevance — earnings releases, price inflection points, capacity expansion/cuts, technology breakthroughs, export control actions, major customer wins/losses, M&A. Avoid minor analyst notes or speculative rumors.
- **Deduplication priority**: When in doubt, skip. It is better to miss a duplicate than to re-analyze the same event twice.
- **Price context**: When covering NAND/DRAM pricing events, note the direction (涨价/降价), approximate magnitude if available, and which product segments are affected (eMMC, UFS, DDR4/5, LPDDR5, enterprise SSD, etc.).
