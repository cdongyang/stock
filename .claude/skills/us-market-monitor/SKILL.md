---
name: us-market-monitor
description: >
  Monitor and analyze major events that impact US stock markets (影响美股的大型事件), covering macroeconomic data releases (CPI, PCE, non-farm payrolls, GDP, PMI), Federal Reserve decisions and speeches (FOMC, rate changes, hawkish/dovish signals), major policy/legislation/executive orders (tariffs, sanctions, tax reform), geopolitical events (wars, elections, US-China tensions), and financial market turbulence (VIX spikes, bank crises, credit downgrades). Produces sector-level impact analysis — which sectors benefit (受益) and which face headwinds (受压) — and stores structured analyses in the `events/us-market/` directory. Use this skill whenever the user asks to monitor, analyze, or research any event that could move US stocks broadly. Triggered by: "监控美股大型事件", "美股市场有什么大事", "分析美联储决议影响", "CPI数据出来了分析一下", "关税对美股影响", "美股今天为什么大跌", "市场风险事件", "VIX暴涨什么情况", "地缘政治对美股影响", "US market risk events", "macro data impact on stocks", or any request about events moving US equities.
---

# 美股大型事件监控与板块影响分析

This skill searches for recent major events affecting US stock markets, analyzes their sector-level impact, stores results as structured markdown files, and sends a Feishu summary.

## Event Categories to Monitor

| Category | Examples |
|----------|---------|
| 宏观数据 Macro Data | CPI、PCE、非农就业、GDP、PMI、零售销售、耐用品订单 |
| 美联储 Fed Policy | FOMC 决议、加减息、点阵图、鲍威尔讲话、QT/QE |
| 政策/立法 Policy | 行政令、关税、制裁、税改、债务上限、政府停摆 |
| 地缘政治 Geopolitics | 战争升级、大选结果、美中对抗、盟友关系 |
| 金融市场异动 Market Events | VIX 飙升、信用评级下调、银行危机、流动性危机 |

---

## Workflow

### Step 1 — Set up directory structure

Ensure these paths exist:

```
events/us-market/
├── index.md                ← Running list of all analyzed events
├── analyzed_events.json    ← Deduplication registry
└── events/                 ← One .md file per analyzed event
```

Initialize `analyzed_events.json` if missing:
```json
{"events": []}
```

Initialize `index.md` if missing:
```markdown
# 美股大型事件分析索引

| 日期 | 标题 | 方向 | 受益板块 | 受压板块 | 文件 |
|------|------|------|---------|---------|------|
```

---

### Step 2 — Search for recent events

Run **5–8 searches** across all categories. Suggested queries:

**Macro & Fed:**
- `Federal Reserve FOMC interest rate decision 2026`
- `US CPI inflation PCE data latest 2026`
- `US jobs report nonfarm payroll 2026`
- `US GDP growth recession risk 2026`

**Policy & Geopolitics:**
- `US tariffs trade war executive order stock market 2026`
- `US China sanctions policy market impact 2026`
- `geopolitical risk US stocks 2026`

**Market Events:**
- `VIX spike stock market crash volatility 2026`
- `US bank crisis credit downgrade financial stability 2026`
- `S&P 500 Nasdaq market selloff rally 2026`

For each result, record: **title**, **date** (ISO), **source**, **url**, **summary** (1–2 sentences), **category** (from the table above).

---

### Step 3 — Deduplicate

Read `events/us-market/analyzed_events.json`. Skip any event whose URL already appears in the registry, or whose title is >80% similar to an existing one. Only proceed with genuinely new events.

If all events are already analyzed, report this and stop.

---

### Step 4 — Analyze sector impact

For each new event, think through the transmission mechanism carefully:

**Key questions to answer:**
1. What is the direct signal? (hawkish/dovish, growth up/down, risk-on/risk-off, inflationary/deflationary)
2. Which sectors benefit from this signal, and why?
3. Which sectors face headwinds from this signal, and why?
4. Does this change the rate outlook? (Rate-sensitive sectors: REITs, Utilities, Financials react strongly)
5. Does this affect risk appetite? (High-beta growth stocks vs. defensives)
6. Any specific large-cap stocks most directly in the crosshairs?

**Sector reference:**
| Sector | Key Tickers | Sensitivity |
|--------|------------|-------------|
| 科技 Tech | NVDA AAPL MSFT GOOGL META AMZN | Rate-sensitive, high-beta |
| 金融 Financials | JPM BAC GS WFC | Rate-sensitive, credit-sensitive |
| 能源 Energy | XOM CVX OXY COP | Oil price, geopolitics |
| 消费 Consumer Disc. | AMZN TSLA COST MCD | Growth & rate sensitive |
| 必需消费 Staples | WMT PG KO | Defensive, inflation hedge |
| 医疗 Healthcare | UNH LLY JNJ ABBV | Defensive |
| 工业 Industrials | CAT DE BA GE | Trade-sensitive, capex cycle |
| 公用事业 Utilities | NEE DUK SO | Highly rate-sensitive |
| 地产/REITs | AMT PLD EQIX | Highly rate-sensitive |
| 国防 Defense | LMT RTX NOC GD | Geopolitics-sensitive |
| 中概股 CN ADRs | BABA PDD BIDU NIO | US-China policy-sensitive |

**Overall market direction:**
- 🐂 Bullish: event is net positive for risk assets / SPY
- 🐻 Bearish: event is net negative, likely broad selling
- ↔️ Mixed: divergent sector impact, index roughly flat
- ⚪ Low Impact: limited market significance

---

### Step 5 — Write event files

Create: `events/us-market/events/YYYY-MM-DD_<slug>.md`

`<slug>` = short kebab-case English name (e.g., `fomc-rate-hold`, `cpi-beat-hawkish`, `us-china-tariff-escalation`, `vix-spike-bank-stress`)

```markdown
# [Event Title]

**日期 / Date:** YYYY-MM-DD  
**来源 / Source:** [Source Name](URL)  
**类别 / Category:** [Macro Data | Fed Policy | Policy/Legislation | Geopolitics | Market Event]  
**市场方向 / Direction:** 🐂 Bullish *(or 🐻 Bearish / ↔️ Mixed / ⚪ Low Impact)*  
**受益板块 / Benefiting Sectors:** [e.g., 金融、能源]  
**受压板块 / Pressured Sectors:** [e.g., 科技、REITs]

---

## 事件摘要 / Summary

[2–4 sentences: what happened, the key number or decision, and the immediate market reaction if known]

---

## 传导机制 / Transmission Mechanism

[Explain the logic: why does this event move these sectors? E.g., "Higher-than-expected CPI reduces rate cut expectations → bond yields rise → rate-sensitive sectors (REITs, Utilities, long-duration Tech) sell off; bank NIM expands → Financials benefit"]

---

## 板块影响 / Sector Impact

**受益 Benefiting:**
- **[Sector]**: [Why, 1–2 sentences. Key tickers: XXX]

**受压 Pressured:**
- **[Sector]**: [Why, 1–2 sentences. Key tickers: XXX]

**中性/观察 Watch:**
- [Any sector with ambiguous impact or delayed reaction]

---

## 关键数据点 / Key Data

[The specific number, decision, or development — e.g., "CPI +3.2% YoY vs 3.0% expected", "Fed holds at 4.25–4.5%, 2 cuts priced for 2026", "25% tariff on $300B goods effective July 15"]

---

## 风险与机遇 / Risk & Opportunity

**Overall:** [Bullish / Bearish / Mixed]  
[2–3 sentences: net assessment, what to watch next, any second-order effects]
```

---

### Step 6 — Update registry and index

**Append to `events/us-market/analyzed_events.json`:**
```json
{
  "url": "https://...",
  "title": "Event title",
  "date": "YYYY-MM-DD",
  "category": "Fed Policy",
  "direction": "Bearish",
  "benefiting_sectors": ["Financials", "Energy"],
  "pressured_sectors": ["Tech", "REITs"],
  "file": "events/us-market/events/YYYY-MM-DD_slug.md",
  "analyzed_at": "YYYY-MM-DDTHH:MM:SSZ"
}
```

**Append to `events/us-market/index.md`:**
```markdown
| YYYY-MM-DD | [Event title](events/YYYY-MM-DD_slug.md) | 🐻 Bearish | 金融、能源 | 科技、REITs | [link](events/YYYY-MM-DD_slug.md) |
```

---

### Step 7 — Report to user

```
## 本次监控结果

发现 X 个新事件，已跳过 Y 个重复事件。

### 新分析事件：
1. **[标题]** — 🐻 Bearish — 受压: 科技/REITs — `events/us-market/events/...md`
2. ...

所有分析已保存至 `events/us-market/`。
```

---

### Step 8 — Send Feishu notification

```bash
python3 scripts/feishu_notify.py \
  --title "📊 美股大型事件监控报告" \
  --item "发现 X 个新事件，跳过 Y 个重复" \
  --entry "event:[方向emoji] [事件标题]" \
  --entry "detail:[关键数据点，1句话]" \
  --entry "detail:受益: [板块] | 受压: [板块]" \
  --footer "📁 详情: events/us-market/"
```

- Each event: 2 `--entry detail:` lines — key data point + sector summary
- No new events: `--item "✅ 今日无新美股事件"` (no `--entry` needed)
- Skip silently if `scripts/feishu_notify.py` missing or `.env` not configured

---

## Important Notes

- **Focus on market-moving events**: prioritize events that historically cause >1% SPY move. Skip minor analyst notes or speculative rumors.
- **Rate sensitivity is paramount**: the Fed and inflation data are the #1 driver of US equities in the current cycle — always note whether an event is hawkish or dovish and how it shifts rate expectations.
- **Transmission logic matters**: don't just say "Tech falls" — explain why (e.g., duration risk, reduced growth outlook, margin pressure). The analysis is only valuable if the reasoning is clear.
- **Source credibility**: prefer Bloomberg, Reuters, FT, WSJ, CNBC, official Fed/BLS/BEA releases. Flag low-credibility sources.
- **跨板块移交**: if an event has complex multi-sector transmission chains, hand off to `event-impact-estimation` skill for deeper transmission analysis.
- **Deduplication priority**: when in doubt, skip — re-analyzing the same event is worse than missing a near-duplicate.
