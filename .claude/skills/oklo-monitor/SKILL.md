---
name: oklo-monitor
description: >
  Monitor and analyze recent events related to Oklo Inc. (奥克洛, NYSE: OKLO), storing structured impact analyses in the `events/oklo/` directory of the current project. Use this skill whenever the user asks to track, monitor, analyze, or research Oklo news, events, announcements, market movements, or any activity involving Oklo nuclear microreactors — even if they don't use the word "monitor". Triggered by: "分析Oklo最新事件", "Oklo news analysis", "OKLO stock news", "奥克洛动态", "追踪Oklo", "nuclear microreactor news", or any request involving Oklo intelligence gathering.
---

# Oklo Inc. 事件监控与分析 Skill

This skill searches for recent events related to Oklo Inc. (NYSE: OKLO), analyzes the impact of each event on the company, stores results in structured markdown files, and deduplicates to avoid re-analyzing events already on record.

Oklo is a next-generation nuclear fission company developing sodium-cooled fast reactors (Aurora Powerhouse, 15–75 MWe) with a closed fuel cycle. **完整知识库见 `research/stock/oklo.md`**——每次分析前先读该文件，作为所有影响评估的基准（关键价位、分析师共识、风险清单、内部交易/ATM/短息等当前基准数据都以该文件为准，本 skill 不重复硬编码这些会过期的数字）。

---

## 监控维度主表

下表是当前阶段的监控维度，按权重排序（权重越高越优先搜索和分析）。**一表两用**：`搜索信号`列指导 Step 2 搜什么，`评估要点`列指导 Step 4 怎么评——具体数值基准一律以 `oklo.md` 为准。

| 权重 | 维度 | 搜索信号（Step 2 搜什么） | 评估要点（Step 4 怎么评） |
|------|------|------------------------|-------------------------|
| 🔴 最高 | **Aurora / Groves 临界里程碑** | criticality achieved/delayed、DOE DSA approval、Aurora-INL / Groves VIPR update | 是否实现临界 / 推迟？DSA 是否获批？是否改变临界时间表？|
| 🔴 最高 | **NRC COLA 进展** | NRC combined license、COLA filing、review acceptance/rejection | 申请提交 / 受理 / 审查进展？许可证时间轴是否变化 |
| 🟠 高 | **内部人员交易** | insider selling/buying、10b5-1 plan、Form 4 | 套现规模 / 频率是否加速？是否出现**首笔内部买入**（强正面信号）？|
| 🟠 高 | **ATM 融资与稀释** | ATM drawdown、equity offering、share count change | 新动用规模？股本总数变化？稀释节奏 |
| 🟠 高 | **竞争对手 IPO** | X-energy (XE) Nasdaq IPO、Holtec IPO、NuScale milestone | 上市时间 / 定价？是否分流 SMR 板块资金 |
| 🟠 高 | **分析师评级变化** | price target upgrade/downgrade、new coverage initiation | 目标价区间收窄 / 扩大？新机构覆盖 / 评级变动 |
| 🟠 高 | **关键客户财报（Meta/NVDA）** | Meta capex guidance、NVDA AI outlook、MSFT/AMZN data center spend | Meta 合同执行风险？数据中心景气度（详见宏观速查）|
| 🟠 高 | **Fed 货币政策** | FOMC、Powell speech、CPI/PCE、dot plot | 见「宏观敏感性速查」——OKLO 对利率**极高敏感** |
| 🟡 中 | **客户管道更新** | new LOI/PPA/contract、Meta partnership、data center nuclear deal | 新签约？管道质量 / 规模变化 |
| 🟡 中 | **燃料供应链执行** | Centrus HALEU、Standard Nuclear、ARMEC integration | LOI → 正式合同？MOU 落地？整合是否顺利 |
| 🟡 中 | **Atomic Alchemy 同位素** | Groves reactor、isotope commercial contract | 是否获**首笔商业合同**（最早的真实营收来源）|
| 🟡 中 | **短息与期权异动** | short interest change、unusual options activity | 空头仓位较基准是否显著变化？异常看涨/看跌期权 |
| 🟢 低 | **DOE 政策/补贴** | DOE loan guarantee、government contract、nuclear policy | 贷款担保进展？核能行政命令？DOE 合同新增 |
| 🟢 低 | **行业板块联动** | SMR sector、Japan/EU nuclear、AI+nuclear narrative | 板块估值中枢变化？竞品里程碑是否改变相对地位 |

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

按上方主表的权重分组搜索，优先覆盖高权重维度。每组至少运行一条查询。

**查询中的年份用当前年份**：运行前先 `date +%Y` 确认今年是哪一年；跨年时一并搜索"最近 12 个月"。下方示例以 `{YEAR}` 表示当前年份。

**🔴 最高优先级查询**（必须运行）：
- `Oklo Aurora criticality DSA DOE approval {YEAR}`
- `Oklo Atomic Alchemy Groves reactor criticality {YEAR}`
- `Oklo NRC COLA combined license application update {YEAR}`
- `OKLO insider selling buying Form 4 SEC filing {YEAR}`

**🟠 高优先级查询**（尽量运行）：
- `X-energy Nasdaq IPO XE NuScale SMR competitor news {YEAR}`
- `OKLO analyst price target upgrade downgrade {YEAR}`
- `Oklo stock news latest site:seekingalpha.com OR site:benzinga.com`

**🟠 宏观因素查询**（有重大宏观事件时运行）：
- `FOMC rate decision Fed Powell growth stocks impact {YEAR}`
- `Meta Platforms earnings capital expenditure AI data center guidance {YEAR}`
- `NVDA NVIDIA earnings AI sector outlook SMR nuclear {YEAR}`
- `VIX volatility spike risk-off growth stocks nuclear energy {YEAR}`

**🟡 中优先级查询**（按需运行，事件较少时补充）：
- `Oklo Meta partnership data center nuclear power update {YEAR}`
- `Oklo Centrus HALEU fuel supply contract update {YEAR}`
- `Oklo Standard Nuclear ARMEC integration update {YEAR}`
- `Oklo Atomic Alchemy isotope commercial contract {YEAR}`
- `OKLO short interest ATM equity offering dilution {YEAR}`

Collect all results. For each result, record:
- **title** (标题)
- **date** (日期, ISO format if available, else approximate)
- **source** (来源)
- **url** (链接)
- **summary** (摘要, 1–2 sentences from the search result)

---

## Step 3 — Deduplicate

先用脚本拉取注册表里所有已知 URL：
```bash
python3 scripts/monitor_registry.py --dir events/oklo --list-urls
```

对每条收集到的事件：
- URL 已在上面列表中 → 跳过
- 标题与已有事件 >80% 相似（同一事件不同来源）→ 跳过
- 只保留**全新**事件

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

**评估时对照上方「监控维度主表」的`评估要点`列，并以 `research/stock/oklo.md` 的最新研究结论为基准**（关键价位、分析师共识区间、内部交易/ATM/短息基准、风险清单等都在该文件里，不要在本 skill 里找硬编码数字）。重大宏观事件叠加时，参照下方「宏观敏感性速查」分析传导路径。

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

**路径约定**：注册表里的 `file` 字段统一用**仓库根目录相对路径**（`events/oklo/events/YYYY-MM-DD_slug.md`）；`index.md` 内的链接因其自身位于 `events/oklo/`，用 `events/YYYY-MM-DD_slug.md`。

**追加到 `events/oklo/analyzed_events.json`**：把本次新事件写入一个临时 JSON 数组文件（每条含 `url` / `title` / `date` / `file` / `impact_rating`），用脚本去重追加——脚本会自动填 `analyzed_at`（当前 UTC 时间戳）并跳过 url 已存在的条目：

```bash
python3 scripts/monitor_registry.py --dir events/oklo --add /tmp/oklo_new_events.json
```

临时文件单条格式：
```json
[
  {
    "url": "https://...",
    "title": "Event title",
    "date": "YYYY-MM-DD",
    "file": "events/oklo/events/YYYY-MM-DD_slug.md",
    "impact_rating": "🟢 High Positive"
  }
]
```

**更新 `events/oklo/index.md`**：为每个新事件追加一行：

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
  --footer "📁 详情: events/oklo/"
```

- If no new events: `--item "✅ 今日无新事件（已跳过 Y 个重复）"`
- Skip silently if `scripts/feishu_notify.py` or `.env` is missing

---

## OKLO 宏观敏感性速查

OKLO 是零营收高β成长股，对宏观因子的反应幅度是大盘的 2-3 倍（具体 β 值见 `oklo.md`）。以下是 `docs/fundamentals/us-market-drivers.md` 中 8 个宏观类别对 OKLO 的具体传导路径：

| 宏观类别 | OKLO 传导路径 | 方向 | 敏感度 |
|---------|------------|------|--------|
| **Fed 货币政策** | 利率上行 → 折现率提高 → 无现金流成长股估值压缩；降息/鸽派 → 流动性溢价扩张，OKLO 率先受益 | 降息利好 / 加息利空 | 🔴 极高 |
| **宏观经济数据** | CPI/PCE 超预期（通胀回升）→ 市场重新定价加息路径 → 成长股遭抛售；就业数据疲软 → risk-off，OKLO 高β放大跌幅 | 降温利好 / 超预期利空 | 🟠 高 |
| **财报季** | Meta capex guidance（OKLO 最大客户，1.2 GW 合同挂钩）；NVDA earnings AI outlook（数据中心景气度锚）；MSFT/AMZN data center spend → AI+核能叙事强弱 | Meta/NVDA 上调利好 / 下调利空 | 🔴 极高（Meta 直接影响客户执行风险） |
| **地缘政治** | 中东冲突→原油飙升→通胀预期→加息担忧→高β遭抛；俄乌缓和→能源价格回落→核能替代逻辑减弱；台海紧张→全市场 risk-off | 多方向、通常短期利空 | 🟠 高 |
| **财政/监管政策** | DOE 贷款/补贴政策（直接影响 OKLO 融资成本和竞争格局）；行政命令加速核能许可 → 直接利好；大型轻水堆（AP1000）获政策优先 → 结构性利空（SMR 政策优先级边缘化） | 正向政策利好 / 偏向大核利空 | 🔴 极高（参考 DOE 巨额 AP1000 贷款案例）|
| **市场结构因素** | VIX 飙升 → 高β先跌，OKLO 2-3x 放大；高做空比率下 VIX 飙升触发 margin call 强制平仓；VIX 回落 → 做空轧空反弹 | VIX 低利好 / VIX 高利空 | 🔴 极高 |
| **大宗商品** | 铀价上涨（≈HALEU 燃料成本上升）→ 运营成本隐忧（中性偏负）；天然气暴跌 → 核能经济性相对弱化；原油飙升 → 能源转型叙事强化（短期利好核能板块） | 铀价高中性偏负 / 油价高中性偏正 | 🟡 中 |
| **全球市场联动** | 日元升值（套息交易平仓）→ 全球高风险资产遭抛，OKLO 被连带；中国/欧洲股市暴跌 → 风险偏好全面收缩；美元指数急升 → 外资撤出美国成长股 | 日元升值/美元急升利空 | 🟠 高 |

**快速判断规则**：
- **FOMC 鸽派 / CPI 降温**：优先搜索 OKLO 是否有个股催化剂叠加，双利好可能触发短逼空
- **Meta 财报 capex 下调**：立即升级为高优先级事件，客户执行风险直接动摇 14 GW 管道估值逻辑
- **VIX 显著走高（如 >25）**：即使无 OKLO 个股消息，也需记录宏观背景作为价格波动解释
- **日元升值 > 2% 单日**：历史上触发全球成长股 5-10% 瞬时下跌（参考 2024-08 日元套利崩盘）

---

## Important notes

- **首先读 oklo.md**：每次监控运行前先读 `research/stock/oklo.md`，确保影响评估与最新研究基准对齐（关键价位、分析师共识、内部交易/ATM/短息基准、风险清单）。**会过期的具体数字以该文件为单一真相来源，本 skill 不重复维护**。
- **遵循分析框架**：影响评估遵循 `stock-analysis-framework` 的硬约束——区分事实与判断、利好利空并列、结论附信心等级（高/中/低）、不编造数据、不预测具体价格。
- **Source credibility**: Prefer Reuters, Bloomberg, FT, Oklo IR (oklo.com/investors), NRC.gov, DOE.gov, Seeking Alpha (institutional analysis only). Flag low-credibility sources.
- **二元催化剂意识**：Aurora / Groves 临界是当前最大的二元风险——成功则轧空，失败则崩跌。相关事件要特别标注"会否影响临界时间表"。
- **内部人员交易解读**：Oklo 的 10b5-1 计划于 2025-03-31 预设。套现本身不代表内幕信息，但**累积规模和节奏**是重要信号（当前基准数据见 `oklo.md`）。若出现**首次内部人员买入**，立即标记为高正面信号。
- **竞争对手上市影响**：X-energy (XE) 和 Holtec IPO 完成后，SMR 板块估值中枢可能下移。监控这两家公司的上市节点和定价。
- **Valuation context**: OKLO 是零营收投机成长股，已从 52 周高点大幅回撤（当前价位与回撤幅度见 `oklo.md`）。情绪和叙事变化可能造成 ±10–20% 单日波动，影响评级时按此波动性加权。
- **Deduplication priority**: When in doubt, skip.
- **跨板块移交**：若事件具跨板块传导性（如 Meta capex 变动牵动 AI+核能链、利率冲击全板块），移交 `event-impact-estimation` skill 做传导链分析。
