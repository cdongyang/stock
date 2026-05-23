# 富途实时资金流向走势图 设计文档

**日期**：2026-05-14  
**状态**：已确认

---

## 目标

从富途 OpenAPI 获取实时资金流向数据，以浏览器 ECharts 走势图展示，同时实现两套方案供效果对比：

- **方案A**：调用富途内置 `get_capital_flow` 接口轮询
- **方案B**：订阅逐笔成交（TICKER + QUOTE）实时推送，按个人操作规则分类主动买卖

---

## 目录结构

```
stock/
├── flow/
│   ├── config/
│   │   └── flow_watch.yaml      # 股票列表 + 服务器参数
│   ├── storage.py               # 共用 SQLite 存取层
│   ├── server.py                # FastAPI + WebSocket + 静态文件
│   ├── frontend/
│   │   └── index.html           # ECharts 前端（方案A/B 可切换对比）
│   ├── plan_a/
│   │   └── collector.py         # 轮询 get_capital_flow，写入 SQLite
│   └── plan_b/
│       ├── tick_handler.py      # 逐笔分类（成交价 vs 买一卖一）
│       └── collector.py         # 管理订阅 + 聚合 + WebSocket 推送
└── scripts/
    └── api/                     # 已有代码，不动
```

**启动方式**（三个终端并行）：

```bash
python -m flow.plan_a.collector   # 方案A采集
python -m flow.plan_b.collector   # 方案B采集
python -m flow.server             # Web服务
```

---

## 配置文件

`flow/config/flow_watch.yaml`：

```yaml
stocks:
  - code: US.OKLO
    name: Oklo
  - code: US.SMR
    name: NuScale

server:
  host: 127.0.0.1
  port: 8080

futu:
  host: 127.0.0.1
  port: 11111
```

---

## 数据存储

**文件**：`flow/data/flow.db`（运行时自动创建）

```sql
CREATE TABLE capital_flow (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL,          -- 如 US.OKLO
    minute      TEXT NOT NULL,          -- YYYY-MM-DD HH:MM
    source      TEXT NOT NULL,          -- 'plan_a' 或 'plan_b'
    buy_amount  REAL NOT NULL,          -- 主动买入金额
    sell_amount REAL NOT NULL,          -- 主动卖出金额
    net_flow    REAL NOT NULL,          -- buy - sell，正=流入 负=流出
    UNIQUE(code, minute, source)
);

CREATE INDEX idx_code_minute ON capital_flow(code, minute, source);
```

**`storage.py` 对外接口**：

```python
def upsert_minute(code, minute, source, buy_amount, sell_amount): ...
def query_today(code, source) -> list[dict]: ...
def query_range(code, source, start, end) -> list[dict]: ...
```

---

## 方案A：轮询采集

**文件**：`flow/plan_a/collector.py`

### 流程

```
每 30s 轮询一次
  → 对每只股票调用 get_capital_flow（拉当天全量）
  → 按分钟拆分，upsert 到 SQLite (source='plan_a')
```

### 字段映射

```python
buy_amount  = main_in_flow + fat_in_flow + mid_in_flow + small_in_flow
sell_amount = main_out_flow + fat_out_flow + mid_out_flow + small_out_flow
```

富途按超大单/大单/中单/小单分类，此处合并为总流入/流出。

### 关键约束

- 非交易时段自动跳过（调用富途 `get_market_state` 判断是否开盘）
- 多股票间加 0.5s 间隔，避免触发富途限流
- 每次拉当日全量数据覆盖写入，保证历史分钟不遗漏

---

## 方案B：逐笔实时采集

**文件**：`flow/plan_b/tick_handler.py` + `flow/plan_b/collector.py`

### 流程

```
FutuOpenD 推送 TICKER + QUOTE
  → tick_handler：每笔成交 → 分类主动买/卖
  → aggregator：按分钟桶累计 buy_amount / sell_amount
  → 每 15s WebSocket 广播一次所有股票最新数据
  → 分钟桶关闭时 upsert SQLite
```

### 逐笔分类规则

来自个人操作经验（personal-operation.md）：

```python
def classify_tick(price, ask1, bid1, prev_direction):
    if price >= ask1:
        return "buy"       # 成交价 ≥ 卖一 → 主动买入（流入）
    elif price <= bid1:
        return "sell"      # 成交价 ≤ 买一 → 主动卖出（流出）
    else:
        return prev_direction  # 介于中间 → 沿用上一笔方向
```

### 分钟桶

```python
# 每只股票维护内存桶
buckets = {
    "US.OKLO": {"minute": "14:30", "buy": 0.0, "sell": 0.0},
}
# 新 tick 的分钟 != 当前分钟时，关闭上一分钟桶并落库
```

### QUOTE 订阅用途

仅用于获取最新买一/卖一价（`ask1`/`bid1`），不单独存储。

### 断线重连策略

重连后从 SQLite 查当天已有分钟，方案B从当前时刻继续采集，缺口分钟由方案A数据补齐（前端对比模式可看出差异）。

---

## Web 服务

**文件**：`flow/server.py`

### 接口

```
GET  /                    → index.html
GET  /api/flow/{code}     → 历史数据（参数: source, date）
WS   /ws                  → 实时推送，每 15s 广播一次
```

### WebSocket 推送格式

```json
{
  "code": "US.OKLO",
  "source": "plan_b",
  "minute": "14:32",
  "buy_amount": 125000.0,
  "sell_amount": 89000.0,
  "net_flow": 36000.0,
  "cum_net_flow": 450000.0
}
```

---

## 前端

**文件**：`flow/frontend/index.html`（单文件，内嵌 ECharts CDN）

### 布局

```
┌────────────────────────────────────────────┐
│ 股票选择: [OKLO] [SMR] ...  日期: [今天▼]  │
│ 数据源:   [方案A] [方案B] [对比]            │
├────────────────────────────────────────────┤
│                                            │
│  ECharts 折线图                             │
│  X轴: 时间（分钟）                          │
│  Y轴: 累计净流入（美元）                     │
│  方案A: 蓝线   方案B: 橙线（对比模式同显）  │
│                                            │
├────────────────────────────────────────────┤
│ 当日净流入: +$450,000  |  方案B 实时更新    │
└────────────────────────────────────────────┘
```

### 数据刷新策略

| 模式 | 刷新方式 |
|------|---------|
| 方案A | 页面加载拉一次 REST，之后每 30s 轮询 |
| 方案B | WebSocket 连接，收到推送自动更新图表 |
| 对比 | 两条线同时显示，共享 X 轴时间 |

---

## 依赖

```
futu-api       # 已有
fastapi
uvicorn
websockets
pyyaml
```

前端仅使用 ECharts CDN，无需 npm。
