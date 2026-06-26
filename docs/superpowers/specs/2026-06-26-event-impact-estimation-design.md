# 大型事件传导链影响预估 skill 设计（event-impact-estimation）

> **状态**：设计已确认，待写实现计划
> **日期**：2026-06-26

---

## 1. 背景与目标

现有 `docs/fundamentals/us-market-drivers.md` 是 8 类宏观驱动的**静态速查**——能告诉你"原油↑→通胀↑→大盘↓"，但无法对一个**具体的大型事件**做跨板块的连锁推演。

典型缺口（用户原话场景）：

> 美光财报毛利率特别高 + 苹果宣布涨价 → 利润向上游内存产业集中 → 对消费电子行业打击 → 带崩大盘。

这是一条"利润池重分布 + 跨板块传导 + 大盘净影响"的二阶推演链。本 skill 补上这层能力，并把影响**最终落到用户的 watchlist/持仓**。

**目标**：给定一个大型事件，产出 `事件 → 利润池重分布 → 跨板块赢输 → 大盘方向 → watchlist 逐标的影响` 的结构化分析，存盘并推送飞书。

---

## 2. 关键决策（来自需求澄清）

| 维度 | 决策 |
|------|------|
| 输出焦点 | 完整传导链 **+ 落到我的持仓/关注票**（不只是通用地图） |
| 触发方式 | **独立 skill（手动调用）+ 被 monitor 移交调用**（两者都要） |
| 输出形态 | **存盘 `events/macro-events/` + 飞书通知**（与现有 monitor 一致） |
| 方法论组织 | **方法论骨架 + 较完整种子原型库(~8) 且持续生长**（B+C 合体） |

---

## 3. 形态与命名

- 新建独立 skill：**`event-impact-estimation`**
- 组成：
  - `SKILL.md` —— 方法论 + 工作流 + 输出模板
  - `references/event-archetypes.md` —— 生长型"事件原型库"

触发描述（frontmatter description）需覆盖：手动调用语（"分析美光财报的连锁影响"、"这事会带崩大盘吗"、"X 对各板块/大盘的传导"、"利润链重分配"）+ 说明 monitor skill 在抓到跨板块大事件时移交本 skill。

---

## 4. 核心方法论（5 步传导链）

1. **事件归类 + 量级闸门**
   判断事件是否够"大型"（具备跨板块传导性）。**不够则不硬编链条**，明确提示改用单标的分析或对应 monitor。量级信号：影响整条产业链利润分配、龙头定调、宏观冲击、大盘级别波动。

2. **利润池重分布**
   分析谁的毛利/定价权 ↑↓。核心洞察（美光案）：*利润向上游集中 = 吃掉下游终端利润*。明确"赢家拿走了谁的利润"。

3. **跨板块传导链（2-3 跳）**
   逐跳书写，每跳标注 `方向 + 机制 + 强度 + 时滞`。
   例：内存涨价 →(成本↑, 即时)→ 手机/PC 厂毛利压缩 →(转嫁失败/需求抑制, 1-2 季)→ 消费电子板块承压。

4. **大盘净影响**
   汇总到指数方向：权重股暴露、是否触发 risk-off、情绪面。给净方向 + 信心等级。

5. **落到 watchlist/持仓**
   读 `watchlist/*.md`，对每个标的给 `利好 / 利空 / 中性 + 信心等级（高/中/低）+ 关键假设`。受影响标的可进一步读其 `research/stock/<ticker>.md` 做更精准判断。

---

## 5. 事件原型库（`references/event-archetypes.md`）

每个原型字段：
- **触发特征**（怎么识别这是该原型）
- **传导链**（预先画好的逐跳链条）
- **典型受益板块 / 受损板块**
- **历史先例**
- **对本项目 watchlist 的常见落点**

**初始种子（~8，较完整覆盖常见大型事件）**：

1. 内存·存储周期反转（DRAM/NAND/HBM 涨价）—— 美光案
2. Mega-cap AI capex 变动（Meta/MSFT/AMZN/NVDA capex ↑↓）
3. 利率 / CPI 冲击（Fed 超预期、通胀爆表）
4. 龙头涨价转嫁（苹果涨价 → 利润链重分配）
5. 关税 / 贸易战
6. 地缘油价冲击
7. 龙头财报定调（NVDA / TSMC 给行业定调）
8. 日元套利平仓 / 全球流动性收缩

**生长机制**：来事件先查库匹配 → 命中则实例化；未命中则现推方法论 **并按沉淀规则新增一条原型进库**。
**沉淀规则**：仅当事件 **具跨板块传导性 + 可复用（未来会再现）** 才入库，避免库被一次性事件污染。

---

## 6. 工作流（Steps）

1. **收集事件事实**：WebSearch 拿事件细节（若由 monitor 移交，则已带事实，跳过或补充）
2. **事件归类 + 量级闸门**（不够大型则降级退出）
3. **查原型库匹配**（`references/event-archetypes.md`）
4. **跑 5 步传导链**（命中原型则实例化，否则现推）
5. **映射 watchlist**（读 `watchlist/*.md`）
6. **写报告 + 更新 index + 注册表**（复用 `scripts/monitor_registry.py --dir events/macro-events`）
7. **飞书通知**（复用 `scripts/feishu_notify.py`）
8. **沉淀新原型**（若命中沉淀规则，追加到 `references/event-archetypes.md`）

---

## 7. 数据流与复用

- **读**：`watchlist/*.md`、`references/event-archetypes.md`、受影响持仓的 `research/stock/<ticker>.md`、`docs/fundamentals/us-market-drivers.md`
- **写**：`events/macro-events/YYYY-MM-DD_<slug>.md` + `events/macro-events/index.md` + `events/macro-events/analyzed_events.json`
- **复用（零额外代码）**：
  - 去重 + 时间戳 + 注册表追加 → `scripts/monitor_registry.py --dir events/macro-events`（已建好并自测）
  - 飞书推送 → `scripts/feishu_notify.py`

---

## 8. 输出模板（events/macro-events/ 下单文件）

```markdown
# [事件标题]

**日期 / Date:** YYYY-MM-DD
**事件来源 / Source:** [Source](URL)
**匹配原型 / Archetype:** [原型名 or "新原型(已沉淀)"]
**大盘净影响 / Market Net:** 🔴 利空 / 🟡 中性 / 🟢 利好（信心：高/中/低）

---

## 事件摘要 / Event
[2-4 句事实]

## 利润池重分布 / Profit-Pool Shift
[谁的毛利/定价权↑↓，赢家吃了谁的利润]

## 跨板块传导链 / Transmission Chain
1. [第1跳：方向 + 机制 + 强度 + 时滞]
2. [第2跳：...]
3. [第3跳：...]

## 板块赢输 / Sector Winners & Losers
| 板块 | 赢/输 | 机制 | 信心 |

## 大盘净判断 / Market Impact
[指数方向 + 权重股暴露 + risk-off 与否 + 信心]

## 对持仓/关注票的影响 / Watchlist Impact
| 标的 | 利好/利空/中性 | 信心 | 关键假设 |
| 小米 1810.HK | ... | ... | ... |
| OKLO | ... | ... | ... |
| TME | ... | ... | ... |

## 风险与会推翻判断的信号
[1-3 条]
```

---

## 9. 与 monitor 衔接

在相关 monitor（`memory-flash-monitor`、`oklo-monitor`、`nuscale-monitor` 等）加**一行指针**：

> 若事件具跨板块传导性（见 `event-impact-estimation` 的量级闸门），移交 `event-impact-estimation` 做传导链分析。

轻量手动衔接，**不改 monitor 主流程**（skill 之间不程序化互调）。

---

## 10. 边界与降级

- **事件不够"大型"** → 明确说明"未达跨板块量级，建议用单标的分析/对应 monitor"，不硬编链条
- **watchlist 文件格式/路径变化** → 读 `watchlist/` 下现有清单，容错降级
- **重复事件** → 注册表去重（同 monitor）
- **不编造** → 推测性的跳明确标"信心低"；区分事实与判断

---

## 11. 硬约束（沿用 `stock-analysis-framework`）

区分事实与判断、利好利空并列、结论附信心等级、不预测具体价格（给方向/区间）、数据可溯源不编造、拒绝 FOMO 话术。

---

## 12. 验证方式

skill 为 prompt 而非代码，按 skill-creator 思路用代表性事件试跑、看输出合理性：

1. **美光财报毛利率超高**（内存周期原型）→ 应得：利润向内存集中、消费电子承压、对小米(消费电子)偏利空、对大盘偏空
2. **Fed 超预期鹰派 / CPI 爆表**（利率冲击原型）→ 高β成长股(OKLO)放大利空
3. **苹果涨价**（龙头涨价转嫁原型）→ 利润链重分配判断

`scripts/monitor_registry.py` 已单独自测通过。

---

## 13. 非目标（YAGNI）

- 不做实时自动轮询（由 monitor 触发或手动调用即可）
- 不做精确价格预测（给方向 + 信心）
- 不做 skill 间程序化互调（手动移交）
- 原型库不追求一次写满，靠运行中生长
