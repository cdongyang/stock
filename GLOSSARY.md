# 术语表（GLOSSARY）

**用途**：本项目各份分析报告共享的术语参考。遇到陌生缩写 / 行业概念时优先查此表。
**维护原则**：只收录"在实际分析中出现过 / 会影响判断"的术语；过时或已无关的条目应删除，而不是堆积。

---

## 📑 目录

1. [核能 / 能源](#1-核能--能源)
2. [AI / 半导体 / 算力](#2-ai--半导体--算力)
3. [宏观经济 / 货币政策](#3-宏观经济--货币政策)
4. [贸易 / 关税 / 地缘](#4-贸易--关税--地缘)
5. [市场结构 / 技术面](#5-市场结构--技术面)
6. [信用 / 融资 / 财务](#6-信用--融资--财务)
7. [交易所 / 指数 / 板块](#7-交易所--指数--板块)

---

## 1. 核能 / 能源

| 术语 | 全称 / 含义 | 说明 |
|------|-----------|------|
| **SMR** | Small Modular Reactor（小型模块化反应堆） | 单机容量 < 300 MWe 的核反应堆，工厂预制、卡车运输、现场组装。对比传统 1000+ MWe 大堆，优势是周期短、选址灵活、适合数据中心 / 偏远地区。代表公司：NuScale（NYSE: SMR）、Oklo（NYSE: OKLO）、X-Energy |
| **LWR** | Light Water Reactor（轻水堆） | 目前全球最主流的商用堆型（含 PWR 压水堆、BWR 沸水堆），用普通水做冷却剂和慢化剂 |
| **HTGR** | High Temperature Gas-cooled Reactor（高温气冷堆） | 使用氦气冷却，出口温度 700-950°C，适合制氢、工业供热。X-Energy 和中国华能石岛湾是代表 |
| **MSR** | Molten Salt Reactor（熔盐堆） | 使用液态氟化盐作为冷却剂 / 燃料载体，常压运行，理论安全性高。TerraPower、Copenhagen Atomics 在推 |
| **TRISO** | Tri-structural Isotropic particle fuel | 多层包覆颗粒燃料，被称为"最坚固的核燃料"，用于 HTGR/SMR |
| **HALEU** | High-Assay Low-Enriched Uranium（高丰度低浓铀） | 丰度 5-20% 的浓缩铀，比常规商用燃料（3-5%）更高，是大部分先进反应堆设计的刚需。美国目前高度依赖俄罗斯供应，成为产业链瓶颈 |
| **GWe / MWe** | Gigawatt electric / Megawatt electric | **电**功率，注意与热功率 MWth 的区别（热效率通常 33%） |
| **PPA** | Power Purchase Agreement（购电协议） | 发电方与买方（如数据中心、工业客户）签署的长期售电合同。SMR 项目估值高度依赖 PPA 条款 |
| **容量因子** | Capacity Factor | 实际发电量 / 理论最大发电量。核电容量因子通常 > 90%，远高于风（35%）/ 光伏（25%） |
| **OPEC+** | OPEC + 俄罗斯等非 OPEC 产油国 | 决定全球原油供给节奏的最大卡特尔联盟 |
| **Brent / WTI** | 两大原油基准 | Brent = 北海布伦特（欧洲 / 全球定价）；WTI = 西德克萨斯中质油（美国）。一般 Brent 比 WTI 高 $3-5 |
| **霍尔木兹海峡** | Strait of Hormuz | 波斯湾出口咽喉，约 20% 全球原油海运 + 1/3 LNG 经过。封锁会立即推升国际油价 |

---

## 2. AI / 半导体 / 算力

| 术语 | 全称 / 含义 | 说明 |
|------|-----------|------|
| **Mag7** | Magnificent 7 | 美股七大科技巨头：AAPL / MSFT / GOOGL / AMZN / META / NVDA / TSLA。市值约占 S&P 500 的 30%+ |
| **Hyperscaler** | 超大规模云厂商 | 指 AWS / Azure / GCP，有时 + Meta / Oracle。衡量 AI CAPEX 的核心口径 |
| **Neocloud** | 新型 GPU 云 | 专门租赁 AI 算力的新兴云服务商，代表：CoreWeave、Lambda、Nebius、Crusoe。通常高杠杆、单一客户集中 |
| **Stargate** | OpenAI 主导的数据中心计划 | OpenAI + Oracle + SoftBank 宣布的 ~$500B、10GW 级数据中心项目，是"AI 循环融资"话题的核心 |
| **HBM** | High Bandwidth Memory（高带宽内存） | 通过 TSV 硅通孔堆叠的 DRAM，AI GPU 的标配。HBM3 / HBM3E / HBM4 代际差异大，供应集中在 SK hynix / Samsung / Micron |
| **EUV** | Extreme Ultraviolet Lithography（极紫外光刻） | 7nm 以下制程必需的光刻技术，全球仅 ASML 能制造 EUV 光刻机，单台 ~$2 亿 |
| **ASIC** | Application-Specific Integrated Circuit（专用集成电路） | 为特定应用定制的芯片，如 Google TPU、Meta MTIA。相比 GPU 更省电但灵活性低。Broadcom（AVGO）、Marvell 是主要代工方 |
| **GPU / dGPU** | Graphics Processing Unit / discrete GPU | 训练 / 推理 AI 的通用并行算力。NVDA 主导 |
| **NPU / TPU** | Neural / Tensor Processing Unit | 专门做神经网络计算的 AI 加速器 |
| **Hopper / Blackwell / Rubin** | NVIDIA 架构代号 | H100/H200 = Hopper；B100/B200 = Blackwell；2026-2027 将推出 Rubin |
| **LLM** | Large Language Model（大语言模型） | GPT、Claude、Gemini 等基于 Transformer 的生成式 AI 底座 |
| **Agentic AI** | 智能体 AI | 能自主规划、调用工具、完成多步任务的 AI 应用形态，2025-2026 年的主力叙事 |
| **Training / Inference** | 训练 / 推理 | AI 模型的两大阶段。训练一次性、算力密集；推理重复性、对延迟敏感。推理需求被认为会长期超过训练 |
| **Token** | AI 输入输出的最小计费单位 | 1 token ≈ 0.75 英文单词。定价以 "每百万 token" 计 |
| **Foundry** | 晶圆代工厂 | 不设计芯片、只负责制造。TSMC / Samsung Foundry / Intel Foundry / SMIC |
| **Fab** | Fabrication Plant | 晶圆工厂，一座现代 Fab 投资 $200-$400 亿 |
| **wspm** | Wafer Starts Per Month | 衡量 Fab 产能的行业口径 |
| **SMIC / 华虹** | 中国最大两家晶圆代工 | 中芯国际（0981.HK / 688981.SH）、华虹（1347.HK / 688347.SH）。是中国半导体自主可控核心标的 |
| **Liquid Cooling** | 液冷 | AI 机柜功率密度从 10kW 飙升到 100+ kW 后，风冷失效，必须液冷。受益股：Vertiv（VRT）、台达 |
| **Colocation** | 第三方数据中心 | 业主出租机房空间 / 电力 / 制冷。代表：Digital Realty（DLR）、Equinix（EQIX） |

---

## 3. 宏观经济 / 货币政策

| 术语 | 全称 / 含义 | 说明 |
|------|-----------|------|
| **Fed / FOMC** | Federal Reserve / Federal Open Market Committee | 美联储 / 联邦公开市场委员会。FOMC 一年 8 次会议决定利率 |
| **Fed Funds Rate** | 联邦基金利率 | 银行间隔夜拆借利率，美联储货币政策的主工具。2026/4 当前目标 3.50%-3.75% |
| **SEP** | Summary of Economic Projections | Fed 季度发布的经济预测（GDP / 失业率 / 通胀 / 利率点阵图） |
| **点阵图 (Dot Plot)** | SEP 中 FOMC 委员对未来利率的匿名预测 | 市场最关注的前瞻指标之一 |
| **QE / QT** | Quantitative Easing / Tightening | 量化宽松 / 紧缩，通过买卖国债和 MBS 调节流动性 |
| **CPI / Core CPI** | Consumer Price Index（消费者物价指数） | CPI = 全项目；Core = 剔除食品和能源（更稳定） |
| **PCE / Core PCE** | Personal Consumption Expenditures | **Fed 的首选通胀指标**。Core PCE 目标 2.0% |
| **GDP** | Gross Domestic Product | 国内生产总值。Fed 模型常用 **实际 GDP** 环比年化 |
| **NFP** | Non-Farm Payrolls（非农就业） | 每月第一个周五公布，就业市场最关键数据 |
| **失业率 (U-3)** | 标准失业率口径 | 还有 U-6（含打零工、想工作但未找）口径更广 |
| **滞胀 (Stagflation)** | Stagnation + Inflation | 增长停滞 + 通胀上行的组合，货币政策最难应对的情境 |
| **实际利率** | Real Interest Rate | 名义利率 - 通胀。黄金与实际利率强负相关 |
| **收益率曲线倒挂** | Yield Curve Inversion | 短端利率 > 长端（如 2Y > 10Y），历史上经济衰退的领先指标 |
| **BEI** | Break-Even Inflation | 通胀保护债（TIPS）隐含的通胀预期 |

---

## 4. 贸易 / 关税 / 地缘

| 术语 | 全称 / 含义 | 说明 |
|------|-----------|------|
| **IEEPA** | International Economic Emergency Powers Act | 1977 年授权，允许总统在"国家紧急状态"下实施经济制裁 / 关税。Trump 第二任期关税主要依据。**2026/2 最高法院裁定不能用于征收关税** |
| **Section 122 Trade Act** | 1974 年贸易法第 122 条 | 允许总统为应对"重大逆差"征收最高 15% 关税，**150 天** 期限。Trump 在 IEEPA 失效后的替代工具 |
| **Section 301 Trade Act** | 1974 年贸易法第 301 条 | USTR 认定外国"不公平贸易做法"后的报复工具。2018 年中美贸易战的法律基础 |
| **Section 232** | 1962 年贸易扩展法第 232 条 | 以"国家安全"为由对特定商品加关税（如钢铁、铝、半导体、药品） |
| **Liberation Day** | 2025/4/2 Trump 宣布的全球对等关税 | 引发 S&P 500 七周跌近 20%，后多数条款被撤回 |
| **USMCA** | 美墨加协定 | NAFTA 升级版，2020 年生效 |
| **Entity List** | 美国商务部"实体清单" | 被列入的企业购买美国技术需申请许可证。华为、SMIC、中芯等在列 |
| **BIS** | Bureau of Industry and Security | 美国商务部工业与安全局，负责出口管制执行 |
| **AI Overwatch Act** | 2026 年国会提案 | 赋予国会 30 天否决 AI 芯片出口许可权，可能禁售 Blackwell 及以上 |
| **稀土** | Rare Earth Elements | 17 种金属，电动车 / 风电 / 国防 / 半导体必需。中国产量占全球 70%，冶炼占 85% |

---

## 5. 市场结构 / 技术面

| 术语 | 全称 / 含义 | 说明 |
|------|-----------|------|
| **VIX** | CBOE Volatility Index | "恐慌指数"，由 S&P 500 期权隐含波动率计算。< 15 平静；> 30 恐慌 |
| **60/40 组合** | 60% 股票 + 40% 债券 | 传统平衡组合。2022 和 2026 年股债同向，策略失效 |
| **CAPE / Shiller PE** | Cyclically Adjusted PE | 价格 / 过去 10 年平均实际 EPS。消除周期扰动。历史均值 ~17，> 30 通常意味着长期回报疲弱 |
| **PE / PB / PS / PEG** | 市盈率 / 市净率 / 市销率 / PE 增长比 | PEG < 1 通常被认为低估 |
| **Forward PE** | 前瞻市盈率 | 用未来 12 月预期 EPS 计算，反映市场对未来的定价 |
| **Earnings Yield** | EPS / Price = 1 / PE | 股票"利率"，常与 10Y 国债比较（Fed Model） |
| **MA20 / 50 / 200** | 20 / 50 / 200 日移动均线 | 常用趋势指标。股价站上 200MA 通常视为多头 |
| **MACD** | Moving Average Convergence Divergence | 基于快慢均线差的趋势 / 动能指标 |
| **RSI** | Relative Strength Index | 0-100 区间。> 70 超买；< 30 超卖；50 是多空分水岭 |
| **背离 (Divergence)** | 价格新高 / 低，但指标未创新高 / 低 | 趋势衰竭信号 |
| **缺口 (Gap)** | 开盘价与前收盘价存在跳空 | 分普通缺口 / 突破缺口 / 竭尽缺口 |
| **支撑 / 压力** | Support / Resistance | 价格多次止跌 / 止涨的水平线 |
| **相对强度 (RS)** | 个股走势 / 大盘走势 | RS 创新高 = 跑赢大盘 |
| **多头 / 空头** | Long / Short | 买入看涨 / 做空看跌 |
| **T+1 / T+0** | 交易后第 1 个 / 当天结算 | A 股 T+1（买入次日才能卖）；美股 2024/5 起改 T+1 结算但仍可日内回转 |
| **涨跌停** | Price Limit | A 股日内涨跌幅限制（主板 ±10%，创业板 / 科创板 ±20%）。美股无涨跌停但有熔断 |
| **ADR** | American Depositary Receipt | 美国存托凭证，让非美国公司在美股交易。如阿里、台积电 ADR |

---

## 6. 信用 / 融资 / 财务

| 术语 | 全称 / 含义 | 说明 |
|------|-----------|------|
| **CAPEX / OPEX** | Capital Expenditure / Operating Expenditure | 资本开支 / 运营开支。AI 行业 CAPEX 已达 OCF 的 94% |
| **FCF** | Free Cash Flow（自由现金流） | 经营现金流 - CAPEX。真正可分配给股东的钱 |
| **OCF** | Operating Cash Flow | 经营现金流 |
| **EBITDA** | 息税折旧摊销前利润 | 常用但易被美化，不等于现金流 |
| **毛利率 / 净利率 / 净利润率** | Gross / Net Margin | 三大盈利能力指标 |
| **ROE / ROIC** | Return on Equity / Invested Capital | 股东权益 / 投入资本回报率 |
| **Beat / Miss / In-line** | 财报与分析师一致预期比较 | Beat = 超预期；Miss = 不及预期 |
| **Guidance** | 管理层业绩指引 | 常常比财报本身更影响股价 |
| **RPO** | Remaining Performance Obligations（剩余履约义务） | 已签合同但尚未确认收入的部分。SaaS / 云计算 / AI 基建的关键订单指标。**Oracle Q3 FY26 RPO $553B（+325% YoY）是其 AI 故事的核心** |
| **Bookings / Billings** | 订单额 / 开票额 | SaaS 行业前瞻指标 |
| **SBC** | Stock-Based Compensation | 股权激励支出，常常被调整掉但是真实成本 |
| **投资级 / 垃圾级** | Investment Grade / High Yield | 标普评级 BBB- 以上为投资级；以下为垃圾级（High Yield） |
| **Baa2 / BBB** | Moody's / S&P 评级 | 投资级最后一档。Oracle 当前 Baa2，被 Moody's 负面展望 |
| **CDS** | Credit Default Swap | 信用违约互换，衡量违约风险的衍生品 |
| **私募信贷** | Private Credit | 非银行、非公开债券的直接贷款。2025-2028 预计 AI 数据中心一半资金来自此渠道 |
| **ATM 增发** | At-the-Market Offering | 按市价持续抛售新股融资。通常被市场视为稀释信号 |
| **SAFE** | Simple Agreement for Future Equity | 创业公司常用融资工具，未来估值不确定时的"期权式"投资 |
| **稀释** | Dilution | 新股发行或期权行权导致每股价值下降 |
| **回购 (Buyback)** | Share Repurchase | 公司用现金回购自家股票，通常视为股东回报的信号 |

---

## 7. 交易所 / 指数 / 板块

| 术语 | 含义 | 说明 |
|------|------|------|
| **NYSE / NASDAQ** | 纽约证券交易所 / 纳斯达克 | NYSE 偏传统行业；NASDAQ 偏科技 |
| **S&P 500 / SPX** | 标普 500 | 美股大盘最常用基准，市值加权 |
| **Nasdaq 100 / NDX** | 纳斯达克 100（QQQ 跟踪） | 剔除金融的 100 大纳斯达克非金融股 |
| **Dow 30 / DJIA** | 道琼斯工业指数 | 30 只成分股，价格加权（不常用） |
| **Russell 2000 / IWM** | 罗素 2000 | 小盘股基准，对利率最敏感 |
| **VIX** | 波动率指数 | 见第 5 节 |
| **11 个 GICS 板块** | | 科技（XLK）、通信（XLC）、医疗（XLV）、金融（XLF）、可选消费（XLY）、必需消费（XLP）、能源（XLE）、工业（XLI）、材料（XLB）、地产（XLRE）、公用事业（XLU） |
| **恒生指数 / 恒生科技** | HSI / HSTECH | 港股主板 / 科技板块基准 |
| **恒指 ETF** | 2800.HK / 3033.HK | 恒指 / 恒生科技 ETF |
| **沪深 300 / 中证 500 / 中证 1000** | | A 股大盘 / 中盘 / 小盘基准 |
| **科创板 / 创业板 / 北交所** | | A 股分层：科创板（688xxx）偏硬科技；创业板（300xxx）偏创新；北交所偏专精特新 |

---

## 附录：常见 Ticker 速查

### 美股 AI / 算力
- **NVDA** NVIDIA | **AMD** AMD | **AVGO** Broadcom | **TSM** 台积电 ADR
- **MU** Micron | **ASML** ASML | **LRCX** Lam Research | **KLAC** KLA | **AMAT** Applied Materials
- **ORCL** Oracle | **CRWV** CoreWeave | **NBIS** Nebius | **VRT** Vertiv

### 美股超大规模云厂
- **MSFT** Microsoft | **GOOGL** Alphabet | **AMZN** Amazon | **META** Meta | **AAPL** Apple

### 美股核能 / SMR
- **SMR** NuScale Power | **OKLO** Oklo | **BWXT** BWX Technologies
- **CEG** Constellation Energy | **VST** Vistra | **NRG** NRG Energy
- **CCJ** Cameco | **UEC** Uranium Energy | **URNM** 铀矿 ETF

### 美股能源 / 传统
- **XOM** Exxon | **CVX** Chevron | **COP** ConocoPhillips | **SLB** Schlumberger | **OXY** Occidental

### 美股国防 / 航天
- **LMT** Lockheed | **RTX** Raytheon | **NOC** Northrop Grumman | **GD** General Dynamics | **PLTR** Palantir

### 港股 / A 股
- **0700.HK** 腾讯 | **9988.HK** 阿里 | **3690.HK** 美团 | **1810.HK** 小米
- **600519.SH** 贵州茅台 | **300750.SZ** 宁德时代 | **688981.SH** 中芯国际

---

## 使用规范

- 本文档术语首次出现在分析报告中时，建议后括号标注中文或英文简称，例如：`远期市盈率（Forward PE）`
- 如果遇到本表未收录的术语，补充时请：**放入对应分类 → 给一句话解释 → 如有代表公司标注 ticker**
- 对于有争议 / 定义不稳定的术语（如 "Neocloud" 的外延），在解释中明确"本项目采用的定义"
