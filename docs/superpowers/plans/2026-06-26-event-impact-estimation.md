# event-impact-estimation Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新建 `event-impact-estimation` skill，对大型事件做"利润池重分布 → 跨板块传导 → 大盘净方向 → watchlist 逐标的影响"的结构化分析，存盘 `events/macro-events/` + 飞书。

**Architecture:** 一个 prompt-based skill（`SKILL.md` 方法论/工作流 + `references/event-archetypes.md` 生长型原型库），复用已建好的 `scripts/monitor_registry.py`（去重/注册表）和 `scripts/feishu_notify.py`（飞书）。无新增 Python 代码。

**Tech Stack:** Markdown skill（Claude Code SKILL 格式）、现有 Python 脚本、WebSearch。

**前置（执行时）：** 当前在 `main` 分支。执行前先开分支或 worktree（见 `superpowers:using-git-worktrees`），所有 commit 落在该分支。

**设计来源：** `docs/superpowers/specs/2026-06-26-event-impact-estimation-design.md`（本计划是其落地）。

---

## File Structure

| 文件 | 职责 | 操作 |
|------|------|------|
| `.claude/skills/event-impact-estimation/SKILL.md` | 触发描述 + 5 步方法论 + 工作流 + 输出模板 + 硬约束 | Create |
| `.claude/skills/event-impact-estimation/references/event-archetypes.md` | 8 个种子事件原型 + 生长规则 | Create |
| `.claude/skills/memory-flash-monitor/SKILL.md` | 加移交指针 | Modify |
| `.claude/skills/oklo-monitor/SKILL.md` | 加移交指针 | Modify |
| `.claude/skills/nuscale-monitor/SKILL.md` | 加移交指针 | Modify |
| `AGENTS.md` | skills 索引新增一行 | Modify |
| `events/macro-events/` | 运行时由 skill 创建（不预建），同 monitor 模式 | — |

---

## Task 1: 创建 skill 目录与 SKILL.md

**Files:**
- Create: `.claude/skills/event-impact-estimation/SKILL.md`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p .claude/skills/event-impact-estimation/references
```

- [ ] **Step 2: 写 SKILL.md（完整内容如下）**

写入 `.claude/skills/event-impact-estimation/SKILL.md`：

````markdown
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
````

- [ ] **Step 3: 校验 frontmatter 可被解析**

Run:
```bash
head -5 .claude/skills/event-impact-estimation/SKILL.md
```
Expected: 显示 `---` / `name: event-impact-estimation` / `description: >` 起始的 YAML 头。

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/event-impact-estimation/SKILL.md
git commit -m "feat(skill): add event-impact-estimation SKILL.md (methodology + workflow)"
```

---

## Task 2: 写种子原型库 references/event-archetypes.md

**Files:**
- Create: `.claude/skills/event-impact-estimation/references/event-archetypes.md`

每个原型字段固定为：**触发特征 / 传导链 / 典型受益板块 / 典型受损板块 / 历史先例 / 对本项目 watchlist 的常见落点**。

- [ ] **Step 1: 写文件头 + 生长规则**

写入文件开头：

```markdown
# 事件原型库 / Event Archetypes

供 `event-impact-estimation` skill 匹配大型事件用。来事件先在此查匹配，命中则实例化传导链。

**生长规则**：现推一个未命中的事件后，仅当它 **(a) 具跨板块传导性 且 (b) 未来会再现（可复用）** 才追加为新原型；一次性事件不入库，避免污染。

每个原型字段：触发特征 / 传导链 / 典型受益板块 / 典型受损板块 / 历史先例 / 对 watchlist 的常见落点。

---
```

- [ ] **Step 2: 写原型 1-2（完整范式，作为后续 6 个的模板）**

```markdown
## 原型 1：内存·存储周期反转（DRAM / NAND / HBM 涨价）

- **触发特征**：美光/SK海力士/三星财报毛利率大涨或给出涨价指引；HBM/DRAM 现货价跳涨；存储缺货。
- **传导链**：
  1. 存储涨价 →(成本↑, 即时)→ 利润池向上游存储原厂集中
  2. →(BOM 成本↑, 转嫁难, 当季-1季)→ 手机/PC/服务器整机厂毛利压缩
  3. →(终端涨价或需求抑制, 1-2季)→ 消费电子板块承压
- **典型受益板块**：存储原厂、存储设备、部分模组
- **典型受损板块**：消费电子整机、PC/手机品牌、低毛利硬件
- **历史先例**：2017-18 存储超级周期；2024-25 HBM 紧缺
- **对 watchlist 的常见落点**：小米(1810.HK, 消费电子+手机) 偏**利空**（BOM 成本↑）；中性偏空大盘（若科技权重股受拖累）。

## 原型 2：龙头涨价转嫁（如苹果涨价）

- **触发特征**：终端龙头（苹果等）宣布产品涨价，多与上游成本上升同期。
- **传导链**：
  1. 龙头涨价 →(转嫁成本, 即时)→ 龙头自身毛利可维持
  2. →(定价权分化)→ 有定价权者赢、无定价权者继续被上游挤压
  3. →(终端价格↑→需求弹性)→ 销量风险，传导到供应链出货
- **典型受益板块**：有定价权的终端龙头、上游涨价方
- **典型受损板块**：无定价权的中小整机/代工、价格敏感的需求端
- **历史先例**：历轮 iPhone 涨价 + 存储/面板涨价同期
- **对 watchlist 的常见落点**：小米(定价权弱于苹果)相对**利空**；判断需结合其自身涨价能力。
```

- [ ] **Step 3: 写原型 3-8（同字段，内容如下）**

```markdown
## 原型 3：利率 / CPI 冲击（Fed 超预期、通胀爆表）
- **触发特征**：FOMC 鹰派超预期、CPI/PCE 超预期、点阵图上移。
- **传导链**：折现率↑ →(即时)→ 无现金流/高久期成长股估值压缩 →(risk-off)→ 高β放大跌幅。
- **受益**：价值股、现金流稳健板块、（降息时）成长股。
- **受损**：零营收高β成长股、长久期科技。
- **历史先例**：2022 加息周期成长股杀估值。
- **watchlist 落点**：OKLO（零营收高β）放大**利空**；港股/中概受美元/利率间接传导。

## 原型 4：Mega-cap AI capex 变动（Meta/MSFT/AMZN/NVDA）
- **触发特征**：超大厂 capex 指引上调/下调；AI 数据中心支出表态。
- **传导链**：capex↑ →(订单, 1-2季)→ AI 算力/电力/核能产业链受益；capex↓ →(景气度↓)→ AI 叙事退潮、相关高估值标的杀逻辑。
- **受益（上调时）**：GPU/算力、数据中心电力、SMR 核能。
- **受损（下调时）**：AI 主题高估值股。
- **历史先例**：Meta-Oklo 1.2GW 合同；各轮超大厂 capex 指引。
- **watchlist 落点**：OKLO 直接挂钩 Meta capex，**高敏感**（上调利好/下调利空）。

## 原型 5：关税 / 贸易战
- **触发特征**：新关税、出口管制、实体清单。
- **传导链**：关税 →(供应链成本↑/订单受限)→ 受限行业利润压缩 →(中概/出口链)→ 估值与情绪承压。
- **受益**：进口替代、国产替代受益方。
- **受损**：跨境供应链、出口依赖、被制裁中概。
- **历史先例**：2018-19 中美贸易战；AI 芯片出口管制。
- **watchlist 落点**：小米/中概（出口与供应链敞口）偏**利空**。

## 原型 6：地缘油价冲击
- **触发特征**：中东冲突、OPEC+ 减产、油价跳涨。
- **传导链**：油价↑ →(能源通胀)→ CPI↑ →(加息预期)→ 高β遭抛；同时能源转型叙事短期强化。
- **受益**：能源股、（短期）核能/替代能源叙事。
- **受损**：高β成长股、航空/运输等高油耗。
- **历史先例**：2022 俄乌油价飙升。
- **watchlist 落点**：OKLO 双向（通胀传导利空 vs 能源叙事短利好），净偏空，信心低。

## 原型 7：龙头财报定调（NVDA / TSMC）
- **触发特征**：NVDA/TSMC 财报与指引，对 AI / 半导体景气度定调。
- **传导链**：定调向好 →(板块情绪)→ 整个 AI/半导体链跟涨；定调转弱 →(杀景气度)→ 板块普跌。
- **受益/受损**：随定调方向，AI/半导体/算力电力链整体同向。
- **历史先例**：NVDA 财报对科技板块的"定调"作用。
- **watchlist 落点**：OKLO 随 AI+核能叙事强弱同向。

## 原型 8：日元套利平仓 / 全球流动性收缩
- **触发特征**：BOJ 加息/YCC 调整、日元急升、全球 risk-off。
- **传导链**：日元升值 →(套息平仓)→ 全球高风险资产被抛 →(连带)→ 高β/成长股瞬时下杀。
- **受益**：避险资产（美债/黄金）。
- **受损**：全球高β成长股、杠杆资产。
- **历史先例**：2024-08 日元套利崩盘，全球成长股 5-10% 瞬跌。
- **watchlist 落点**：OKLO 等高β被连带**利空**，通常短期。
```

- [ ] **Step 4: 校验原型数量**

Run:
```bash
grep -c '^## 原型' .claude/skills/event-impact-estimation/references/event-archetypes.md
```
Expected: `8`

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/event-impact-estimation/references/event-archetypes.md
git commit -m "feat(skill): add 8 seed event archetypes for event-impact-estimation"
```

---

## Task 3: monitor 移交指针 + AGENTS.md 索引

**Files:**
- Modify: `.claude/skills/memory-flash-monitor/SKILL.md`
- Modify: `.claude/skills/oklo-monitor/SKILL.md`
- Modify: `.claude/skills/nuscale-monitor/SKILL.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: memory-flash-monitor 加移交指针**

在 `memory-flash-monitor/SKILL.md` 的分析步骤区（"Important notes" 或等价小节）追加一行：

```markdown
- **跨板块移交**：若事件具跨板块传导性（如存储涨价挤压消费电子整机、龙头定调），移交 `event-impact-estimation` skill 做传导链分析并落到 watchlist。
```

实施时先 Read 该文件定位锚点；用 Edit 在 notes 区插入上面这行。

- [ ] **Step 2: oklo-monitor 加移交指针**

`oklo-monitor/SKILL.md` 的 "Important notes" 区已存在（Task 已知结构）。在其中追加：

```markdown
- **跨板块移交**：若事件具跨板块传导性（如 Meta capex 变动牵动 AI+核能链、利率冲击全板块），移交 `event-impact-estimation` skill 做传导链分析。
```

- [ ] **Step 3: nuscale-monitor 加移交指针**

`nuscale-monitor/SKILL.md` 的 "Important notes" 区追加：

```markdown
- **跨板块移交**：若事件具跨板块传导性（SMR 板块联动、AI capex/利率冲击），移交 `event-impact-estimation` skill 做传导链分析。
```

- [ ] **Step 4: AGENTS.md skills 索引新增**

在 `AGENTS.md` "### 分析框架" 表（含 `stock-analysis-framework` / `stock-research` 行）后追加一行；用 Edit 把：

```
| `stock-research` | 单只股票深度研究报告，输出到 `research/stock/` |
```
替换为：
```
| `stock-research` | 单只股票深度研究报告，输出到 `research/stock/` |
| `event-impact-estimation` | 大型事件跨板块传导链分析，落到 watchlist，输出到 `events/macro-events/` |
```

- [ ] **Step 5: 校验指针与索引就位**

Run:
```bash
grep -rl "event-impact-estimation" .claude/skills/memory-flash-monitor/SKILL.md .claude/skills/oklo-monitor/SKILL.md .claude/skills/nuscale-monitor/SKILL.md AGENTS.md
```
Expected: 4 个文件路径都列出。

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/memory-flash-monitor/SKILL.md .claude/skills/oklo-monitor/SKILL.md .claude/skills/nuscale-monitor/SKILL.md AGENTS.md
git commit -m "feat: wire monitor hand-off pointers + AGENTS index for event-impact-estimation"
```

---

## Task 4: 验证（3 个代表性事件试跑）

skill 是 prompt 而非代码，验证 = 用代表性事件试跑看输出是否合理。`scripts/monitor_registry.py` 已单独自测通过（list-urls / dedup）。

- [ ] **Step 1: 确认 events/macro-events 注册表脚手架可用**

Run（自检脚本对新目录可正常初始化/读取）：
```bash
mkdir -p events/macro-events/events
printf '{"events": []}' > events/macro-events/analyzed_events.json
printf '# 宏观事件传导链分析索引\n\n| 日期 | 事件 | 大盘净影响 | 文件 |\n|------|------|-----------|------|\n' > events/macro-events/index.md
python3 scripts/monitor_registry.py --dir events/macro-events --list-urls
```
Expected: 无报错，输出为空（0 条 URL）。

- [ ] **Step 2: 试跑事件 A —— 美光财报毛利率超高（内存周期原型）**

在会话中触发 skill：提示语 `分析美光财报毛利率大涨的连锁影响`。
人工检查输出是否：
- 命中"原型 1 内存·存储周期反转"
- 利润池重分布写出"利润向上游存储集中"
- 传导链含"整机厂毛利压缩 → 消费电子承压"
- watchlist 表里小米标为**利空**、给信心 + 关键假设
- 大盘净影响有方向 + 信心
- 报告落到 `events/macro-events/events/`，飞书段命令完整（缺 .env 时静默跳过）

- [ ] **Step 3: 试跑事件 B —— Fed 超预期鹰派 / CPI 爆表（利率冲击原型）**

提示语 `CPI 大超预期，Fed 转鹰，对我持仓的影响`。
检查：命中"原型 3"，OKLO（零营收高β）被标为放大**利空**，方法论 5 步齐全。

- [ ] **Step 4: 试跑事件 C —— 苹果宣布涨价（龙头涨价转嫁原型）**

提示语 `苹果宣布全线涨价，这事怎么传导`。
检查：命中"原型 2"，利润链重分配判断清晰，无定价权方受损逻辑成立。

- [ ] **Step 5: 验证"不够大型"降级**

提示语 `某小盘股今天发了个普通公告`。
检查：skill 触发量级闸门，**明确说明未达跨板块量级、建议改用单标的分析**，不硬编传导链。

- [ ] **Step 6: 清理试跑产物（若不保留）+ Commit 验证记录**

如试跑产物仅为验证，按需清理 `events/macro-events/` 下的测试文件；保留目录脚手架。

```bash
git add events/macro-events/ docs/superpowers/plans/2026-06-26-event-impact-estimation.md
git commit -m "test: validate event-impact-estimation on representative events; scaffold macro-events dir"
```

---

## Self-Review（已执行）

**Spec 覆盖**：spec §3 形态→Task1；§4 方法论→Task1 Step2；§5 原型库(8)→Task2；§6 工作流→Task1；§7 数据流/复用(monitor_registry/feishu)→Task1 Step2 + Task4 Step1；§8 输出模板→Task1 Step2；§9 monitor 衔接→Task3；§10 边界降级→Task1 + Task4 Step5；§11 硬约束→Task1；§12 验证(3事件)→Task4。全部有对应任务。

**占位扫描**：输出模板内的 `[...]` 是 skill 运行时填充的有意占位，非计划占位；其余步骤均含具体命令/内容/校验期望。

**类型/命名一致**：skill 名 `event-impact-estimation`、目录 `events/macro-events/`、复用 `scripts/monitor_registry.py --dir events/macro-events`、原型字段六项——全文一致。
