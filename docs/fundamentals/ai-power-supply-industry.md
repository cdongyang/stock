# AI 供电行业深度分析（全球 · 含中国）

> 产出方式：`deep-research` 工作流（5 角度 → 27 源 → 122 条声明 → 对抗式验证）+ 人工综合。
> 生成日期：2026-06-27。是 `us-market-drivers.md`（静态宏观）之上的"AI 电力产业链"专题层。
> 关联原型：`event-archetypes.md` 原型4（Mega-cap AI capex）、原型3（利率/CPI）、原型9（油价下行）。

---

## 0. 数据可信度说明（必读）

本报告每条事实按验证强度分三档标注，**严格区分事实与判断**：

- **[已验证]** — 经 3 票对抗式验证通过（3-0），**信心高**。
- **[源支持·未独立验证]** — 来自可信来源，但本轮验证因触及会话限额未完成对抗投票（0-0 弃票，**非被证伪**），**信心中**；财报/政府站点类一手源信心略高，二手转述信心中低。
- **[判断]** — 笔者基于事实的推断，附独立信心等级。

⚠️ **本轮已被证伪、已剔除/纠偏的流行说法**：
1. "AI 数据中心吃掉了北美未来用电增长的大部分" —— **被证伪（1-2）**。IEA 数据显示数据中心增长仅占全球用电总增长 **不到 10%**（见 §1）。真正的矛盾是**局部高度集中**，不是全国性缺电。
2. "数据中心扩张是 2020 年以来美国变压器需求飙升的首要驱动" —— **被弱证伪（1-0）**，属过度归因；制造业回流 + 电气化 + 老旧设备替换同样是主因。

---

## 1. 需求侧：AI 数据中心电力需求曲线

| 指标 | 数据 | 来源/验证 |
|------|------|-----------|
| 全球数据中心用电 | 2024 约 **415 TWh**（占全球 ~1.5%）→ 2030 翻倍至 **~945 TWh**（~3%），年增 ~15%，是其他部门增速的 4 倍+ | [已验证] IEA |
| 美国数据中心用电 | 2024 **177–192 TWh** → 2030 **380–790 TWh**（低-高情景），较 EPRI 旧估高 ~60% | [已验证] EPRI |
| 占美国电力比重 | 2024 **4–5%** → 2030 **9–17%** | [已验证] EPRI |
| 中美增量占比 | 到 2030 合计占全球增量 **~80%**；美 +240 TWh(+130%)、中 +175 TWh(+170%) | [已验证] IEA |
| 北美电网峰值 | 夏峰 10 年（2026-2035）增 **>224 GW**，比上年同期预测高 **69%**；冬峰 +245 GW | [已验证] NERC LTRA 2025 |
| 超大厂 AI 资本开支 | Big Tech AI 支出计划达 **$725B** 量级 | [源支持] Tom's Hardware |

**关键纠偏 [已验证]**：数据中心负荷"地理高度集中"（不像电动车分散），即便占全国比例不高，**局部并网/可靠性压力极大**。2024-2030 数据中心仅贡献全球用电增长 <10%。
→ **[判断，信心中高]** 投资含义：受益最确定的不是"全国发电缺口"叙事，而是**局部瓶颈环节**（电网设备、就近电源、容量市场涨价）。

**PPA / 核电长协（供需直连，绕过电网排队）**：
- Meta 与 Constellation 签 **20 年 PPA**，包下伊利诺伊一座核电站全部产出 [源支持]。
- Meta 多方核电采购（TerraPower/Oklo/Vistra）最高 6.6 GW [源·信心低，原始源被标 unreliable]；其中 Oklo 1.2 GW 长协见 watchlist 既有研究。
- **[判断]** 超大厂愿为"确定性 + 零碳 + 24/7 基荷"付溢价 → 利润流向能锁定长协的现役核电运营商，定价权强。

---

## 2. 供给侧四环节

### 2.1 发电侧全谱

**[判断，信心中高] 利润分配主线**：短缺环境下，"快、确定、可调度"者拿定价权。按落地节奏分三层：

| 子赛道 | 核心玩家 | 兑现窗口 | 定价权/竞争格局 | 事实锚点 |
|--------|----------|----------|----------------|----------|
| 现役核电延寿/重启 | Constellation、Vistra | 2026-2028（即时） | **强**（PPA 锁价、稀缺基荷） | Meta-Constellation 20年PPA [源支持] |
| 天然气调峰 | GE Vernova、西门子能源 | 2026-2028 | **强**（设备瓶颈） | GE Vernova 燃机 backlog 达 **100 GW**、价格上涨 [源支持]；EPRI：现行政策下最低成本 favor 天然气，年新增 **6.6–13.7 GW** vs 历史均值 5.7 GW [已验证] |
| 先进核能/SMR | Oklo、NuScale、X-energy、Kairos、TerraPower | **2028-2030+**（期权） | 弱（预商业、未盈利） | Oklo 75MW Aurora 设计 [源支持]；TVA-ENTRA1 **6 GW / 6 堆** SMR 合作 [源支持] |
| 可再生/地热 | 光伏风电 + Fervo(地热) | 持续 | 中（需配储能） | — |

**[判断]** 可再生间歇性 → 单独难满足数据中心 24/7 基荷，**角色是"配储能 + 调峰气电"的组合件**，而非独立解；地热（Fervo）是小众但 24/7 的补充，信心低。

### 2.2 电网与输配瓶颈 —— **[判断，信心高] 当前 AI 供电最大的物理卡点**

| 卡点 | 数据 | 来源/验证 |
|------|------|-----------|
| 大型电力变压器 | 供给缺口 **30%**；成本自 2019 涨 **77%** | [已验证] Wood Mackenzie |
| 配电变压器 | 供给缺口 **6%**；成本涨 78–95% | [已验证] Wood Mackenzie |
| 变压器交付周期 | 延长至 **~4 年** | [源支持] pv-magazine |
| 并网排队 | 待并网发电+储能 **>2.2 TW**；申请到商运周期升至 **~5 年**（2008 年 <2 年） | [源支持·未验证] RMI |
| PJM 容量拍卖 | 清算价创纪录 **$333.44/MW-day**（连续第三次创纪录）；procured 145,777 MW，低于 20% 储备目标 5.2pp | [源支持·未验证] Utility Dive |
| 区域可靠性风险 | MISO（2027 升 Elevated / 2028+ High）、PJM（2026-28 Elevated / 2029+ High）、ERCOT、WECC-Basin 同步升级 | [已验证] NERC |

**[判断，信心高]** 变压器/开关设备/并网是"卖铲子"里最硬的瓶颈——产能扩张慢、订单能见度长、定价权强。这是**确定性最高、但 watchlist 未覆盖**的环节（标的如 GE Vernova、Eaton、西门子能源、ABB）。

### 2.3 储能

- **Fluence（FLNC）**：数据中心储能 pipeline 达 **12 GWh**、记录 backlog **$5.6B**、FY26 营收指引 $3.2–3.6B / 调整 EBITDA $40–60M、与超大厂签 2 份主供协议、预计 Q3 FY26 首张数据中心订单 [源支持·未独立验证，来自财报电话会]。
- **[源支持] 定位**：Fluence 对数据中心的价值在**电能质量管理（平抑 AI 负载瞬时波动）**，而非电芯本身——管理层视电芯为大宗商品。
- **市场**：电池储能装机预计 2027 翻倍至 **88.4 GW**，Tesla/BYD/CATL/Fluence 加速投资 [源支持]。
- **[判断，信心中]** 储能是 AI 供电的"缓冲层"——解决间歇性可再生 + AI 负载尖峰。但电芯环节高度依赖中国供应链（见 §3），**FEOC/关税政策是美国玩家的结构性变量**。

---

## 3. 中国维度

| 环节 | 要点 | 来源/验证 |
|------|------|-----------|
| 电网/特高压 | 国家电网"十五五"（2026-2030）固投预计 **~4 万亿元**（较十四五 +~40%）；跨区跨省输电能力 +30%，特高压直流支撑西部清洁能源外送 | [源支持·未验证] 国家能源局 |
| 储能产业链 | 宁德时代、比亚迪、阳光电源全球领先；中国电芯玩家受美 FEOC 政策约束仍图供美 | [源支持] energy-storage.news |
| 核电 | 中广核、中核稳步审批扩容（事实性，信心中） | — |
| 数据中心需求 | 中国数据中心用电 2030 +175 TWh（**+170%**，全球最快增速之一） | [已验证] IEA |

**[判断]** 中国是 AI 供电"全产业链自给"程度最高的经济体：特高压解决远距离输送、储能链全球成本最低、核电自主审批。瓶颈不在设备而在**电力市场化与跨区消纳机制**。

---

## 4. 产业链利润分布与投资主线 [判断]

**谁吃谁的利润（信心中高）**：短缺把利润推向**瓶颈环节**——
1. **设备瓶颈方**（变压器、燃气轮机）= 定价权最强、最确定，吃下游建设方的利润；
2. **稀缺基荷方**（现役核电）= 用长协锁定超大厂溢价；
3. **超大厂**（capex 买家）= 付溢价换确定性，但其 capex 强度决定整条链景气度（原型4）；
4. **预商业 SMR/部分储能** = 仍在烧钱/薄利阶段，靠远期预期定价，**估值波动先于基本面落地**。

**时间表分层（信心中）**：
- **2026-2028 兑现**：电网设备（变压器/开关）、燃气轮机、现役核电延寿/重启、电网级储能。
- **2028-2030 才落地**：SMR/微堆首堆商运、新建大型核电。

---

## 5. 落到 watchlist / 持仓

| 标的 | 与"AI供电"关系 | 判断 | 信心 | 关键假设 / 利好利空并列 |
|------|---------------|------|------|------------------------|
| **OKLO** | 发电侧·SMR（直接） | 🟡 中性偏多 · 高波动 | 中低 | **利好**：AI 核电需求 + 白宫政策 + 订单生态（TVA/Meta 长协）；**利空**：无 NRC 商运牌照、零营收、商业化 2028+、内部人减持、估值靠远期预期。**主驱动是里程碑事件而非行业β** |
| **SMR (NuScale)** | 发电侧·SMR（直接） | 🟡 中性偏多 · 高波动 | 中低 | **利好**：NRC 唯一已批设计（先发）、DOE 贷款信号、TVA 6GW 生态；**利空**：首堆 2028-2030、P/S ~100x 估值透支、集体诉讼、深度亏损 |
| **FLNC (Fluence)** | 储能（直接受益） | 🟢 利好为主 | 中 | **利好**：数据中心 pipeline/backlog 增长（源支持未验证）、电能质量管理定位稀缺、订单翻倍；**利空**：电芯依赖中国供应链 + FEOC 政策、毛利薄、Tesla/比亚迪竞争 |
| **Cerebras** | 算力侧 = 需求制造者（非供电方） | ⚪ 对本主题中性 | 中 | 它是**拉高电力需求的源头**而非供电标的；AI capex 强 → 其需求强（原型4 上游驱动），但不直接受益"供电"主线 |

**[判断，信心中高] 诚实提示**：
- 本主题**确定性最高的受益方（变压器/燃气轮机/现役核电：GE Vernova、Eaton、西门子能源、Constellation、Vistra）均不在 watchlist**；watchlist 里的 OKLO/SMR/FLNC 属于**高弹性、高波动的"期权式"表达**——赔率高但确定性低。
- OKLO 与 SMR **高度同涨同跌**（SMR 板块 β×2），分散效果弱，建议合计控制敞口（watchlist 既有提示 ≤5%）。
- FLNC 是三者中**当期基本面最实**的（有营收、有 backlog、有订单），但 stock-analysis-framework 要求不预测股价，这里只给方向：基本面顺风、政策（中国电芯）是最大变量。

---

## 6. 风险与会推翻判断的信号

1. **AI capex 降速**（超大厂资本开支指引下修）→ 整条链景气度回落（原型4 反向），SMR/储能高β首当其冲。
2. **利率高企/CPI 反弹** → 高久期、零营收的 SMR 杀估值（原型3）。
3. **"数据中心缺电"叙事回摆** → IEA 已提示数据中心仅占全球用电增长 <10%，若市场意识到瓶颈是局部而非总量，部分主题溢价可能回吐。
4. **SMR 许可/首堆延期** → OKLO 的 NRC 商运牌照、NuScale 首堆是决定性里程碑，延期则估值回调。
5. **储能政策**（FEOC、对华电池关税）→ 直接冲击 FLNC 成本与供应链。
6. **天然气/油价大幅波动** → 改变各电源经济性排序（关联原型9）。

---

## 7. 来源清单（按可信度）

**一手 / 高可信（[已验证] 主要来自这些）**
- [IEA — Energy demand from AI](https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai)
- [EPRI — Powering Intelligence](https://powering-intelligence.epri.com/executive-summary.html)
- [NERC LTRA 2025](https://www.nerc.com/globalassets/our-work/assessments/nerc_ltra_2025.pdf)
- [Wood Mackenzie — Transformer troubles](https://www.woodmac.com/news/opinion/transformer-troubles-manufacturing-and-policy-constraints-hit-us-transformer-supply/)
- [Fluence Q2 FY2026 财报电话会](https://www.fool.com/earnings/call-transcripts/2026/05/07/fluence-flnc-q2-2026-earnings-transcript/)
- [国家能源局](https://www.nea.gov.cn/20260130/f5870f4fe28744139406827434f3859c/c.html)
- [RMI — Interconnection reform](https://rmi.org/resources/interconnection-reform-ai-data-centers-generator-queues/)

**二手（[源支持]）**
- [Utility Dive — PJM 容量拍卖](https://www.utilitydive.com/news/pjm-interconnection-capacity-auction-data-center/808264/) / [数据中心成本](https://www.utilitydive.com/news/data-centers-pjm-capacity-auction/808951/)
- [Utility Dive — GE Vernova 燃机 backlog 100GW](https://www.utilitydive.com/news/ge-vernova-gas-turbine-backlog-hits-100-gw-as-prices-rise/818332/)
- [Utility Dive — Oklo 75MW 设计](https://www.utilitydive.com/news/oklo-75-mw-reactor-design-smr-nuclear/743578/)
- [DataCenterDynamics — Meta-Constellation 20年PPA](https://www.datacenterdynamics.com/en/news/meta-signs-20-year-ppa-with-constellation-for-entire-output-of-illinois-nuclear-power-plant/)
- [PowerMag — TVA-ENTRA1 6GW SMR](https://www.powermag.com/tva-entra1-sign-agreement-for-6-gw-six-plant-nuclear-smr-collaboration/)
- [pv-magazine — 变压器交期 4 年](https://pv-magazine-usa.com/2026/05/11/u-s-transformer-market-faces-severe-supply-constraints-as-lead-times-extend-to-four-years/)
- [Tom's Hardware — Big Tech AI $725B](https://www.tomshardware.com/tech-industry/big-tech/big-techs-ai-spending-plans-reach-725-billion)
- [GreenTechLead — 储能 2027 翻倍 88.4GW](https://greentechlead.com/renewable-energy/battery-storage-market-set-to-double-to-88-4-gw-by-2027-as-tesla-byd-catl-and-fluence-accelerate-investments-53589)
- [energy-storage.news — Fluence 订单翻倍](https://www.energy-storage.news/fluence-doubles-order-intake-expects-to-book-first-big-data-centre-deal-this-quarter/) / [中国 BESS 与 FEOC](https://www.energy-storage.news/chinese-bess-players-still-hope-to-supply-us-in-feoc-policy-environment/)

> **免责声明**：本分析基于公开信息与上述来源，不构成投资建议。标"源支持·未独立验证"者因深度研究工作流触及会话限额、未完成对抗式验证，请使用时自行复核。
