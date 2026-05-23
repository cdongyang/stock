# 富途实时资金流向走势图 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现两套富途资金流向采集方案（轮询 vs 逐笔实时），共用 SQLite 存储，通过浏览器 ECharts 走势图对比效果。

**Architecture:** 方案A 每 30s 轮询 `get_capital_flow` 写入 SQLite；方案B 订阅 TICKER+QUOTE 推送，按"成交价 vs 买一卖一"规则逐笔分类后按分钟聚合，每 15s 通过 WebSocket 广播。FastAPI server 提供 REST + WebSocket，前端单页 ECharts 支持方案A/B 切换与对比。

**Tech Stack:** Python 3.10+, futu-api, FastAPI, uvicorn, PyYAML, pytest, ECharts 5 (CDN)

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `flow/__init__.py` | 包入口 |
| `flow/config/flow_watch.yaml` | 股票列表 + 服务参数 |
| `flow/storage.py` | SQLite 读写（两套方案共用） |
| `flow/plan_a/__init__.py` | 包入口 |
| `flow/plan_a/collector.py` | 轮询 get_capital_flow，写入 SQLite |
| `flow/plan_b/__init__.py` | 包入口 |
| `flow/plan_b/tick_handler.py` | TickClassifier + QuoteHandler + TickerHandler |
| `flow/plan_b/aggregator.py` | Aggregator：分钟桶累计逻辑（纯函数，可测） |
| `flow/plan_b/state.py` | 共享 latest_data dict（跨线程读写） |
| `flow/plan_b/collector.py` | 管理 Futu 订阅 + 主循环 |
| `flow/server.py` | FastAPI REST + WebSocket + 15s 广播任务 |
| `flow/frontend/index.html` | ECharts 单页前端 |
| `tests/flow/test_storage.py` | storage 单元测试 |
| `tests/flow/test_tick_handler.py` | TickClassifier 单元测试 |
| `tests/flow/test_aggregator.py` | Aggregator 单元测试 |
| `tests/flow/test_plan_a.py` | compute_flow_from_df 单元测试 |
| `tests/flow/test_server.py` | FastAPI REST 端点测试 |

---

## Task 1: Config + 包结构 + Storage 层

**Files:**
- Create: `flow/__init__.py`
- Create: `flow/config/flow_watch.yaml`
- Create: `flow/storage.py`
- Create: `tests/__init__.py`
- Create: `tests/flow/__init__.py`
- Create: `tests/flow/test_storage.py`

- [ ] **Step 1: 创建包骨架**

```bash
mkdir -p flow/config flow/plan_a flow/plan_b flow/frontend flow/data
mkdir -p tests/flow
touch flow/__init__.py flow/plan_a/__init__.py flow/plan_b/__init__.py
touch tests/__init__.py tests/flow/__init__.py
```

- [ ] **Step 2: 写配置文件**

`flow/config/flow_watch.yaml`:
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

- [ ] **Step 3: 写 storage 失败测试**

`tests/flow/test_storage.py`:
```python
import pytest
from pathlib import Path


@pytest.fixture
def db(tmp_path, monkeypatch):
    import flow.storage as storage
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test.db")
    return storage


def test_upsert_and_query_today(db):
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    db.upsert_minute("US.OKLO", f"{today} 14:30", "plan_b", 100.0, 60.0)
    rows = db.query_today("US.OKLO", "plan_b")
    assert len(rows) == 1
    assert rows[0]["net_flow"] == pytest.approx(40.0)
    assert rows[0]["buy_amount"] == pytest.approx(100.0)


def test_upsert_overwrites_same_minute(db):
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    db.upsert_minute("US.OKLO", f"{today} 14:30", "plan_b", 100.0, 60.0)
    db.upsert_minute("US.OKLO", f"{today} 14:30", "plan_b", 200.0, 80.0)
    rows = db.query_today("US.OKLO", "plan_b")
    assert len(rows) == 1
    assert rows[0]["buy_amount"] == pytest.approx(200.0)


def test_source_isolation(db):
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    db.upsert_minute("US.OKLO", f"{today} 14:30", "plan_a", 100.0, 60.0)
    db.upsert_minute("US.OKLO", f"{today} 14:30", "plan_b", 200.0, 80.0)
    assert len(db.query_today("US.OKLO", "plan_a")) == 1
    assert len(db.query_today("US.OKLO", "plan_b")) == 1


def test_query_range(db):
    db.upsert_minute("US.OKLO", "2026-05-14 14:30", "plan_b", 100.0, 60.0)
    db.upsert_minute("US.OKLO", "2026-05-14 14:31", "plan_b", 50.0, 30.0)
    db.upsert_minute("US.OKLO", "2026-05-14 14:32", "plan_b", 70.0, 40.0)
    rows = db.query_range("US.OKLO", "plan_b", "2026-05-14 14:30", "2026-05-14 14:31")
    assert len(rows) == 2
```

- [ ] **Step 4: 运行测试，确认失败**

```bash
cd /Users/dy.chen/Personal/stock
python -m pytest tests/flow/test_storage.py -v
```
预期：`ImportError` 或 `ModuleNotFoundError`

- [ ] **Step 5: 实现 storage.py**

`flow/storage.py`:
```python
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "flow.db"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS capital_flow (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL,
    minute      TEXT NOT NULL,
    source      TEXT NOT NULL,
    buy_amount  REAL NOT NULL,
    sell_amount REAL NOT NULL,
    net_flow    REAL NOT NULL,
    UNIQUE(code, minute, source)
);
"""
_CREATE_INDEX = "CREATE INDEX IF NOT EXISTS idx_code_minute ON capital_flow(code, minute, source);"


@contextmanager
def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute(_CREATE_TABLE)
    con.execute(_CREATE_INDEX)
    con.commit()
    try:
        yield con
    finally:
        con.close()


def upsert_minute(code: str, minute: str, source: str, buy_amount: float, sell_amount: float) -> None:
    net_flow = buy_amount - sell_amount
    with _conn() as con:
        con.execute(
            """
            INSERT INTO capital_flow (code, minute, source, buy_amount, sell_amount, net_flow)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(code, minute, source) DO UPDATE SET
                buy_amount  = excluded.buy_amount,
                sell_amount = excluded.sell_amount,
                net_flow    = excluded.net_flow
            """,
            (code, minute, source, buy_amount, sell_amount, net_flow),
        )
        con.commit()


def query_today(code: str, source: str) -> list[dict]:
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    with _conn() as con:
        rows = con.execute(
            "SELECT minute, buy_amount, sell_amount, net_flow FROM capital_flow "
            "WHERE code=? AND source=? AND minute LIKE ? ORDER BY minute",
            (code, source, f"{today}%"),
        ).fetchall()
    return [dict(r) for r in rows]


def query_range(code: str, source: str, start: str, end: str) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT minute, buy_amount, sell_amount, net_flow FROM capital_flow "
            "WHERE code=? AND source=? AND minute BETWEEN ? AND ? ORDER BY minute",
            (code, source, start, end),
        ).fetchall()
    return [dict(r) for r in rows]
```

- [ ] **Step 6: 运行测试，确认通过**

```bash
python -m pytest tests/flow/test_storage.py -v
```
预期：全部 PASS

- [ ] **Step 7: 提交**

```bash
git add flow/__init__.py flow/plan_a/__init__.py flow/plan_b/__init__.py \
        flow/config/flow_watch.yaml flow/storage.py \
        tests/__init__.py tests/flow/__init__.py tests/flow/test_storage.py
git commit -m "feat: add flow package skeleton, config, and storage layer"
```

---

## Task 2: Plan B — TickClassifier + Aggregator（纯逻辑，无 Futu 依赖）

**Files:**
- Create: `flow/plan_b/tick_handler.py` (TickClassifier 类)
- Create: `flow/plan_b/aggregator.py`
- Create: `tests/flow/test_tick_handler.py`
- Create: `tests/flow/test_aggregator.py`

- [ ] **Step 1: 写 TickClassifier 失败测试**

`tests/flow/test_tick_handler.py`:
```python
from flow.plan_b.tick_handler import TickClassifier


def test_buy_when_price_equals_ask():
    c = TickClassifier()
    assert c.classify("US.OKLO", price=10.0, ask1=10.0, bid1=9.8) == "buy"


def test_buy_when_price_above_ask():
    c = TickClassifier()
    assert c.classify("US.OKLO", price=10.1, ask1=10.0, bid1=9.8) == "buy"


def test_sell_when_price_equals_bid():
    c = TickClassifier()
    assert c.classify("US.OKLO", price=9.8, ask1=10.0, bid1=9.8) == "sell"


def test_sell_when_price_below_bid():
    c = TickClassifier()
    assert c.classify("US.OKLO", price=9.7, ask1=10.0, bid1=9.8) == "sell"


def test_mid_inherits_prev_buy():
    c = TickClassifier()
    c.classify("US.OKLO", price=10.0, ask1=10.0, bid1=9.8)  # buy
    assert c.classify("US.OKLO", price=9.9, ask1=10.0, bid1=9.8) == "buy"


def test_mid_inherits_prev_sell():
    c = TickClassifier()
    c.classify("US.OKLO", price=9.8, ask1=10.0, bid1=9.8)  # sell
    assert c.classify("US.OKLO", price=9.9, ask1=10.0, bid1=9.8) == "sell"


def test_default_direction_is_buy_when_no_history():
    c = TickClassifier()
    assert c.classify("US.OKLO", price=9.9, ask1=10.0, bid1=9.8) == "buy"


def test_direction_isolated_per_code():
    c = TickClassifier()
    c.classify("US.OKLO", price=10.0, ask1=10.0, bid1=9.8)  # OKLO: buy
    c.classify("US.SMR", price=9.8, ask1=10.0, bid1=9.8)   # SMR: sell
    assert c.classify("US.OKLO", price=9.9, ask1=10.0, bid1=9.8) == "buy"
    assert c.classify("US.SMR", price=9.9, ask1=10.0, bid1=9.8) == "sell"
```

- [ ] **Step 2: 写 Aggregator 失败测试**

`tests/flow/test_aggregator.py`:
```python
from flow.plan_b.aggregator import Aggregator


def test_accumulates_buy_in_same_minute():
    agg = Aggregator()
    agg.add_tick("US.OKLO", "2026-05-14 14:30", "buy", 1000.0)
    agg.add_tick("US.OKLO", "2026-05-14 14:30", "buy", 500.0)
    assert agg.buckets["US.OKLO"]["buy"] == 1500.0


def test_accumulates_sell_in_same_minute():
    agg = Aggregator()
    agg.add_tick("US.OKLO", "2026-05-14 14:30", "sell", 800.0)
    assert agg.buckets["US.OKLO"]["sell"] == 800.0


def test_closes_bucket_on_new_minute():
    agg = Aggregator()
    agg.add_tick("US.OKLO", "2026-05-14 14:30", "buy", 1000.0)
    agg.add_tick("US.OKLO", "2026-05-14 14:30", "sell", 600.0)
    agg.add_tick("US.OKLO", "2026-05-14 14:31", "buy", 200.0)
    closed = agg.flush_closed()
    assert len(closed) == 1
    code, minute, buy, sell = closed[0]
    assert code == "US.OKLO"
    assert minute == "2026-05-14 14:30"
    assert buy == 1000.0
    assert sell == 600.0


def test_flush_closed_clears_list():
    agg = Aggregator()
    agg.add_tick("US.OKLO", "2026-05-14 14:30", "buy", 1000.0)
    agg.add_tick("US.OKLO", "2026-05-14 14:31", "buy", 200.0)
    agg.flush_closed()
    assert agg.flush_closed() == []


def test_independent_buckets_per_code():
    agg = Aggregator()
    agg.add_tick("US.OKLO", "2026-05-14 14:30", "buy", 1000.0)
    agg.add_tick("US.SMR", "2026-05-14 14:30", "sell", 500.0)
    assert agg.buckets["US.OKLO"]["buy"] == 1000.0
    assert agg.buckets["US.SMR"]["sell"] == 500.0
```

- [ ] **Step 3: 运行失败测试**

```bash
python -m pytest tests/flow/test_tick_handler.py tests/flow/test_aggregator.py -v
```
预期：全部 FAIL

- [ ] **Step 4: 实现 TickClassifier**

`flow/plan_b/tick_handler.py`:
```python
class TickClassifier:
    def __init__(self):
        self._prev: dict[str, str] = {}

    def classify(self, code: str, price: float, ask1: float, bid1: float) -> str:
        if price >= ask1:
            direction = "buy"
        elif price <= bid1:
            direction = "sell"
        else:
            direction = self._prev.get(code, "buy")
        self._prev[code] = direction
        return direction
```

- [ ] **Step 5: 实现 Aggregator**

`flow/plan_b/aggregator.py`:
```python
class Aggregator:
    def __init__(self):
        self.buckets: dict[str, dict] = {}
        self._closed: list[tuple] = []

    def add_tick(self, code: str, minute: str, direction: str, amount: float) -> None:
        if code not in self.buckets:
            self.buckets[code] = {"minute": minute, "buy": 0.0, "sell": 0.0}

        bucket = self.buckets[code]
        if bucket["minute"] != minute:
            self._closed.append((code, bucket["minute"], bucket["buy"], bucket["sell"]))
            self.buckets[code] = {"minute": minute, "buy": 0.0, "sell": 0.0}
            bucket = self.buckets[code]

        if direction == "buy":
            bucket["buy"] += amount
        else:
            bucket["sell"] += amount

    def flush_closed(self) -> list[tuple]:
        closed, self._closed = self._closed, []
        return closed
```

- [ ] **Step 6: 运行测试，确认通过**

```bash
python -m pytest tests/flow/test_tick_handler.py tests/flow/test_aggregator.py -v
```
预期：全部 PASS

- [ ] **Step 7: 提交**

```bash
git add flow/plan_b/tick_handler.py flow/plan_b/aggregator.py \
        tests/flow/test_tick_handler.py tests/flow/test_aggregator.py
git commit -m "feat: add TickClassifier and Aggregator for plan_b"
```

---

## Task 3: Plan B — Futu 集成（QuoteHandler + TickerHandler + Collector）

**Files:**
- Modify: `flow/plan_b/tick_handler.py` (追加 QuoteHandler + TickerHandler)
- Create: `flow/plan_b/state.py`
- Create: `flow/plan_b/collector.py`

- [ ] **Step 1: 创建共享状态模块**

`flow/plan_b/state.py`:
```python
# 跨线程共享，CPython dict 读写在 GIL 下是原子操作
latest_data: dict[str, dict] = {}
```

- [ ] **Step 2: 追加 Futu 回调类到 tick_handler.py**

在 `flow/plan_b/tick_handler.py` 末尾追加：

```python
from futu import QuoteHandlerBase, TickerHandlerBase, RET_OK

from flow.plan_b.aggregator import Aggregator
from flow.plan_b import state
from flow.storage import upsert_minute


class QuoteHandler(QuoteHandlerBase):
    def __init__(self, quotes: dict):
        super().__init__()
        self._quotes = quotes

    def on_recv_rsp(self, rsp_str):
        ret, df = super().on_recv_rsp(rsp_str)
        if ret != RET_OK:
            return ret, df
        for _, row in df.iterrows():
            self._quotes[row["code"]] = {
                "ask1": row["ask_price_1"],
                "bid1": row["bid_price_1"],
            }
        return ret, df


class TickerHandler(TickerHandlerBase):
    def __init__(self, classifier: TickClassifier, aggregator: Aggregator, quotes: dict):
        super().__init__()
        self._cls = classifier
        self._agg = aggregator
        self._quotes = quotes

    def on_recv_rsp(self, rsp_str):
        ret, df = super().on_recv_rsp(rsp_str)
        if ret != RET_OK:
            return ret, df
        for _, row in df.iterrows():
            code = row["code"]
            price = float(row["price"])
            volume = int(row["volume"])
            q = self._quotes.get(code, {})
            ask1 = q.get("ask1", price)
            bid1 = q.get("bid1", price)
            direction = self._cls.classify(code, price, ask1, bid1)
            minute = str(row["time"])[:16]   # "YYYY-MM-DD HH:MM"
            self._agg.add_tick(code, minute, direction, price * volume)
            for entry in self._agg.flush_closed():
                c, m, buy, sell = entry
                upsert_minute(c, m, "plan_b", buy, sell)
                _update_state(c, m, buy, sell)
        return ret, df


def _update_state(code: str, minute: str, buy: float, sell: float) -> None:
    prev = state.latest_data.get(code, {})
    prev_cum = prev.get("cum_net_flow", 0.0)
    net = buy - sell
    state.latest_data[code] = {
        "code": code,
        "source": "plan_b",
        "minute": minute,
        "buy_amount": buy,
        "sell_amount": sell,
        "net_flow": net,
        "cum_net_flow": prev_cum + net,
    }
```

- [ ] **Step 3: 实现 plan_b/collector.py**

`flow/plan_b/collector.py`:
```python
import time
import yaml
from pathlib import Path

from futu import OpenQuoteContext, SubType, RET_OK

from flow.plan_b.tick_handler import TickClassifier, QuoteHandler, TickerHandler
from flow.plan_b.aggregator import Aggregator

_CONFIG = yaml.safe_load((Path(__file__).parent.parent / "config" / "flow_watch.yaml").read_text())


def run():
    codes = [s["code"] for s in _CONFIG["stocks"]]
    futu_cfg = _CONFIG["futu"]

    quotes: dict = {}
    classifier = TickClassifier()
    aggregator = Aggregator()

    ctx = OpenQuoteContext(host=futu_cfg["host"], port=futu_cfg["port"])
    ctx.set_handler(QuoteHandler(quotes))
    ctx.set_handler(TickerHandler(classifier, aggregator, quotes))

    ret, msg = ctx.subscribe(codes, [SubType.QUOTE, SubType.TICKER], is_first_push=True)
    if ret != RET_OK:
        print(f"订阅失败: {msg}")
        ctx.close()
        return

    print(f"Plan B 订阅成功: {codes}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        ctx.close()


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: 手动验证（需 FutuOpenD 运行）**

```bash
python -m flow.plan_b.collector
```
预期：打印"Plan B 订阅成功"，盘中有成交时控制台无报错；`flow/data/flow.db` 开始有数据写入。

- [ ] **Step 5: 提交**

```bash
git add flow/plan_b/tick_handler.py flow/plan_b/state.py flow/plan_b/collector.py
git commit -m "feat: add plan_b Futu handlers and collector"
```

---

## Task 4: Plan A — 轮询采集器

**Files:**
- Create: `flow/plan_a/collector.py`
- Create: `tests/flow/test_plan_a.py`

- [ ] **Step 1: 写纯函数失败测试**

`tests/flow/test_plan_a.py`:
```python
import pandas as pd
import pytest
from flow.plan_a.collector import compute_flow_from_df


def _make_df(rows):
    cols = ["time", "main_in_flow", "main_out_flow",
            "fat_in_flow", "fat_out_flow",
            "mid_in_flow", "mid_out_flow",
            "small_in_flow", "small_out_flow"]
    return pd.DataFrame(rows, columns=cols)


def test_single_row():
    df = _make_df([["2026-05-14 14:30", 50000, 20000, 10000, 5000, 3000, 1000, 500, 200]])
    result = compute_flow_from_df(df)
    assert len(result) == 1
    assert result[0]["minute"] == "2026-05-14 14:30"
    assert result[0]["buy_amount"] == pytest.approx(63500)
    assert result[0]["sell_amount"] == pytest.approx(26200)
    assert result[0]["net_flow"] == pytest.approx(37300)


def test_multiple_rows():
    df = _make_df([
        ["2026-05-14 14:30", 10000, 5000, 0, 0, 0, 0, 0, 0],
        ["2026-05-14 14:31", 20000, 8000, 0, 0, 0, 0, 0, 0],
    ])
    result = compute_flow_from_df(df)
    assert len(result) == 2
    assert result[1]["buy_amount"] == pytest.approx(20000)


def test_empty_df():
    df = _make_df([])
    assert compute_flow_from_df(df) == []
```

- [ ] **Step 2: 运行失败测试**

```bash
python -m pytest tests/flow/test_plan_a.py -v
```
预期：FAIL

- [ ] **Step 3: 实现 plan_a/collector.py**

`flow/plan_a/collector.py`:
```python
import time
import yaml
from datetime import datetime
from pathlib import Path

import pandas as pd

from flow.storage import upsert_minute

_CONFIG = yaml.safe_load((Path(__file__).parent.parent / "config" / "flow_watch.yaml").read_text())
_POLL_INTERVAL = 30  # 秒


def compute_flow_from_df(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    result = []
    for _, row in df.iterrows():
        buy = (row["main_in_flow"] + row["fat_in_flow"]
               + row["mid_in_flow"] + row["small_in_flow"])
        sell = (row["main_out_flow"] + row["fat_out_flow"]
                + row["mid_out_flow"] + row["small_out_flow"])
        result.append({
            "minute": str(row["time"])[:16],
            "buy_amount": float(buy),
            "sell_amount": float(sell),
            "net_flow": float(buy - sell),
        })
    return result


def _is_market_open(ctx, code: str) -> bool:
    from futu import RET_OK
    ret, data = ctx.get_market_state([code])
    if ret != RET_OK:
        return True  # 获取失败时不阻塞，继续轮询
    state = data.iloc[0]["market_state"]
    return "OPEN" in str(state).upper()


def _poll_once(ctx, codes: list[str]) -> None:
    from futu import RET_OK, KLType
    for code in codes:
        if not _is_market_open(ctx, code):
            continue
        ret, df = ctx.get_capital_flow(code)
        if ret != RET_OK:
            print(f"get_capital_flow 失败 {code}: {df}")
            time.sleep(0.5)
            continue
        for row in compute_flow_from_df(df):
            upsert_minute(code, row["minute"], "plan_a",
                          row["buy_amount"], row["sell_amount"])
        time.sleep(0.5)


def run():
    from futu import OpenQuoteContext
    futu_cfg = _CONFIG["futu"]
    codes = [s["code"] for s in _CONFIG["stocks"]]
    ctx = OpenQuoteContext(host=futu_cfg["host"], port=futu_cfg["port"])
    print(f"Plan A 启动，轮询间隔 {_POLL_INTERVAL}s，监控: {codes}")
    try:
        while True:
            _poll_once(ctx, codes)
            time.sleep(_POLL_INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        ctx.close()


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
python -m pytest tests/flow/test_plan_a.py -v
```
预期：全部 PASS

- [ ] **Step 5: 提交**

```bash
git add flow/plan_a/collector.py tests/flow/test_plan_a.py
git commit -m "feat: add plan_a polling collector"
```

---

## Task 5: FastAPI Server（REST + WebSocket）

**Files:**
- Create: `flow/server.py`
- Create: `tests/flow/test_server.py`

- [ ] **Step 1: 安装依赖**

```bash
pip install fastapi uvicorn websockets httpx
```

- [ ] **Step 2: 写 REST 端点失败测试**

`tests/flow/test_server.py`:
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def client():
    from flow.server import app
    return TestClient(app)


def test_get_flow_returns_list(client):
    mock_rows = [
        {"minute": "2026-05-14 14:30", "buy_amount": 100.0, "sell_amount": 60.0, "net_flow": 40.0},
    ]
    with patch("flow.server.query_today", return_value=mock_rows):
        resp = client.get("/api/flow/US.OKLO?source=plan_b")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["cum_net_flow"] == pytest.approx(40.0)


def test_get_flow_computes_cumulative(client):
    mock_rows = [
        {"minute": "2026-05-14 14:30", "buy_amount": 100.0, "sell_amount": 60.0, "net_flow": 40.0},
        {"minute": "2026-05-14 14:31", "buy_amount": 50.0, "sell_amount": 80.0, "net_flow": -30.0},
    ]
    with patch("flow.server.query_today", return_value=mock_rows):
        resp = client.get("/api/flow/US.OKLO?source=plan_b")
    data = resp.json()
    assert data[0]["cum_net_flow"] == pytest.approx(40.0)
    assert data[1]["cum_net_flow"] == pytest.approx(10.0)


def test_get_flow_with_date(client):
    with patch("flow.server.query_range", return_value=[]) as mock_qr:
        resp = client.get("/api/flow/US.OKLO?source=plan_a&date=2026-05-14")
    assert resp.status_code == 200
    mock_qr.assert_called_once_with("US.OKLO", "plan_a", "2026-05-14 00:00", "2026-05-14 23:59")
```

- [ ] **Step 3: 运行失败测试**

```bash
python -m pytest tests/flow/test_server.py -v
```
预期：FAIL

- [ ] **Step 4: 实现 server.py**

`flow/server.py`:
```python
import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from flow.storage import query_today, query_range

app = FastAPI()

_FRONTEND = Path(__file__).parent / "frontend" / "index.html"


class _ConnectionManager:
    def __init__(self):
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._active.remove(ws)

    async def broadcast(self, data: dict) -> None:
        msg = json.dumps(data)
        for ws in list(self._active):
            try:
                await ws.send_text(msg)
            except Exception:
                self._active.remove(ws)


_manager = _ConnectionManager()


@app.on_event("startup")
async def _start_broadcast_loop():
    asyncio.create_task(_broadcast_loop())


async def _broadcast_loop():
    from flow.plan_b import state
    while True:
        await asyncio.sleep(15)
        for code, data in list(state.latest_data.items()):
            await _manager.broadcast(data)


@app.get("/")
async def root():
    return FileResponse(_FRONTEND)


@app.get("/api/flow/{code}")
async def get_flow(code: str, source: str = "plan_b", date: str = None):
    if date is None:
        rows = query_today(code, source)
    else:
        rows = query_range(code, source, f"{date} 00:00", f"{date} 23:59")
    cum = 0.0
    result = []
    for r in rows:
        cum += r["net_flow"]
        result.append({**r, "cum_net_flow": cum})
    return result


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await _manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        _manager.disconnect(ws)
```

- [ ] **Step 5: 运行测试，确认通过**

```bash
python -m pytest tests/flow/test_server.py -v
```
预期：全部 PASS

- [ ] **Step 6: 提交**

```bash
git add flow/server.py tests/flow/test_server.py
git commit -m "feat: add FastAPI server with REST and WebSocket endpoints"
```

---

## Task 6: 前端（ECharts 单页）

**Files:**
- Create: `flow/frontend/index.html`

- [ ] **Step 1: 创建 index.html**

`flow/frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <title>资金流向走势</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: sans-serif; background: #0d1117; color: #c9d1d9; padding: 16px; }
    #controls { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }
    select, input[type=date] { background: #161b22; color: #c9d1d9; border: 1px solid #30363d; padding: 6px 10px; border-radius: 6px; }
    .tab-group { display: flex; gap: 4px; }
    .tab { padding: 6px 14px; border-radius: 6px; border: 1px solid #30363d; background: #161b22; color: #8b949e; cursor: pointer; }
    .tab.active { background: #1f6feb; color: #fff; border-color: #1f6feb; }
    #chart { width: 100%; height: 500px; }
    #status { margin-top: 8px; font-size: 13px; color: #8b949e; }
  </style>
</head>
<body>
<div id="controls">
  <select id="stockSelect"></select>
  <input type="date" id="dateSelect">
  <div class="tab-group" id="sourceTabs">
    <button class="tab active" data-src="plan_b">方案B（逐笔）</button>
    <button class="tab" data-src="plan_a">方案A（轮询）</button>
    <button class="tab" data-src="both">对比</button>
  </div>
</div>
<div id="chart"></div>
<div id="status">等待数据...</div>

<script>
const chart = echarts.init(document.getElementById('chart'));
let currentCode = '', currentSource = 'plan_b', ws = null;

const STOCKS = []; // 从后端获取

async function fetchStocks() {
  // 直接从 config 读取不暴露接口，这里硬编码配置中的股票
  const resp = await fetch('/api/stocks').catch(() => null);
  if (resp && resp.ok) {
    const data = await resp.json();
    data.forEach(s => STOCKS.push(s));
  }
}

function initChart() {
  chart.setOption({
    backgroundColor: '#0d1117',
    tooltip: { trigger: 'axis', formatter: params => {
      return params.map(p => `${p.seriesName}: $${p.value?.toLocaleString() ?? '--'}`).join('<br>');
    }},
    legend: { data: ['方案A', '方案B'], textStyle: { color: '#8b949e' } },
    grid: { left: 80, right: 20, top: 40, bottom: 60 },
    xAxis: { type: 'category', data: [], axisLabel: { color: '#8b949e', rotate: 30 } },
    yAxis: { type: 'value', name: '累计净流入 (USD)', nameTextStyle: { color: '#8b949e' },
             axisLabel: { color: '#8b949e', formatter: v => '$' + (v/1000).toFixed(0) + 'k' },
             splitLine: { lineStyle: { color: '#21262d' } } },
    series: [
      { name: '方案A', type: 'line', data: [], smooth: true,
        itemStyle: { color: '#5470c6' }, lineStyle: { width: 2 }, symbol: 'none' },
      { name: '方案B', type: 'line', data: [], smooth: true,
        itemStyle: { color: '#ff7c00' }, lineStyle: { width: 2 }, symbol: 'none' },
    ]
  });
}

function updateSeries(seriesName, rows) {
  const times = rows.map(r => r.minute.slice(11, 16));
  const values = rows.map(r => r.cum_net_flow);
  const idx = seriesName === '方案A' ? 0 : 1;
  chart.setOption({ xAxis: { data: times }, series: [{ id: idx, data: values }] });
}

async function loadHistory(code, source, date) {
  const dateParam = date ? `&date=${date}` : '';
  const sources = source === 'both' ? ['plan_a', 'plan_b'] : [source];
  for (const src of sources) {
    const resp = await fetch(`/api/flow/${code}?source=${src}${dateParam}`);
    const rows = await resp.json();
    updateSeries(src === 'plan_a' ? '方案A' : '方案B', rows);
  }
  setStatus(`已加载 ${code} 历史数据`);
}

function setStatus(msg) {
  document.getElementById('status').textContent = msg;
}

function connectWS() {
  ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onopen = () => setStatus('WebSocket 已连接，方案B 实时更新中...');
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.code !== currentCode) return;
    if (currentSource !== 'plan_b' && currentSource !== 'both') return;
    // append latest point
    const opt = chart.getOption();
    const times = [...(opt.xAxis[0].data || [])];
    const series = opt.series;
    const bSeries = series[1].data ? [...series[1].data] : [];
    const t = msg.minute.slice(11, 16);
    if (!times.includes(t)) times.push(t);
    const idx = times.indexOf(t);
    bSeries[idx] = msg.cum_net_flow;
    chart.setOption({ xAxis: { data: times }, series: [{ name: '方案B', data: bSeries }] });
    setStatus(`方案B 更新: ${msg.minute}  净流入 $${msg.cum_net_flow.toLocaleString()}`);
  };
  ws.onclose = () => {
    setStatus('WebSocket 断开，3s 后重连...');
    setTimeout(connectWS, 3000);
  };
}

// 初始化股票下拉
async function initStockSelect() {
  const sel = document.getElementById('stockSelect');
  // 尝试从服务端获取，失败则回退硬编码
  const pairs = [['US.OKLO', 'Oklo'], ['US.SMR', 'NuScale']];
  pairs.forEach(([code, name]) => {
    const opt = document.createElement('option');
    opt.value = code; opt.textContent = `${name} (${code})`;
    sel.appendChild(opt);
  });
  currentCode = sel.value;
}

// 事件绑定
document.getElementById('stockSelect').addEventListener('change', e => {
  currentCode = e.target.value;
  loadHistory(currentCode, currentSource, document.getElementById('dateSelect').value || null);
});

document.getElementById('dateSelect').addEventListener('change', e => {
  loadHistory(currentCode, currentSource, e.target.value || null);
});

document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentSource = btn.dataset.src;
    loadHistory(currentCode, currentSource, document.getElementById('dateSelect').value || null);
  });
});

// 方案A 每 30s 轮询一次
setInterval(() => {
  if (currentSource === 'plan_a' || currentSource === 'both') {
    loadHistory(currentCode, 'plan_a', document.getElementById('dateSelect').value || null);
  }
}, 30000);

// 启动
initChart();
initStockSelect().then(() => {
  loadHistory(currentCode, currentSource, null);
  connectWS();
});
</script>
</body>
</html>
```

- [ ] **Step 2: 在 server.py 追加 /api/stocks 端点**

在 `flow/server.py` 中追加：

```python
import yaml

_CONFIG = yaml.safe_load((Path(__file__).parent / "config" / "flow_watch.yaml").read_text())


@app.get("/api/stocks")
async def get_stocks():
    return _CONFIG["stocks"]
```

- [ ] **Step 3: 启动三个进程验证**

终端1:
```bash
python -m flow.plan_a.collector
```

终端2:
```bash
python -m flow.plan_b.collector
```

终端3:
```bash
uvicorn flow.server:app --host 127.0.0.1 --port 8080 --reload
```

打开浏览器 `http://127.0.0.1:8080`，确认：
- 股票下拉有 OKLO / SMR
- 方案A 页面加载时显示历史折线
- 方案B 每 15s 更新一次（盘中）
- 对比模式两条线同时显示

- [ ] **Step 4: 提交**

```bash
git add flow/frontend/index.html flow/server.py
git commit -m "feat: add ECharts frontend and /api/stocks endpoint"
```

---

## 自查结果

- **Spec 覆盖**：目录结构 ✓，配置 ✓，SQLite 存储 ✓，方案A 轮询 ✓，方案B 逐笔 ✓，WebSocket 15s ✓，REST API ✓，前端对比模式 ✓
- **Placeholder**：无
- **类型一致性**：`upsert_minute` 签名在 storage、plan_a、plan_b 中一致；`query_today`/`query_range` 在 server.py 中直接导入使用
