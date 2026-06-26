---
name: event-impact-estimation
description: >
  对一个大型事件（重磅财报 / 政策 / 宏观冲击 / 龙头动作）做跨板块"传导链"影响预估——从利润池重分布推演到板块赢输、大盘净方向，最终落到本项目 watchlist 持仓的逐标的影响，结果存盘 `events/macro-events/` 并推送飞书。Use this skill whenever the user wants to understand the ripple / contagion effect of a big event across sectors or on the broad market, or asks how one event affects other stocks or their holdings — even casual phrasings. Triggered by: "分析X的连锁影响", "X会带崩大盘吗", "X对各板块/大盘的传导", "美光财报对消费电子的影响", "利润链重分配", "这事对我持仓有什么影响". 各 monitor skill 抓到具跨板块传导性的大事件时也应移交本 skill。Do NOT use for single-stock deep research (用 stock-research) 或单标的日常事件记录（用对应 *-monitor skill）。
---

# 大型事件传导链影响预估 Skill

给定一个大型事件，推演它跨板块的连锁影响，并落到本项目的 watchlist 持仓。补的是 `docs/fundamentals/us-market-drivers.md`（静态宏观速查）之上的"二阶 / 跨板块传导"那层。

**先读基准**：`docs/fundamentals/us-market-drivers.md`（宏观传导）、`references/event-archetypes.md`（事件原型库）、`watchlist/` 下最新关注清单。

---

## 量级闸门（先判断够不够"大型"）

只对**具备跨板块传导性**的事件跑完整传导链。量级信号（满足其一即可）：
- 影响整条产业链的**利润分配**（上游吃下游、龙头涨价转嫁）
- **龙头定调**（NVDA / TSMC / 美光财报给行业景气度定调）
- **宏观冲击**（Fed 超预期、CPI 爆表、关税、地缘油价）
- **大盘级别波动**需要归因

**不够大型** → 不硬编链条，直接说明"未达跨板块量级，建议用单标的分析（stock-research）或对应 *-monitor"，然后停止。

---

## 核心方法论（5 步传导链）

1. **事件归类 + 量级闸门** — 见上。归到某一类（财报/政策/宏观/龙头动作）。
2. **利润池重分布** — 谁的毛利/定价权 ↑↓？*赢家吃掉了谁的利润*（美光案：利润向上游内存集中 = 吃掉下游终端毛利）。
3. **跨板块传导链（2-3 跳）** — 逐跳写 `方向 + 机制 + 强度 + 时滞`。例：内存涨价 →(成本↑, 即时)→ 手机/PC 厂毛利压缩 →(转嫁失败/需求抑制, 1-2 季)→ 消费电子板块承压。
4. **大盘净影响** — 汇总指数方向：权重股暴露、是否 risk-off、情绪面，给净方向 + 信心等级。
5. **落到 watchlist/持仓** — 读 `watchlist/*.md`，每个标的给 `利好/利空/中性 + 信心（高/中/低）+ 关键假设`；受影响标的可读其 `research/stock/<ticker>.md` 做更精准判断。

**用原型库**：先查 `references/event-archetypes.md` 是否有匹配原型——命中则实例化其传导链；未命中则按上面 5 步现推，**并按"生长规则"在分析后追加一条新原型**（仅当跨板块 + 可复用）。

---

## 工作流 Steps

1. **收集事件事实**：WebSearch 拿细节（若由 monitor 移交、已带事实，可跳过或补充）。
2. **量级闸门**：不够大型则降级退出。
3. **查原型库匹配**：`references/event-archetypes.md`。
4. **跑 5 步传导链**：命中原型则实例化，否则现推。
5. **映射 watchlist**：读 `watchlist/*.md`。
6. **写报告**：`events/macro-events/events/YYYY-MM-DD_<slug>.md`（模板见下）。
7. **更新注册表 + index**：用临时 JSON + 脚本去重追加（自动填时间戳）：
   ```bash
   python3 scripts/monitor_registry.py --dir events/macro-events --add /tmp/macro_new.json
   ```
   首次运行前确保 `events/macro-events/{index.md, analyzed_events.json, events/}` 存在（不存在则创建，`analyzed_events.json` 初始化为 `{"events": []}`）；并向 `events/macro-events/index.md` 追加一行。
8. **飞书通知**：
   ```bash
   python3 scripts/feishu_notify.py \
     --title "🔗 事件传导链分析：[事件标题]" \
     --item "大盘净影响：[🔴/🟡/🟢] [方向]（信心 X）" \
     --item "受损板块：[...]｜受益板块：[...]" \
     --item "持仓影响：小米[..] / OKLO[..] / TME[..]" \
     --footer "📁 详情: events/macro-events/"
   ```
   `scripts/feishu_notify.py` 或 `.env` 缺失则静默跳过。
9. **沉淀新原型**：若命中生长规则，追加到 `references/event-archetypes.md`。

---

## 输出模板（events/macro-events/events/ 下单文件）

```markdown
# [事件标题]

**日期 / Date:** YYYY-MM-DD
**事件来源 / Source:** [Source](URL)
**匹配原型 / Archetype:** [原型名 or "新原型（已沉淀）"]
**大盘净影响 / Market Net:** 🔴 利空 / 🟡 中性 / 🟢 利好（信心：高/中/低）

---

## 事件摘要 / Event
[2-4 句事实]

## 利润池重分布 / Profit-Pool Shift
[谁的毛利/定价权 ↑↓，赢家吃了谁的利润]

## 跨板块传导链 / Transmission Chain
1. [第1跳：方向 + 机制 + 强度 + 时滞]
2. [第2跳：...]
3. [第3跳：...]

## 板块赢输 / Sector Winners & Losers
| 板块 | 赢/输 | 机制 | 信心 |
|------|-------|------|------|

## 大盘净判断 / Market Impact
[指数方向 + 权重股暴露 + risk-off 与否 + 信心]

## 对持仓/关注票的影响 / Watchlist Impact
| 标的 | 利好/利空/中性 | 信心 | 关键假设 |
|------|---------------|------|---------|

## 风险与会推翻判断的信号
[1-3 条]
```

---

## 硬约束（沿用 stock-analysis-framework）

区分事实与判断、利好利空并列、结论附信心等级、不预测具体价格（给方向/区间）、数据可溯源不编造（推测的跳标"信心低"）、拒绝 FOMO 话术。

## 边界与降级

- 事件不够"大型" → 明说并退出，不硬编链条。
- watchlist 文件名/格式变化 → 读 `watchlist/` 下现有清单，容错。
- 重复事件 → 注册表去重（脚本自动按 url 跳过）。
