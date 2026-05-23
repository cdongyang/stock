---
title: 富途资金流向 v2 设计文档
date: 2026-05-18
status: approved
---

# 富途资金流向监控 v2

## 目标

实时监控指定股票的资金流向，按特大/大/中/小单分档展示净买入走势，并以表格形式展示特大单逐笔明细。

## 整体架构

```
FutuOpenD (port 11111)
    ↕ futu-api Python SDK（二进制协议，直连）
Python FastAPI app (uvicorn)
  ├── Plan A task (asyncio)  → 30s 轮询 get_capital_flow → 写 capital_flow 表
  ├── Plan B handler         → futu 回调线程 → asyncio.Queue
  │   └── consumer task      → 分档聚合 → 写 capital_flow 表
  │                            检测到特大单 → 写 ticks 表 + WS 推 tick 消息
  └── FastAPI routes
        ├── GET  /api/flow/{code}    → 聚合数据（图表）
        ├── GET  /api/ticks/{code}   → 特大单逐笔（表格）
        ├── GET  /api/stocks         → 股票列表
        ├── WS   /ws                 → flow_update（15s）+ tick（实时）
        └── /                       → 静态前端
```

- 语言：Python 3.11+
- Web 框架：FastAPI + uvicorn
- 数据库：SQLite（aiosqlite）
- 富途 SDK：futu-api
- 前端：ECharts 5（CDN），单页 HTML

## Storage

### capital_flow 表（按分钟聚合）

```sql
CREATE TABLE capital_flow (
    id         INTEGER PRIMARY KEY,
    code       TEXT NOT NULL,
    minute     TEXT NOT NULL,        -- "2026-05-18 14:30"
    source     TEXT NOT NULL,        -- "plan_a" | "plan_b"
    main_buy   REAL DEFAULT 0,
    main_sell  REAL DEFAULT 0,
    fat_buy    REAL DEFAULT 0,
    fat_sell   REAL DEFAULT 0,
    mid_buy    REAL DEFAULT 0,
    mid_sell   REAL DEFAULT 0,
    small_buy  REAL DEFAULT 0,
    small_sell REAL DEFAULT 0,
    UNIQUE(code, minute, source)
);
CREATE INDEX idx_flow_code_minute ON capital_flow(code, minute, source);
```

- Plan A 和 Plan B 各自写入，source 字段区分
- `ON CONFLICT DO UPDATE` 保证幂等
- buy/sell 分开存储，净流入由 API 层计算（net = buy - sell）

### ticks 表（特大单逐笔，仅 Plan B）

```sql
CREATE TABLE ticks (
    id        INTEGER PRIMARY KEY,
    code      TEXT NOT NULL,
    time      TEXT NOT NULL,         -- "2026-05-18 14:30:05"
    price     REAL NOT NULL,
    volume    INTEGER NOT NULL,
    amount    REAL NOT NULL,         -- price * volume
    direction TEXT NOT NULL          -- "buy" | "sell"
);
CREATE INDEX idx_ticks_code_time ON ticks(code, time);
```

## 后端逻辑

### Plan A（asyncio task，30s 间隔）

- 调用 `ctx.get_capital_flow(code)` 获取 DataFrame
- 映射字段：`main_in_flow → main_buy`，`main_out_flow → main_sell`，以此类推
- 所有字段通过 `_f(val)` 安全转 float（处理 `'N/A'`、`None`，默认返回 0.0）
- 对每行执行 `INSERT OR REPLACE INTO capital_flow`

### Plan B（futu 回调 → asyncio queue）

**回调线程（futu SDK 线程）：**
- `TickHandler.on_recv_rsp`：收到逐笔成交，放入 `asyncio.Queue`
- `QuoteHandler.on_recv_rsp`：收到快照更新，更新 ask1/bid1 内存缓存

**consumer task（asyncio）：**
- 从 queue 消费 QUOTE 事件：更新 `{code: (ask1, bid1)}` 内存字典
- 从 queue 消费 TICKER 事件：
  - 方向判断：price ≥ ask1 → buy；price ≤ bid1 → sell；否则继承上一笔方向（per-code，首笔默认 buy）
  - `amount = price × volume`
  - 按 thresholds 分档：amount ≥ main → main；≥ fat → fat；≥ mid → mid；否则 small
  - 累计到当前分钟 bucket（`{code: {minute: FlowData}}`）
  - 跨分钟时 flush bucket → 写 `capital_flow` 表
  - 若 amount ≥ main_threshold → 写 `ticks` 表 + WS 广播 `{"type":"tick","data":{...}}`

**15s 定时广播（asyncio task）：**
- 对每个监控股票广播 `{"type":"flow_update","code":"...","source":"plan_b"}`

### API 路由

| 路由 | 参数 | 说明 |
|------|------|------|
| `GET /api/flow/{code}` | `source`, `date` | 返回当天或指定日期的每分钟聚合数据，含各档净流入和累计净流入 |
| `GET /api/ticks/{code}` | `direction=all\|buy\|sell`, `date` | 返回特大单逐笔，按时间降序 |
| `GET /api/stocks` | — | 返回 config 中的股票列表 |
| `WS /ws` | — | 双向，服务端推送 flow_update 和 tick 消息 |

`/api/flow` 返回字段：`minute, main_net, fat_net, mid_net, small_net, cum_net_flow`

### WebSocket 消息格式

```json
// 聚合更新（15s 推送）
{"type": "flow_update", "code": "US.OKLO", "source": "plan_b"}

// 特大单实时推送
{"type": "tick", "data": {
    "code": "US.OKLO", "time": "2026-05-18 14:30:05",
    "price": 25.5, "volume": 2000, "amount": 51000.0, "direction": "buy"
}}
```

## 前端

单页 `frontend/index.html`，深色主题，布局从上到下：

**控制栏**：股票下拉 | 日期选择 | 方案A/B 切换 tab

**图表区（ECharts 5）**
- 上图（360px）：4 条折线，各档净买入（main_net/fat_net/mid_net/small_net）
  - 颜色：深绿 / 绿 / 浅绿 / 最浅绿
- 下图（160px）：累计总净流入折线 + 橙色面积填充

**特大单表格**（仅方案B显示）
- 方向 toggle：全部 / 买入 / 卖出
- 列：时间 | 价格 | 数量 | 金额 | 方向（买=绿/卖=红标签）
- WS `tick` 消息：实时追加到表格顶部，保留最近 200 条
- WS `flow_update` 消息：重拉 `/api/flow` 更新图表

## 配置文件 `config/flow_watch.yaml`

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
  port: 11111      # FutuOpenD 端口

thresholds:
  main: 50000      # 特大单 >= $50k
  fat:  10000      # 大单   >= $10k
  mid:  2000       # 中单   >= $2k
                   # 小单    < $2k

db_path: data/flow.db
```

## 目录结构

```
flow/
  config/
    flow_watch.yaml
  app/
    main.py          # FastAPI app，启动入口
    config.py        # 读取 yaml 配置
    db.py            # aiosqlite 封装（建表、upsert、查询）
    plan_a.py        # Plan A asyncio task
    plan_b.py        # Plan B futu 回调 + consumer task
    ws.py            # WebSocket 连接管理 + broadcast
    classifier.py    # 逐笔方向判断 + 分档逻辑
  frontend/
    index.html
  data/              # SQLite DB（gitignore）
```

## 测试要点

- `classifier.py`：方向判断（ask/bid 边界）、分档逻辑（阈值边界）
- `db.py`：upsert 幂等性、QueryToday/QueryRange
- Plan A 映射：Futu 字段 → DB 字段，'N/A' 处理
- Plan B consumer：跨分钟 flush、特大单写 ticks 表
