---
name: forecast-review
description: >
  Compare stock price forecasts against actual results for Xiaomi (01810.HK) and Tencent Music (TME), reflect on prediction errors, update forecast records with review data, and send a Feishu notification. Use this skill whenever the user asks to review, verify, check, or grade a past stock forecast — including phrases like "预测对了吗", "复盘一下预测结果", "昨天小米预测准了吗", "帮我对比一下实际走势", "forecast accuracy", "prediction review", or any request to compare what was predicted vs what actually happened. Always use this skill when the user wants to evaluate forecast quality or understand why a prediction was wrong.
---

# 预测结果复盘 Skill（小米 & 腾讯音乐）

This skill fetches actual closing prices for the forecast date, grades each prediction as Hit / Partial / Miss, reflects on the root cause of any errors, writes the review back to the forecast record, and sends a structured Feishu notification. The goal is honest, useful learning — not to justify past calls, but to understand what the signal model missed.

## Workflow Overview

1. **Find forecasts to review** — identify unreviewed forecast JSON files
2. **Fetch actual prices** — get real closing prices for the forecast date
3. **Grade each prediction** — Hit / Partial / Miss with objective criteria
4. **Reflect on misses** — diagnose what went wrong and why
5. **Update records** — write review into forecast JSON + save narrative `.md`
6. **Send Feishu notification**

---

## Step 1 — Find forecasts to review

Scan `forecasts/` for JSON files (pattern: `YYYY-MM-DD_forecast.json`).

A forecast needs review if:
- Its `forecast_date` is today or earlier, AND
- The JSON does **not** yet contain a top-level `"review"` field

If the user specifies a date (e.g., "复盘4月14日"), target that file. Otherwise, process all unreviewed files, newest first.

If no unreviewed forecasts exist, report this and stop.

---

## Step 2 — Fetch actual prices

For each forecast date, search for the actual closing prices:

- `小米集团 01810.HK 收盘价 YYYY-MM-DD` (or "YYYY年MM月DD日收盘")
- `Tencent Music TME closing price YYYY-MM-DD`
- Also note the HSI closing that day for context

Record:
- `actual_close` — the official closing price
- `actual_pct_change` — percentage change vs the prior session close (`price_at_forecast`)
- `hsi_pct_change` — HSI % change that day (to understand market backdrop)

If the forecast date was a non-trading day (weekend, holiday), use the next available trading session and note this.

---

## Step 3 — Grade each prediction

Apply these grading criteria objectively — don't rationalize, just score:

### Direction grade
Compare the `direction` field against the actual move:

| Predicted direction | Actual move | Direction grade |
|--------------------|-------------|-----------------|
| Bullish (Strong/Mild) | Positive (>+0.5%) | ✅ Correct |
| Bearish (Strong/Mild) | Negative (<-0.5%) | ✅ Correct |
| Neutral | Within ±0.5% | ✅ Correct |
| Bullish | Negative | ❌ Wrong |
| Bearish | Positive | ❌ Wrong |
| Neutral | Move >±1.5% | ❌ Wrong |
| Any | Move within 0.5% of predicted boundary | 🟡 Borderline |

### Range grade
Did the actual closing price fall within `[range_low, range_high]`?
- ✅ In range: actual close is between range_low and range_high
- 🟡 Near miss: actual close is within 2% of either boundary
- ❌ Outside range: actual close is more than 2% beyond either boundary

### Overall grade

| Direction | Range | Overall |
|-----------|-------|---------|
| ✅ | ✅ | ✅ **Hit** |
| ✅ | 🟡 or ❌ | 🟡 **Partial** |
| 🟡 | ✅ or 🟡 | 🟡 **Partial** |
| ❌ | anything | ❌ **Miss** |
| ✅ | ✅ but confidence was Low | 🟡 **Lucky Hit** (note this) |

---

## Step 4 — Reflect on misses and partials

For every ❌ Miss or 🟡 Partial, do a structured root-cause analysis. The goal is to identify *what specifically went wrong in the signal model* — not just "the market was unpredictable."

Think through these questions:

**1. Which listed bull/bear factors were wrong?**
- Did a bull factor fail to materialize? (e.g., "AI catalyst already priced in by open")
- Was a bear factor underweighted? (e.g., "macro tariff risk overwhelmed company-specific news")

**2. What was missed entirely?**
- Was there a significant catalyst not in the forecast JSON's `sources`?
- Was there breaking news between forecast generation and market open that changed the picture?

**3. Was the signal model systematically biased?**
- Did we overweight company-specific news vs macro/market backdrop?
- Did we anchor too strongly on recent momentum?
- Was the confidence level honest? (Low confidence + miss is less surprising than High confidence + miss)

**4. What would have changed the call?**
- State the specific piece of information that, if known, would have produced a correct prediction.
- This is the most actionable output — it tells you what to monitor more closely next time.

Write the reflection concisely: 3–6 sentences per stock, focused on the most important insight. Avoid vague statements like "markets are unpredictable" — that's not useful. Aim for specific, falsifiable observations like "the MiMo AI catalyst was already priced in from the prior session's 3% bounce; fresh catalysts that already moved the stock before the forecast window rarely drive follow-through."

---

## Step 5 — Update records

### Update the forecast JSON

Add a `"review"` object to the existing forecast JSON:

```json
{
  "review": {
    "reviewed_at": "YYYY-MM-DDTHH:MM:SSZ",
    "hsi_actual_pct": 1.2,
    "xiaomi": {
      "actual_close": 32.10,
      "actual_pct_change": 2.3,
      "direction_correct": true,
      "in_range": true,
      "overall_grade": "Hit",
      "reflection": null
    },
    "tencent_music": {
      "actual_close": 9.15,
      "actual_pct_change": -2.2,
      "direction_correct": false,
      "in_range": false,
      "overall_grade": "Miss",
      "reflection": "预测偏多的核心错误是低估了KWEB整体抛压：当日中概股指数下跌3.2%，系统性流出盖过了公司层面的利好因子。关键教训：在中美关税博弈高度活跃期，TME这类流动性偏低的中概ADR应首先检查当日KWEB方向，再叠加公司信号。"
    }
  }
}
```

Read the existing JSON, merge in the `review` field, and write it back. Do not modify any other fields.

### Write a review narrative (`YYYY-MM-DD_review.md`)

Save a human-readable review to `forecasts/YYYY-MM-DD_review.md`:

```markdown
# 预测复盘 — YYYY-MM-DD

## 市场背景
HSI当日: [+/-X.X%] | 整体市场: [风险偏好/规避]

## 小米集团 (01810.HK)

| 项目 | 预测 | 实际 |
|------|------|------|
| 方向 | [Mild Bullish] | [+2.3%] |
| 区间 | HK$31.00~33.50 | HK$32.10 ✅ |
| 整体评级 | — | ✅ Hit |

### 反思
[如有 Miss/Partial，填写反思内容；Hit 可简要确认哪个因素起了主导作用]

---

## 腾讯音乐 (TME)

| 项目 | 预测 | 实际 |
|------|------|------|
| 方向 | [Neutral/Bearish] | [-2.2%] |
| 区间 | $8.90~9.50 | $9.15 🟡 |
| 整体评级 | — | 🟡 Partial |

### 反思
[...]

---

## 总结与改进方向
[1–3 sentences: 这次复盘最重要的教训是什么？下次预测应该调整哪个权重？]
```

---

## Step 6 — Send Feishu notification

```bash
python3 scripts/feishu_notify.py \
  --title "🔍 预测复盘 YYYY-MM-DD" \
  --item "📱 小米 01810.HK — [实际涨跌%] → [✅ Hit / 🟡 Partial / ❌ Miss]" \
  --item "   预测: [方向] [区间] | 实际: HK$[close]" \
  --item "   [如Miss: 反思一句话核心结论]" \
  --item "────────────────────" \
  --item "🎵 腾讯音乐 TME — [实际涨跌%] → [✅ Hit / 🟡 Partial / ❌ Miss]" \
  --item "   预测: [方向] [区间] | 实际: $[close]" \
  --item "   [如Miss: 反思一句话核心结论]" \
  --item "────────────────────" \
  --item "🌐 HSI当日: [+/-X.X%]" \
  --footer "📁 详情: forecasts/YYYY-MM-DD_review.md"
```

- For a Hit with no reflection: omit the reflection line
- For a Miss: the reflection line is the most valuable part — make it specific and actionable
- Skip silently if `scripts/feishu_notify.py` or `.env` is missing

---

## Important notes

**Be honest about misses.** The value of this review comes entirely from intellectual honesty. If the prediction was wrong, say so clearly and explain specifically why. Rationalizations like "the prediction was conceptually right but the market overreacted" are not useful — if the actual price moved outside the predicted range, it's a miss.

**Distinguish luck from skill.** A Hit with Low confidence is a lucky hit — note this explicitly. A correct direction call but wrong magnitude (range miss) is a Partial, not a Hit. These distinctions matter for calibrating the model over time.

**Macro vs company signals.** A recurring pattern in Chinese equities: on days with large macro moves (HSI ±2%+), company-specific signals are largely overwhelmed. If a miss occurred on a high-volatility macro day, this is worth noting — it suggests the forecast model should apply a "macro override" when HSI is expected to move significantly.

**Build the track record.** Over time, the `review` fields across all forecast JSONs form a calibration dataset. If you consistently grade well and reflect honestly, the signal model will improve. If direction accuracy is consistently >60% but range accuracy is <40%, that tells you to widen range estimates. Let the data speak.
