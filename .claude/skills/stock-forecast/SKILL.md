---
name: stock-forecast
description: >
  Forecast same-day or next-day stock price movement for Xiaomi Group (小米集团, 01810.HK) and Tencent Music (腾讯音乐, TME/1698.HK) by synthesizing local project event analyses with live market data. Use this skill whenever the user asks about stock price outlook, expected movement, predicted range, or trading signals for Xiaomi or Tencent Music — even casual phrasings like "小米今天会涨吗", "腾讯音乐明天走势怎么样", "帮我预判一下", "今天该不该买小米", or "TME tomorrow forecast". Always use this skill when the user wants a price prediction grounded in the project's accumulated research.
---

# 股价短期走势预测 Skill（小米集团 & 腾讯音乐）

This skill synthesizes three layers of evidence — recent company events, macro policy signals, and live market data — to produce a structured short-term price forecast for Xiaomi (01810.HK) and Tencent Music (TME/1698.HK). The goal is an actionable, well-reasoned estimate, not a guarantee. Always communicate uncertainty honestly.

## Workflow Overview

1. **Load project context** — read recent event files for both companies + policy signals
2. **Fetch live market data** — current price, recent performance, breaking news
3. **Score signals** — weight positive/negative factors by recency and magnitude
4. **Generate forecast** — direction, estimated range, confidence level
5. **Report** — structured output + Feishu notification

---

## Step 1 — Load project context

Read the following files to build the evidence base. You only need the most recent 5–7 events per company, plus the latest policy index.

**Xiaomi:**
- `xiaomi/index.md` — scan for events from the last 14 days, note their impact ratings
- Read the full `.md` files for any events rated 🔴 or 🟢 (skip ⚪ Low Impact)

**Tencent Music:**
- `tencent-music/index.md` — same approach, last 14 days
- Read full files for 🔴 / 🟢 rated events

**China Policy:**
- `china-policy/index.md` — identify policies from the last 7 days that affect either company's sector
- Pay special attention to: 贸易政策 (affects Xiaomi hardware exports), 科技监管 (affects both), 资本市场 (affects both HK listings)

For each company, mentally tally: **net sentiment score** = count(🟢 High Positive) − count(🔴 High Negative) among recent events.

---

## Step 2 — Fetch live market data

Run these web searches to get current market context:

- `小米集团 01810.HK 股价 今日` — current price and today's movement
- `腾讯音乐 1698.HK 股价 今日` — current price and today's movement
- `Hang Seng Index HSI today performance` — market backdrop for HK stocks
- `小米 腾讯音乐 最新消息` (or date-specific) — any breaking news in last 24h not yet in project files

Record:
- **Current price** for each stock
- **Today's % change** so far (if market is open) or yesterday's close
- **HSI / broader market direction** — is the macro environment risk-on or risk-off today?
- **Any new catalyst** not yet captured in local files

---

## Step 3 — Score and synthesize signals

For each company, build a signal matrix. Think about each factor's direction and weight:

| Signal Category | Weight | How to assess |
|----------------|--------|---------------|
| Recent company events (last 7d) | High | Net sentiment from Step 1; recency matters more than older events |
| Recent company events (8–14d) | Medium | Still relevant but fading |
| China policy impact on sector | High | Read china-policy entries; translate sector impact to company impact |
| Broader market / HK index direction | Medium | Risk-off days suppress even good-news stocks |
| Technical momentum | Medium | Is the stock up or down in the past 3–5 sessions? Momentum tends to persist short-term |
| Breaking news (last 24h) | Very High | Fresh catalysts dominate short-term moves |

**Directional call:** Combine signals into one of:
- **Strong Bullish** — most signals positive, clear catalyst
- **Mild Bullish** — slight edge positive, no major headwinds
- **Neutral / Sideways** — signals mixed or offsetting
- **Mild Bearish** — slight edge negative, no major tailwind
- **Strong Bearish** — most signals negative, clear negative catalyst

**Estimated range:** Based on directional call and recent volatility, express as a % range from current price:
- Strong move: ±3–5%+
- Moderate move: ±1.5–3%
- Muted move: ±0.5–1.5%
- Sideways: ±0.5%

Example: "预计在 [price]–[price] 之间波动，中性偏多，核心区间 +1.5% ~ +2.5%"

**Confidence level:** Be honest about uncertainty.
- High confidence: multiple signals aligned + fresh catalyst
- Medium confidence: signals mixed but directional lean is clear
- Low confidence: signals contradictory or insufficient data

---

## Step 4 — Write the forecast report

Output a structured report in the conversation. Use this template:

```
## 股价短期走势预测 — [日期]

### 📱 小米集团 (01810.HK)

**当前价格：** HK$XX.XX（截至 [时间]）  
**预测方向：** [Strong/Mild Bullish / Neutral / Mild/Strong Bearish]  
**预估区间：** HK$XX.XX ~ HK$XX.XX（约 ±X%）  
**置信度：** [High / Medium / Low]

#### 判断依据：
**利多因素：**
- [因素1] — [一句说明，引用具体事件或政策]
- [因素2] ...

**利空因素：**
- [因素1] — [一句说明]

**关键变量：** [最需要关注的不确定因素，e.g. "港股今日开盘方向" or "美联储表态"]

---

### 🎵 腾讯音乐 (1698.HK)

**当前价格：** HK$XX.XX  
**预测方向：** ...  
**预估区间：** ...  
**置信度：** ...

#### 判断依据：
**利多因素：** ...
**利空因素：** ...
**关键变量：** ...

---

### 🌐 市场背景
[2–3 sentences on the macro/market environment affecting both stocks today]

### ⚠️ 免责声明
本预测基于公开信息和项目内研究资料综合判断，仅供参考，不构成投资建议。短期股价受多重随机因素影响，实际走势可能与预测存在显著偏差。
```

---

## Step 5 — Save forecast to disk

Saving every prediction is essential — it builds a track record that lets you calibrate accuracy over time and look back at what signals drove past calls.

### Directory structure

Ensure `forecasts/` exists in the current project directory. Within it, maintain two files per run:

```
forecasts/
├── YYYY-MM-DD_forecast.md      ← Full narrative report (the template above)
└── YYYY-MM-DD_forecast.json    ← Structured signal data for programmatic use
```

### Narrative report (`YYYY-MM-DD_forecast.md`)

Write the full template output from Step 4 verbatim. The filename date should reflect the **forecast target date** (i.e., the trading day being predicted), not necessarily today's calendar date. If predicting next-day (e.g., writing on Sunday for Monday's open), use Monday's date.

### Structured signal file (`YYYY-MM-DD_forecast.json`)

Also write a compact JSON alongside the narrative. This makes it easy to query historical forecasts and eventually build an accuracy tracker. Use this schema:

```json
{
  "forecast_date": "YYYY-MM-DD",
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "market_backdrop": "one-sentence summary of HSI / macro environment",
  "xiaomi": {
    "ticker": "01810.HK",
    "price_at_forecast": 0.00,
    "direction": "Mild Bullish",
    "range_low": 0.00,
    "range_high": 0.00,
    "range_pct": "+1%~+4%",
    "confidence": "Medium",
    "bull_factors": ["factor 1", "factor 2"],
    "bear_factors": ["factor 1", "factor 2"],
    "key_variable": "most important unknown"
  },
  "tencent_music": {
    "ticker": "1698.HK",
    "price_at_forecast": 0.00,
    "direction": "Neutral",
    "range_low": 0.00,
    "range_high": 0.00,
    "range_pct": "-1%~+1%",
    "confidence": "Low",
    "bull_factors": ["factor 1"],
    "bear_factors": ["factor 1", "factor 2"],
    "key_variable": "most important unknown"
  },
  "sources": {
    "xiaomi_events_used": ["YYYY-MM-DD_slug.md"],
    "tme_events_used": ["YYYY-MM-DD_slug.md"],
    "policy_events_used": ["YYYY-MM-DD_slug.md"]
  }
}
```

The `sources` block records which project event files actually influenced this forecast — useful for auditing which signals matter most in hindsight.

---

## Step 6 — Send Feishu notification (if configured)

```bash
python3 scripts/feishu_notify.py \
  --title "📈 股价走势预测 [日期]" \
  --item "📱 小米 01810.HK — [方向] [区间]（置信度：[X]）" \
  --item "   利多：[最重要的1个因素]" \
  --item "   利空：[最重要的1个因素]" \
  --item "────────────────────" \
  --item "🎵 腾讯音乐 1698.HK — [方向] [区间]（置信度：[X]）" \
  --item "   利多：[最重要的1个因素]" \
  --item "   利空：[最重要的1个因素]" \
  --item "────────────────────" \
  --item "🌐 市场背景：[HSI/大盘方向一句话]" \
  --footer "📁 详情: forecasts/YYYY-MM-DD_forecast.md"
```

Skip silently if `scripts/feishu_notify.py` or `.env` is missing.

---

## Important notes

**On uncertainty:** Short-term stock prices are genuinely hard to predict. The value of this skill is not in being right every time — it's in making the reasoning explicit and grounded in the project's accumulated research. A "Low confidence / Neutral" call that honestly reflects mixed signals is better than a false high-confidence call.

**Recency wins:** A single major negative catalyst from the last 24 hours outweighs several mildly positive events from the past week. Always scan for breaking news before finalizing the call.

**Policy amplification:** China macro policy moves (especially unexpected PBOC actions or US-China trade escalations) can override company-specific fundamentals entirely on a given day. When a fresh policy event is in the `china-policy/` directory dated today or yesterday, treat it as a dominant signal.

**HK listing:** Both Xiaomi (01810.HK) and Tencent Music (1698.HK) are tracked via their Hong Kong listings. HSI direction is the primary market backdrop for both stocks.

**Archive forecasts:** Saving predictions to `forecasts/` lets you build a track record. Over time, comparing predictions to actual outcomes is the best way to calibrate and improve the scoring approach.
