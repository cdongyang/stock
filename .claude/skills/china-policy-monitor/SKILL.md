---
name: china-policy-monitor
description: >
  Monitor and analyze recent Chinese government policy changes (中国政策变化), storing structured impact analyses in the `events/china-policy/` directory of the current project. Use this skill whenever the user asks to track, monitor, analyze, or research Chinese policy news, regulatory changes, government announcements, or macro policy shifts — even if they don't use the word "monitor". Triggered by: "监控中国最新政策", "帮我看看中国最近有什么政策变化", "china policy analysis", "中国政策动态", "追踪政策变化", "search china policy", "中国监管政策", "国务院政策", "中央政策", or any request involving Chinese government policy intelligence gathering.
---

# 中国政策变化监控与分析 Skill

This skill searches for recent Chinese government policy announcements, regulatory changes, and macro policy shifts, analyzes the market impact of each policy, stores results in structured markdown files, and deduplicates to avoid re-analyzing policies already on record.

## Workflow Overview

1. **Search** for recent Chinese policy changes using web search
2. **Deduplicate** against already-analyzed policies
3. **Analyze** each new policy's market and sector impact
4. **Store** results in `events/china-policy/events/` as markdown files
5. **Update** the index and deduplication registry

---

## Step 1 — Set up directory structure

Ensure these paths exist in the current working directory:

```
events/china-policy/
├── index.md              ← Running list of all analyzed policies
├── analyzed_events.json  ← Deduplication registry
└── events/               ← One .md file per analyzed policy
```

Create them if they don't exist. For `analyzed_events.json`, initialize as:
```json
{"events": []}
```

For `index.md`, initialize with a header:
```markdown
# 中国政策变化分析索引

| 日期 | 政策标题 | 领域 | 影响评级 | 文件 |
|------|----------|------|----------|------|
```

---

## Step 2 — Search for recent policy events

Use **multiple search queries** to cast a wide net. Run 4–6 of these:

- `中国 最新政策 国务院 发改委 2026`
- `China government policy announcement regulation 2026`
- `中国 经济政策 货币政策 财政政策 最新`
- `China tech regulation AI policy financial market 2026`
- `中国 产业政策 制造业 半导体 新能源 政策`
- `China trade policy tariff export control latest`
- `中国 资本市场 证监会 金融监管 新规`
- `China stimulus policy economic support measures`

Policy domains to prioritize (cover at least 3–4 per run):
- **经济/宏观** (Economic/Macro): GDP targets, fiscal stimulus, monetary policy (PBOC)
- **科技监管** (Tech Regulation): AI, data, platform economy, semiconductor policy
- **金融市场** (Financial Markets): Securities regulation (CSRC), capital markets, IPO rules
- **贸易政策** (Trade Policy): Tariffs, export controls, trade negotiations
- **产业政策** (Industrial Policy): Manufacturing, NEV, semiconductor self-sufficiency
- **房地产** (Real Estate): Property market support or tightening measures
- **对外政策** (Foreign/Geopolitical): Policies affecting foreign investment or trade relations

Collect all results. For each result, record:
- **title** (标题)
- **date** (日期, ISO format if available, else approximate)
- **source** (来源)
- **url** (链接)
- **domain** (领域, one of the categories above)
- **summary** (摘要, 1–2 sentences from the search result)

---

## Step 3 — Deduplicate

Read `events/china-policy/analyzed_events.json`. For each collected policy:

- Check if the URL already appears in `analyzed_events.json["events"][*]["url"]`
- Also check for near-duplicate titles: if the title is >80% similar to an existing title (same policy, different source), skip it
- Only proceed with **genuinely new** policies not yet in the registry

If all policies are already analyzed, report this to the user and stop.

---

## Step 4 — Analyze each new policy

For each new policy, produce a structured impact analysis. Think carefully about:

- **What happened**: A factual summary of the policy (2–4 sentences)
- **直接影响 / Direct Impact**: Immediate effect on relevant industries, companies, or markets
- **受影响板块 / Affected Sectors**: Which A-share/H-share/US-listed Chinese stock sectors are most affected (e.g., 科技股、新能源、金融、地产)
- **市场信号 / Market Signal**: Is this policy bullish, bearish, or neutral for Chinese equities overall? Why?
- **战略意义 / Strategic Implications**: Longer-term direction this policy signals for China's economic strategy
- **投资者视角 / Investor Angle**: How this might affect Shanghai Composite (上证), CSI 300 (沪深300), Hang Seng Tech (恒生科技), or specific sector ETFs
- **Impact rating**: Choose one: 🔴 High Negative / 🟡 Neutral / 🟢 High Positive / ⚪ Low Impact

---

## Step 5 — Write policy event files

For each analyzed policy, create a file at:
```
events/china-policy/events/YYYY-MM-DD_<slug>.md
```

Where `<slug>` is a short kebab-case English title (e.g., `pboc-rate-cut`, `ai-regulation-update`, `csrc-ipo-reform`).

Use this exact template:

```markdown
# [Policy Title in Chinese or English]

**日期 / Date:** YYYY-MM-DD  
**来源 / Source:** [Source Name](URL)  
**领域 / Domain:** [e.g., 货币政策 / Monetary Policy]  
**影响评级 / Impact Rating:** 🟢 High Positive *(or whichever applies)*

---

## 政策摘要 / Summary

[2–4 sentence factual description of the policy or announcement]

---

## 直接影响 / Direct Impact

[Immediate effects on relevant industries, companies, or financial markets]

---

## 受影响板块 / Affected Sectors

[List the specific stock market sectors and why they are affected — e.g., 新能源汽车板块受益, 科技股承压]

---

## 市场信号 / Market Signal

**整体判断:** [Bullish / Bearish / Neutral for Chinese equities]  
[2–3 sentences explaining the market implications]

---

## 战略意义 / Strategic Implications

[Longer-term direction this policy signals for China's economic or regulatory strategy]

---

## 投资者视角 / Investor Angle

[How this may affect major indices (上证、沪深300、恒生科技) or sector ETFs; specific stocks to watch]

---

## 风险与机遇 / Risk & Opportunity

**Overall:** [Positive / Negative / Neutral]  
[1–3 sentences explaining the net assessment for investors]
```

---

## Step 6 — Update the registry and index

**Update `events/china-policy/analyzed_events.json`** — append each new policy:

```json
{
  "events": [
    {
      "url": "https://...",
      "title": "Policy title",
      "date": "YYYY-MM-DD",
      "domain": "货币政策",
      "file": "events/china-policy/events/YYYY-MM-DD_slug.md",
      "impact_rating": "High Positive",
      "analyzed_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}
```

**Update `events/china-policy/index.md`** — add a row to the table for each new policy:

```markdown
| YYYY-MM-DD | [Policy title](events/YYYY-MM-DD_slug.md) | 货币政策 | 🟢 High Positive | [link](events/YYYY-MM-DD_slug.md) |
```

---

## Step 7 — Report to the user

After completing all analyses, provide a concise summary:

```
## 本次监控结果 / Monitoring Results

发现 X 个新政策，已跳过 Y 个重复。

### 新分析政策：
1. **[政策标题]** — [Domain] — [Impact Rating] — `events/china-policy/events/...md`
2. ...

### 市场整体判断：
[1–2 sentences on the overall policy environment signal for Chinese equities]

所有分析已保存至 `events/china-policy/` 目录。
```

---

## Step 7.5 — Industry impact summary (行业利好/利空分析)

After listing individual policies, synthesize across **all new policies** to produce a cross-policy industry impact table. This is the most actionable output for an investor.

Group industries into three tiers:

**🟢 强烈利好 / Strong Tailwind** — multiple policies converge to benefit this sector, or one policy has direct material impact  
**🟡 结构性利好 / Selective Tailwind** — specific sub-segments benefit, or benefit is indirect/conditional  
**🔴 承压 / Headwind** — one or more policies directly pressure this sector

For each industry entry, state:
- **行业名称** and representative A/H-share tickers
- **触发政策** — which specific policy(ies) drive this assessment (reference the slug or title)
- **核心逻辑** — one sentence on why: what mechanism links the policy to this industry's outlook

Format as a structured table in the user-facing report:

```
## 行业影响总览 / Industry Impact Summary

### 🟢 强烈利好
| 行业 | 代表标的 | 触发政策 | 核心逻辑 |
|------|----------|----------|----------|
| 半导体/集成电路 | 中芯国际、北方华创 | IC税收优惠 + 进口替代 | 税负降低 + 贸易战加速国产替代需求 |
| ... | | | |

### 🟡 结构性利好
| 行业 | 代表标的 | 触发政策 | 核心逻辑 |
|------|----------|----------|----------|
| ... | | | |

### 🔴 承压行业
| 行业 | 代表标的 | 触发政策 | 核心逻辑 |
|------|----------|----------|----------|
| ... | | | |
```

This table must be generated every run — it's the primary output investors use to make allocation decisions.

---

## Step 8 — Send Feishu notification (if configured)

After reporting to the user, send a **detailed** Feishu notification that covers both the policy list and the industry impact summary. Structure the `--item` arguments in three sections separated by divider lines (use `────────────────────` as a divider item):

```bash
python3 scripts/feishu_notify.py \
  --title "📋 中国政策变化监控报告" \
  --item "发现 X 个新政策，跳过 Y 个重复" \
  --item "────────────────────" \
  --item "📌 政策速览" \
  --item "🔴 [政策标题1]（贸易政策）" \
  --item "🟢 [政策标题2]（资本市场）" \
  --item "🟡 [政策标题3]（科技监管）" \
  --item "────────────────────" \
  --item "📊 行业影响" \
  --item "🟢 强烈利好：[行业A]（[1句逻辑]）" \
  --item "🟢 强烈利好：[行业B]（[1句逻辑]）" \
  --item "🟡 结构性利好：[行业C]（[1句逻辑]）" \
  --item "🔴 承压：[行业D]（[1句逻辑]）" \
  --item "────────────────────" \
  --item "💡 市场整体判断：[1句话结论]" \
  --footer "📁 详情: ~/stock-analysis/events/china-policy/"
```

Rules:
- Include **every** new policy in the 政策速览 section with its emoji rating
- Include **every** industry tier entry from Step 7.5 in the 行业影响 section — one `--item` per industry, format: `[emoji] [强烈利好/结构性利好/承压]：[行业名]（[核心逻辑一句话]）`
- The 市场整体判断 should be a single punchy sentence summarizing the net signal
- If no new policies found: replace all sections with `--item "✅ 今日无新政策（已跳过 Y 个重复）"`
- If `scripts/feishu_notify.py` doesn't exist or `.env` is not configured, skip silently — don't fail the task
- See the **feishu-notify** skill for setup instructions

---

## Important notes

- **Language**: Write policy files in bilingual format (Chinese + English headers as shown in template). Analysis content can be in Chinese for Chinese-focused projects.
- **Date handling**: If exact date is unknown, use the search result's publication date. If unavailable, use today's date with a note.
- **Source credibility**: Prefer authoritative sources (Xinhua/新华社, People's Daily/人民日报, NDRC/发改委, PBOC/央行, CSRC/证监会, Reuters, Bloomberg, FT, 财联社, 第一财经). Flag if a source is low-credibility.
- **Scope**: Focus on policies with material market relevance — interest rate changes, major regulatory overhauls, industrial subsidies, capital market reforms, significant tariff changes. Avoid minor administrative notices or obvious non-market-moving items.
- **Deduplication priority**: When in doubt, skip. It is better to miss a duplicate than to re-analyze the same policy twice.
- **Market focus**: This skill is designed for investors tracking Chinese equities (A-shares, H-shares, ADRs). Always connect policy analysis to market implications.
