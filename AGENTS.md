# 个人股票研究项目

个人投资研究工作台，覆盖美股/港股/A 股。核心能力：多维度股票分析、行业事件监控、短期走势预测与复盘。

---

## 目录结构

```
stock/
├── docs/                   # 基础知识文档
│   └── fundamentals/       # 市场驱动因素等基础概念
├── events/                 # 行业事件分析（按标的/主题分目录）
│   ├── oklo/
│   ├── xiaomi/
│   ├── memory-flash/
│   ├── us-israel-iran/
│   └── ...
├── experience/             # 实战复盘记录
│   └── <公司名>/           # 每次操作的得失总结
├── watchlist/              # 关注股票清单
├── flow/                   # 行情监控与预测系统（Python）
├── scripts/                # 辅助脚本
├── research/               # 研究报告：单只标的(stock/) + 行业研究(AI/半导体/消费电子等)
│   └── stock/              # 单只标的深度报告（oklo.md, NuScale-Power.md 等）
├── GLOSSARY.md             # 术语表
└── AGENTS.md               # 本文件：项目索引
```

---

## Skills 索引

### 分析框架

| Skill | 用途 |
|-------|------|
| `stock-analysis-framework` | 四维度分析基础框架（消息面/基本面/技术面/竞争格局），其他分析类 skill 的基础规范 |
| `stock-research` | 单只股票深度研究报告，输出到 `research/stock/` |
| `event-impact-estimation` | 大型事件跨板块传导链分析，落到 watchlist，输出到 `events/macro-events/` |

### 事件监控

| Skill | 监控标的 |
|-------|---------|
| `oklo-monitor` | Oklo Inc.（NYSE: OKLO）核微反应堆 |
| `xiaomi-monitor` | 小米集团（01810.HK） |
| `tencent-music-monitor` | 腾讯音乐（TME / 1698.HK） |
| `memory-flash-monitor` | 内存/闪存行业（Samsung/Hynix/Micron/YMTC 等） |
| `nuscale-monitor` | NuScale Power（SMR 小型模块核电） |
| `china-policy-monitor` | 中国政策动向 |
| `us-israel-iran-monitor` | 美以伊冲突与中东地缘政治 |

### 预测与复盘

| Skill | 用途 |
|-------|------|
| `stock-forecast` | 小米 & 腾讯音乐当日/次日走势预测 |
| `forecast-review` | 预测结果复盘，对比实际走势，输出准确率反思 |

### 通知

| Skill | 用途 |
|-------|------|
| `feishu-notify` | 将监控/分析结果推送到飞书 |

---

## 关键文档

- [`GLOSSARY.md`](GLOSSARY.md)：项目共享术语表，遇到陌生缩写先查这里
- [`docs/fundamentals/us-market-drivers.md`](docs/fundamentals/us-market-drivers.md)：影响美股大盘的核心驱动因素分类
- [`watchlist/`](watchlist/)：当前关注的股票清单

---

## 分析原则速查

详见 `stock-analysis-framework` skill，核心硬约束：

1. 数据必须可溯源，不确定标"待核实"
2. 区分事实与判断
3. 不预测具体价格，给区间和方向
4. 短期（技术/情绪主导）与中长期（基本面主导）分开论述
5. 拒绝"必涨"、"躺赚"等 FOMO 话术

> 本项目所有分析仅基于公开信息，不构成投资建议。
