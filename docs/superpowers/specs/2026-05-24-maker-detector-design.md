# 庄家进出场检测系统设计

**日期**: 2026-05-24  
**范围**: 扩展 `flow/app/` 服务，增加庄家信号检测与飞书通知

---

## 背景

现有 `flow/app/` 已通过富途 API 实时订阅 Ticker/Quote 数据，按特大单(main)/大单(fat)/中单(mid)/小单(small) 分类，存入 SQLite，WebSocket 推送前端。

本设计在此基础上增加庄家行为检测层，识别四类信号并通过飞书通知，附带仓位建议。

---

## 信号定义

| 编号 | 名称 | 类型 | 说明 |
|------|------|------|------|
| 进场① | main 连续买入 | 做多信号 | 实时 main 滑动窗口净买入超阈值 |
| 进场② | 散户卖出价格不跌 | 做多信号 | 分钟级：fat+mid+small 净卖出但价格平稳，庄家在吸筹 |
| 出货① | 价格停滞散户仍买 | 做空信号 | 分钟级：前期涨幅后价格停滞，散户仍净买入，庄家在出货 |
| 出货② | main 连续卖出 | 做空信号 | 实时 main 滑动窗口净卖出超阈值 |

---

## 架构

### 整体结构

```
flow/app/
├── plan_b.py       (修改) ← main tick 推给 Detector
├── detector.py     (新建) ← 两条检测路径
├── alert.py        (新建) ← 冷却管理 + 飞书通知
├── config.py       (修改) ← DetectorConfig dataclass
└── main.py         (修改) ← 启动分钟级 scan task
```

### 数据流

```
Futu Ticker/Quote
       │
   plan_b._consume()
       ├── [tier==main] ──→ Detector.on_main_tick()   ← 实时路径（秒级）
       │                         │ 进场①/出货②
       │                         ↓
       └── [DB upsert] ──→ Detector.minute_scan()     ← 分钟路径（60s 轮询）
                                 │ 进场②/出货①
                                 ↓
                            Alert.send()  (冷却过滤 → 飞书)
```

---

## 检测逻辑

### 实时路径：`Detector.on_main_tick()`

每收到 main tick，维护每只股票的滑动窗口（最近 `main_window` 笔 main 单，默认 10）。

- **进场①**：窗口内 main 净买入 ≥ `entry_main_threshold`（默认 500万）
- **出货②**：窗口内 main 净卖出 ≥ `exit_main_threshold`（默认 500万）

### 分钟路径：`Detector.minute_scan()`

每 60 秒从 DB 读最近 `minute_window` 分钟数据（默认 5 分钟）。  
价格数据来自 `Detector` 内存中维护的每股最新报价（由 `QuoteHandler` 实时更新，`Detector` 持有 `quotes: dict[str, float]`）。

- **进场②**：fat+mid+small 净卖出 ≥ `absorb_threshold`（默认 300万）**且** 价格变化绝对值 ≤ `price_flat_pct`（默认 0.3%）
- **出货①**：前 `minute_window` 分钟涨幅 ≥ `rise_pct`（默认 1.0%）**且** 最近 2 分钟涨幅 ≤ 0.2% **且** fat+mid+small 净买入 ≥ `dist_threshold`（默认 200万）

---

## 仓位建议

基于当日 main 累计净买入/净卖出 vs 庄家估算总资金 `maker_capital`（默认 2000万）：

- **做多建议**：`净买入 / maker_capital`，上限 100%
- **减仓建议**：`(1 - 净卖出 / maker_capital) × 当前满仓`

---

## 冷却与通知

### 冷却规则

- `Alert` 维护 `(code, signal_direction) → last_sent_time`
- 同股票同方向冷却 `cooldown_seconds`（默认 300 秒 = 5 分钟）
- **反向信号不受冷却限制**：出货信号出现时立即发送，不管做多冷却是否到期

### 飞书消息示例

**进场信号：**
```
🔔 [US.OKLO] 庄家进场①
信号：main 大单连续净买入 ¥680万
价格：$23.15
建议：做多，参考仓位 34%（680/2000万）
时间：14:23
```

**出货信号：**
```
⚠️ [US.OKLO] 庄家出货①
信号：价格停滞（涨后5分钟仅+0.1%），散户净买入 ¥240万
价格：$25.40
建议：减仓或观望
时间：14:51
```

---

## 配置（`flow/config/flow_watch.yaml` 新增块）

```yaml
stocks:
  - code: US.OKLO
    name: Oklo

detector:
  main_window: 10
  minute_window: 5
  entry_main_threshold: 5000000
  exit_main_threshold: 5000000
  absorb_threshold: 3000000
  dist_threshold: 2000000
  rise_pct: 1.0
  price_flat_pct: 0.3
  cooldown_seconds: 300
  maker_capital: 20000000
```

---

## 文件改动清单

| 文件 | 改动 |
|------|------|
| `flow/app/detector.py` | 新建，`Detector` 类 |
| `flow/app/alert.py` | 新建，`Alert` 类 |
| `flow/app/plan_b.py` | `_consume()` 中 main tick 调用 `detector.on_main_tick()` |
| `flow/app/main.py` | `lifespan` 启动 `detector.minute_scan_loop()` task |
| `flow/app/config.py` | 增加 `DetectorConfig` dataclass |
| `flow/config/flow_watch.yaml` | 增加 `detector` 块，stocks 加 `US.OKLO` |
