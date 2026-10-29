---
name: sndk-monitor
description: >
  Monitor and analyze recent events related to Sandisk Corp. (闪迪, NASDAQ: SNDK), the NAND flash company spun off from Western Digital, storing structured impact analyses in the `events/sndk/` directory of the current project. Use this skill whenever the user asks to track, monitor, analyze, or research Sandisk / SNDK news, earnings, NAND pricing impact on Sandisk, enterprise SSD demand, or any activity involving 闪迪 — even if they don't use the word "monitor". Triggered by: "分析SNDK最新事件", "闪迪动态", "追踪Sandisk", "SNDK news", "Sandisk earnings", "sndk monitor", or any request involving Sandisk intelligence gathering. For industry-wide NAND/DRAM events that do not directly name Sandisk, use memory-flash-monitor instead.
---

# Sandisk (SNDK) 事件监控与分析 Skill

搜索 Sandisk Corp.（NASDAQ: SNDK）近期事件，逐条分析对公司的影响，结构化存盘，并去重避免重复分析。

Sandisk 是纯 NAND 闪存公司（2025 年从 Western Digital 分拆），与 Kioxia 有合资工厂（JV）。股价对 NAND 合约价、AI 数据中心存储需求、市场情绪高度敏感，波动大。

**知识库**：目前没有 `research/stock/sandisk.md`。分析时参考 `experience/sandisk.md`（操作观察）和 `research/` 下现有存储/半导体行业资料；缺失的数据标"待核实"，不要编造。

**与 memory-flash-monitor 的边界（严格分开）**：
- 事件**直接点名 Sandisk / SNDK**（财报、指引、评级、产品、JV、管理层、股价异动）→ 记到本 skill（`events/sndk/`）
- 行业级事件（NAND/DRAM 价格趋势、三星/海力士/美光动态、出口管制等，未直接涉及 Sandisk）→ 属于 `memory-flash-monitor`，本 skill 跳过，不重复记录

---

## Step 1 — 建目录

确保以下路径存在（不存在则创建）：

```
events/sndk/
├── index.md              ← 已分析事件索引
├── analyzed_events.json  ← 去重注册表
└── events/               ← 每个事件一个 .md 文件
```

`analyzed_events.json` 初始化为：
```json
{"events": []}
```

`index.md` 初始化为：
```markdown
# Sandisk (SNDK) 事件分析索引

| 日期 | 标题 | 影响评级 | 文件 |
|------|------|----------|------|
```

---

## Step 2 — 搜索近期事件

用多个 query 撒网，跑 3–5 个：

- `Sandisk SNDK stock news latest 2026`
- `Sandisk earnings guidance NAND 2026`
- `Sandisk enterprise SSD AI data center demand`
- `Sandisk Kioxia joint venture update`
- `Sandisk analyst upgrade downgrade price target`
- `NAND flash contract price TrendForce Sandisk`

每条结果记录：title、date（ISO，没有则写约数）、source、url、summary（1–2 句）。

---

## Step 3 — 去重

```bash
python3 scripts/monitor_registry.py --dir events/sndk --list-urls
```

- 与已有 URL 逐条比对；标题相似度 >80% 也视为重复
- 只处理**全新**事件；全部已分析则报告并停止
- 拿不准时跳过

---

## Step 4 — 分析每个新事件

每个事件产出：

- **What happened**：事实摘要（2–4 句）
- **Direct impact**：对 Sandisk 收入、毛利率、产能、指引的直接影响
- **Strategic implications**：对企业级 SSD 布局、与 Kioxia JV、AI 存储需求中地位的长期影响
- **Investor angle**：对 SNDK 股价、情绪、估值的影响（短期情绪与中长期基本面分开论述）
- **Risk / Opportunity**：净正面 / 负面 / 中性及原因
- **Impact rating**：🔴 High Negative / 🟡 Neutral / 🟢 High Positive / ⚪ Low Impact

必看维度：
- **NAND 价格与供需**：合约价涨跌、库存、供给纪律（减产/扩产）
- **产品结构**：企业级 SSD / 数据中心占比提升是毛利率改善的关键
- **AI 需求**：AI 训练/推理对大容量 SSD 的拉动
- **财报与指引**：营收、毛利率、capex、下季度指引 vs 市场预期
- **Kioxia JV**：产能分配、合约续期、技术路线（BiCS）
- **竞品**：三星、海力士、美光、Kioxia、长江存储的动作是否挤压 SNDK
- **资金面**：评级调整、机构持仓、大户/散户情绪导致的异常波动（参考 `experience/sandisk.md`）

分析遵循 `stock-analysis-framework`：数据可溯源、区分事实与判断、不预测具体价格、拒绝 FOMO 话术。

---

## Step 5 — 写 event 文件

路径：`events/sndk/events/YYYY-MM-DD_<slug>.md`

```markdown
# [Event Title]

**日期 / Date:** YYYY-MM-DD  
**来源 / Source:** [Source Name](URL)  
**影响评级 / Impact Rating:** 🟢 High Positive *(or whichever applies)*

---

## 事件摘要 / Summary

[2–4 句事实描述]

---

## 直接影响 / Direct Impact

[对收入、毛利率、产能、指引的直接影响]

---

## 战略意义 / Strategic Implications

[对企业级 SSD、Kioxia JV、AI 存储定位的长期影响]

---

## 投资者视角 / Investor Angle

[对 SNDK 股价/情绪/估值的影响；短期与中长期分开]

---

## 风险与机遇 / Risk & Opportunity

**Overall:** [Positive / Negative / Neutral]  
[1–3 句净评估]
```

---

## Step 6 — 更新注册表和索引

把新事件写成 JSON 数组文件（字段：url / title / date / file / impact_rating，`analyzed_at` 由脚本自动补）：

```bash
python3 scripts/monitor_registry.py --dir events/sndk --add $TMPDIR/sndk_new_events.json
```

`events/sndk/index.md` 追加一行：
```markdown
| YYYY-MM-DD | [Event title](events/YYYY-MM-DD_slug.md) | 🟢 High Positive | [link](events/YYYY-MM-DD_slug.md) |
```

---

## Step 7 — 向用户报告

```
## 本次监控结果 / Monitoring Results

发现 X 个新事件，已跳过 Y 个重复事件。

### 新分析事件：
1. **[事件标题]** — [Impact Rating] — `events/sndk/events/...md`

所有分析已保存至 `events/sndk/` 目录。
```

---

## Step 8 — 飞书通知（如已配置）

```bash
python3 scripts/feishu_notify.py \
  --title "💾 Sandisk (SNDK) 事件监控报告" \
  --item "发现 X 个新事件，跳过 Y 个重复" \
  --item "🟢 [事件标题1]" \
  --item "🔴 [事件标题2]" \
  --footer "📁 详情: events/sndk/"
```

- 无新事件：`--item "✅ 今日无新事件（已跳过 Y 个重复）"`
- `scripts/feishu_notify.py` 或 `.env` 缺失时静默跳过

---

## Important notes

- **来源可信度**：优先 Sandisk IR、SEC 文件（8-K/10-Q）、Reuters、Bloomberg、TrendForce；低可信来源要标注
- **价格数据**：NAND 合约价、股价等不确定的数字标"待核实"
- **小盘/高波动提示**：SNDK 股价波动大、易受情绪与资金操盘影响，分析时单独说明"基本面 vs 资金面"
- **去重优先**：拿不准就跳过
- **跨板块移交**：若事件具跨板块传导性（AI capex 变化、存储周期拐点、大额指引调整），移交 `event-impact-estimation` skill 做传导链分析
