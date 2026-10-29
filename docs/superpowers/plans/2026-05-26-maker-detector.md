# Maker Detector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 扩展 `flow/app/` 服务，实时检测庄家进出场信号并通过飞书推送仓位建议。

**Architecture:** 在现有 `plan_b._consume` 管道里插入实时 main tick 检测（进场①/出货②）；独立 async task 每 60 秒扫描分钟级 DB 数据（进场②/出货①）；`Alert` 类管理冷却时间并调用飞书通知。

**Tech Stack:** Python 3.11+, asyncio, aiosqlite, futu-api, feishu_notify (scripts/)

---

## File Map

| 文件 | 操作 | 职责 |
|------|------|------|
| `flow/app/config.py` | 修改 | 增加 `DetectorConfig` dataclass |
| `flow/app/alert.py` | 新建 | 冷却管理 + 飞书通知 |
| `flow/app/detector.py` | 新建 | 四类信号检测 |
| `flow/app/plan_b.py` | 修改 | 接受 detector/alert 参数，main tick 转发 |
| `flow/app/main.py` | 修改 | 实例化 Alert/Detector，启动 minute_scan_loop |
| `flow/config/flow_watch.yaml` | 修改 | 增加 detector 配置块 |
| `flow/tests/test_config.py` | 修改 | 验证 DetectorConfig 加载 |
| `flow/tests/test_alert.py` | 新建 | 冷却逻辑单元测试 |
| `flow/tests/test_detector.py` | 新建 | 四类信号单元测试 |
| `flow/tests/test_plan_b.py` | 修改 | 修复现有测试的 tuple 格式 bug |

---

## Task 1: 在 `config.py` 增加 `DetectorConfig`

**Files:**
- Modify: `flow/app/config.py`
- Modify: `flow/tests/test_config.py`

- [ ] **Step 1: 写失败测试**

在 `flow/tests/test_config.py` 末尾追加：

```python
def test_detector_defaults():
    f = tmp_path / "cfg.yaml"
    f.write_text(YAML)
    cfg = load(f)
    assert cfg.detector.main_window == 10
    assert cfg.detector.maker_capital == 20_000_000.0

def test_detector_from_yaml(tmp_path):
    yaml = YAML + textwrap.dedent("""
        detector:
          main_window: 5
          minute_window: 3
          entry_main_threshold: 1000000
          exit_main_threshold: 1000000
          absorb_threshold: 500000
          dist_threshold: 300000
          rise_pct: 0.8
          price_flat_pct: 0.5
          cooldown_seconds: 120
          maker_capital: 10000000
    """)
    f = tmp_path / "cfg2.yaml"
    f.write_text(yaml)
    cfg = load(f)
    assert cfg.detector.main_window == 5
    assert cfg.detector.cooldown_seconds == 120
    assert cfg.detector.maker_capital == 10_000_000.0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd flow && python -m pytest tests/test_config.py -v 2>&1 | tail -20
```

预期：`AttributeError: 'Config' object has no attribute 'detector'`

- [ ] **Step 3: 实现 `DetectorConfig`**

在 `flow/app/config.py` 的 `Thresholds` 类之后，`Config` 类之前插入：

```python
from dataclasses import dataclass, field as dc_field

@dataclass
class DetectorConfig:
    main_window: int = 10
    minute_window: int = 5
    entry_main_threshold: float = 5_000_000.0
    exit_main_threshold: float = 5_000_000.0
    absorb_threshold: float = 3_000_000.0
    dist_threshold: float = 2_000_000.0
    rise_pct: float = 1.0
    price_flat_pct: float = 0.3
    cooldown_seconds: int = 300
    maker_capital: float = 20_000_000.0
```

在 `Config` dataclass 末尾增加字段（注意 `field` 需要 default_factory 因为不能用可变默认值）：

```python
@dataclass
class Config:
    stocks: list[Stock]
    server: ServerConfig
    futu: FutuConfig
    thresholds: Thresholds
    db_path: str
    detector: DetectorConfig = dc_field(default_factory=DetectorConfig)
```

在 `load()` 函数末尾的 `return Config(...)` 中加入 detector 解析：

```python
def load(path: str | Path | None = None) -> Config:
    if path is None:
        path = Path(__file__).parent.parent / "config" / "flow_watch.yaml"
    data = yaml.safe_load(Path(path).read_text())
    detector_data = data.get("detector", {})
    return Config(
        stocks=[Stock(**s) for s in data["stocks"]],
        server=ServerConfig(**data["server"]),
        futu=FutuConfig(**data["futu"]),
        thresholds=Thresholds(**data["thresholds"]),
        db_path=data.get("db_path", "data/flow.db"),
        detector=DetectorConfig(**detector_data) if detector_data else DetectorConfig(),
    )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd flow && python -m pytest tests/test_config.py -v 2>&1 | tail -20
```

预期：全部 PASS

- [ ] **Step 5: Commit**

```bash
git add flow/app/config.py flow/tests/test_config.py
git commit -m "feat(flow): add DetectorConfig to config"
```

---

## Task 2: 创建 `alert.py`（冷却管理 + 飞书通知）

**Files:**
- Create: `flow/app/alert.py`
- Create: `flow/tests/test_alert.py`

- [ ] **Step 1: 写失败测试**

新建 `flow/tests/test_alert.py`：

```python
import sys
import time
from unittest.mock import MagicMock, patch
from app.alert import Alert


def test_first_send_fires():
    alert = Alert(cooldown_seconds=300)
    with patch.object(alert, "_send_feishu", return_value=True) as mock:
        result = alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.0, 500_000, 20_000_000, "test")
    assert result is True
    mock.assert_called_once()


def test_same_direction_blocked_by_cooldown():
    alert = Alert(cooldown_seconds=300)
    with patch.object(alert, "_send_feishu", return_value=True) as mock:
        alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.0, 500_000, 20_000_000, "a")
        result = alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.1, 600_000, 20_000_000, "b")
    assert result is False
    assert mock.call_count == 1


def test_reversal_bypasses_cooldown():
    alert = Alert(cooldown_seconds=300)
    with patch.object(alert, "_send_feishu", return_value=True) as mock:
        alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.0, 500_000, 20_000_000, "entry")
        result = alert.send("US.OKLO", "Oklo", "出货②", "sell", 23.5, 500_000, 20_000_000, "exit")
    assert result is True
    assert mock.call_count == 2


def test_reversal_clears_opposite_cooldown():
    alert = Alert(cooldown_seconds=300)
    with patch.object(alert, "_send_feishu", return_value=True) as mock:
        alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.0, 500_000, 20_000_000, "a")
        alert.send("US.OKLO", "Oklo", "出货②", "sell", 23.5, 500_000, 20_000_000, "b")
        # After sell clears buy cooldown, another buy should fire
        result = alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.0, 500_000, 20_000_000, "c")
    assert result is True
    assert mock.call_count == 3


def test_different_stocks_independent():
    alert = Alert(cooldown_seconds=300)
    with patch.object(alert, "_send_feishu", return_value=True) as mock:
        alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.0, 500_000, 20_000_000, "a")
        alert.send("US.SMR", "NuScale", "进场①", "buy", 10.0, 500_000, 20_000_000, "b")
    assert mock.call_count == 2


def test_cooldown_expires():
    alert = Alert(cooldown_seconds=0)  # instant expiry
    with patch.object(alert, "_send_feishu", return_value=True) as mock:
        alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.0, 500_000, 20_000_000, "a")
        alert.send("US.OKLO", "Oklo", "进场①", "buy", 23.0, 500_000, 20_000_000, "b")
    assert mock.call_count == 2
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd flow && python -m pytest tests/test_alert.py -v 2>&1 | tail -10
```

预期：`ModuleNotFoundError: No module named 'app.alert'`

- [ ] **Step 3: 实现 `alert.py`**

新建 `flow/app/alert.py`：

```python
import logging
import sys
import time
from pathlib import Path

log = logging.getLogger(__name__)

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"


class Alert:
    def __init__(self, cooldown_seconds: int = 300):
        self._cooldown = cooldown_seconds
        self._last: dict[tuple[str, str], float] = {}

    def send(
        self,
        code: str,
        name: str,
        signal_type: str,
        direction: str,
        price: float,
        net_flow: float,
        maker_capital: float,
        details: str = "",
    ) -> bool:
        key = (code, direction)
        opposite = (code, "sell" if direction == "buy" else "buy")
        now = time.monotonic()

        is_reversal = (now - self._last.get(opposite, 0.0)) < self._cooldown
        if not is_reversal and (now - self._last.get(key, 0.0)) < self._cooldown:
            log.debug("Alert cooldown active: %s %s", code, direction)
            return False

        if is_reversal:
            self._last.pop(opposite, None)
        self._last[key] = now

        return self._send_feishu(code, name, signal_type, direction, price, net_flow, maker_capital, details)

    def _send_feishu(
        self,
        code: str,
        name: str,
        signal_type: str,
        direction: str,
        price: float,
        net_flow: float,
        maker_capital: float,
        details: str,
    ) -> bool:
        emoji = "🔔" if direction == "buy" else "⚠️"
        direction_label = "做多" if direction == "buy" else "减仓/观望"
        position_pct = min(100, round(abs(net_flow) / maker_capital * 100))
        suggestion = (
            f"{direction_label}，参考仓位 {position_pct}%"
            f"（{abs(net_flow)/10000:.0f}万/{maker_capital/10000:.0f}万）"
        )
        title = f"{emoji} [{code} {name}] 庄家{signal_type}"
        items = [details, f"价格：{price:.2f}", f"建议：{suggestion}"]

        if str(_SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(_SCRIPTS_DIR))
        try:
            from feishu_notify import send_notification  # type: ignore
            return send_notification(title=title, items=items)
        except Exception as e:
            log.error("飞书通知失败: %s", e)
            return False
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd flow && python -m pytest tests/test_alert.py -v 2>&1 | tail -15
```

预期：全部 PASS

- [ ] **Step 5: Commit**

```bash
git add flow/app/alert.py flow/tests/test_alert.py
git commit -m "feat(flow): add Alert class with cooldown and Feishu integration"
```

---

## Task 3: 创建 `detector.py`（四类信号检测）

**Files:**
- Create: `flow/app/detector.py`
- Create: `flow/tests/test_detector.py`

- [ ] **Step 1: 写失败测试**

新建 `flow/tests/test_detector.py`：

```python
import asyncio
from collections import deque
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.config import DetectorConfig
from app.detector import Detector

CFG = DetectorConfig(
    main_window=3,
    minute_window=3,
    entry_main_threshold=100_000.0,
    exit_main_threshold=100_000.0,
    absorb_threshold=50_000.0,
    dist_threshold=30_000.0,
    rise_pct=1.0,
    price_flat_pct=0.3,
    cooldown_seconds=300,
    maker_capital=1_000_000.0,
)


def test_no_signal_before_window_full():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 25.0)
    d.on_main_tick("US.OKLO", "Oklo", "buy", 60_000.0, alert)
    d.on_main_tick("US.OKLO", "Oklo", "buy", 60_000.0, alert)
    alert.send.assert_not_called()


def test_entry1_net_buy_triggers():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 25.0)
    for _ in range(3):
        d.on_main_tick("US.OKLO", "Oklo", "buy", 60_000.0, alert)  # net = 180000 > 100000
    alert.send.assert_called_once()
    kw = alert.send.call_args[1]
    assert kw["signal_type"] == "进场①"
    assert kw["direction"] == "buy"
    assert kw["code"] == "US.OKLO"


def test_exit2_net_sell_triggers():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 25.0)
    for _ in range(3):
        d.on_main_tick("US.OKLO", "Oklo", "sell", 60_000.0, alert)
    alert.send.assert_called_once()
    kw = alert.send.call_args[1]
    assert kw["signal_type"] == "出货②"
    assert kw["direction"] == "sell"


def test_mixed_window_below_threshold_no_signal():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 25.0)
    d.on_main_tick("US.OKLO", "Oklo", "buy", 60_000.0, alert)
    d.on_main_tick("US.OKLO", "Oklo", "sell", 60_000.0, alert)
    d.on_main_tick("US.OKLO", "Oklo", "buy", 60_000.0, alert)  # net = +60000 < 100000
    alert.send.assert_not_called()


def test_cum_net_included_in_send():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 25.0)
    for _ in range(3):
        d.on_main_tick("US.OKLO", "Oklo", "buy", 60_000.0, alert)
    kw = alert.send.call_args[1]
    assert kw["net_flow"] == pytest.approx(180_000.0)


@pytest.mark.asyncio
async def test_entry2_retail_sell_flat_price():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 25.0)

    db = MagicMock()
    db.query_flow = AsyncMock(return_value=[{
        "fat_buy": 0.0, "fat_sell": 60_000.0,
        "mid_buy": 0.0, "mid_sell": 0.0,
        "small_buy": 0.0, "small_sell": 0.0,
        "main_buy": 5_000.0, "main_sell": 0.0,  # maker buying → absorbing
    }])

    snaps = deque([25.0, 25.05], maxlen=11)  # price change 0.2% < 0.3%
    await d._scan_stock(db, "US.OKLO", "Oklo", "2026-05-26 14:00", "2026-05-26 14:03", snaps, alert)

    alert.send.assert_called_once()
    kw = alert.send.call_args[1]
    assert kw["signal_type"] == "进场②"
    assert kw["direction"] == "buy"


@pytest.mark.asyncio
async def test_entry2_price_moving_no_signal():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 24.0)

    db = MagicMock()
    db.query_flow = AsyncMock(return_value=[{
        "fat_buy": 0.0, "fat_sell": 60_000.0,
        "mid_buy": 0.0, "mid_sell": 0.0,
        "small_buy": 0.0, "small_sell": 0.0,
        "main_buy": 0.0, "main_sell": 0.0,
    }])

    # price dropped 1.6% → too much movement, not flat
    snaps = deque([25.0, 24.0], maxlen=11)
    await d._scan_stock(db, "US.OKLO", "Oklo", "2026-05-26 14:00", "2026-05-26 14:03", snaps, alert)

    alert.send.assert_not_called()


@pytest.mark.asyncio
async def test_exit1_price_rise_then_flat_retail_buying():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 25.3)

    db = MagicMock()
    db.query_flow = AsyncMock(return_value=[{
        "fat_buy": 40_000.0, "fat_sell": 0.0,
        "mid_buy": 0.0, "mid_sell": 0.0,
        "small_buy": 0.0, "small_sell": 0.0,
        "main_buy": 0.0, "main_sell": 5_000.0,  # maker not buying
    }])

    # Enough history: minute_window=3, needed = 2+3+1 = 6 snapshots
    # Prices: older → newer: 24.9 25.0 25.1 25.2 25.3 25.3
    # price_flat_start = snaps[-3] = 25.2, price_flat_end = snaps[-1] = 25.3
    # flat change = (25.3-25.2)/25.2*100 = 0.4% -- actually let's use smaller:
    # 25.25 25.26 25.27 for last 3 to get ~0.08% flat change
    # prior rise from snaps[-(3+3)] = snaps[-6] = 24.9 to snaps[-3] = 25.25 = 1.4% > 1.0%
    snaps = deque([24.9, 25.0, 25.1, 25.25, 25.26, 25.27], maxlen=11)
    await d._scan_stock(db, "US.OKLO", "Oklo", "2026-05-26 14:00", "2026-05-26 14:03", snaps, alert)

    alert.send.assert_called_once()
    kw = alert.send.call_args[1]
    assert kw["signal_type"] == "出货①"
    assert kw["direction"] == "sell"


@pytest.mark.asyncio
async def test_exit1_no_prior_rise_no_signal():
    d = Detector(CFG)
    alert = MagicMock()
    d.update_quote("US.OKLO", 25.0)

    db = MagicMock()
    db.query_flow = AsyncMock(return_value=[{
        "fat_buy": 40_000.0, "fat_sell": 0.0,
        "mid_buy": 0.0, "mid_sell": 0.0,
        "small_buy": 0.0, "small_sell": 0.0,
        "main_buy": 0.0, "main_sell": 0.0,
    }])

    # Price flat throughout, no prior rise
    snaps = deque([25.0, 25.0, 25.0, 25.0, 25.0, 25.0], maxlen=11)
    await d._scan_stock(db, "US.OKLO", "Oklo", "2026-05-26 14:00", "2026-05-26 14:03", snaps, alert)

    alert.send.assert_not_called()
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd flow && python -m pytest tests/test_detector.py -v 2>&1 | tail -10
```

预期：`ModuleNotFoundError: No module named 'app.detector'`

- [ ] **Step 3: 实现 `detector.py`**

新建 `flow/app/detector.py`：

```python
import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.config import DetectorConfig
from app.db import DB

log = logging.getLogger(__name__)


@dataclass
class Detector:
    cfg: DetectorConfig
    _windows: dict[str, deque] = field(default_factory=dict, init=False)
    _quotes: dict[str, float] = field(default_factory=dict, init=False)
    _cum_net: dict[str, float] = field(default_factory=dict, init=False)
    _price_snapshots: dict[str, deque] = field(default_factory=dict, init=False)
    _last_date: str = field(default="", init=False)

    def update_quote(self, code: str, price: float) -> None:
        self._quotes[code] = price

    def on_main_tick(
        self, code: str, name: str, direction: str, amount: float, alert
    ) -> None:
        win = self._windows.setdefault(code, deque(maxlen=self.cfg.main_window))
        signed = amount if direction == "buy" else -amount
        win.append(signed)
        self._cum_net[code] = self._cum_net.get(code, 0.0) + signed

        if len(win) < self.cfg.main_window:
            return

        window_net = sum(win)
        price = self._quotes.get(code, 0.0)

        if window_net >= self.cfg.entry_main_threshold:
            alert.send(
                code=code,
                name=name,
                signal_type="进场①",
                direction="buy",
                price=price,
                net_flow=self._cum_net[code],
                maker_capital=self.cfg.maker_capital,
                details=f"main 大单连续净买入 ¥{window_net/10000:.0f}万",
            )
        elif window_net <= -self.cfg.exit_main_threshold:
            alert.send(
                code=code,
                name=name,
                signal_type="出货②",
                direction="sell",
                price=price,
                net_flow=self._cum_net[code],
                maker_capital=self.cfg.maker_capital,
                details=f"main 大单连续净卖出 ¥{abs(window_net)/10000:.0f}万",
            )

    async def minute_scan_loop(self, db: DB, stocks: list, alert) -> None:
        max_snap = self.cfg.minute_window * 2 + 2
        while True:
            await asyncio.sleep(60)
            today = datetime.now().strftime("%Y-%m-%d")
            if today != self._last_date:
                self._cum_net.clear()
                self._price_snapshots.clear()
                self._last_date = today

            now = datetime.now()
            start = (now - timedelta(minutes=self.cfg.minute_window)).strftime("%Y-%m-%d %H:%M")
            end = now.strftime("%Y-%m-%d %H:%M")

            for stock in stocks:
                try:
                    price = self._quotes.get(stock.code, 0.0)
                    snaps = self._price_snapshots.setdefault(
                        stock.code, deque(maxlen=max_snap)
                    )
                    snaps.append(price)
                    await self._scan_stock(db, stock.code, stock.name, start, end, snaps, alert)
                except Exception as e:
                    log.error("minute_scan error %s: %s", stock.code, e)

    async def _scan_stock(
        self,
        db: DB,
        code: str,
        name: str,
        start: str,
        end: str,
        price_snaps: deque,
        alert,
    ) -> None:
        rows = await db.query_flow(code, "plan_b", start, end)
        if not rows:
            return

        fat_net = sum(r["fat_buy"] - r["fat_sell"] for r in rows)
        mid_net = sum(r["mid_buy"] - r["mid_sell"] for r in rows)
        small_net = sum(r["small_buy"] - r["small_sell"] for r in rows)
        retail_net = fat_net + mid_net + small_net
        main_net = sum(r["main_buy"] - r["main_sell"] for r in rows)

        price_now = price_snaps[-1] if price_snaps else 0.0
        if price_now == 0.0:
            return

        # 进场②: 散户净卖出 + 价格平稳 + 庄家未净卖出
        if retail_net <= -self.cfg.absorb_threshold and main_net >= 0:
            price_past = price_snaps[0] if len(price_snaps) > 1 else price_now
            change_pct = abs((price_now - price_past) / price_past * 100) if price_past else 0.0
            if change_pct <= self.cfg.price_flat_pct:
                alert.send(
                    code=code,
                    name=name,
                    signal_type="进场②",
                    direction="buy",
                    price=price_now,
                    net_flow=self._cum_net.get(code, 0.0),
                    maker_capital=self.cfg.maker_capital,
                    details=f"散户净卖出 ¥{abs(retail_net)/10000:.0f}万，价格平稳（{change_pct:.2f}%）",
                )

        # 出货①: 散户净买入 + 庄家未净买入 + 先涨后停滞
        if retail_net >= self.cfg.dist_threshold and main_net <= 0:
            needed = 2 + self.cfg.minute_window + 1
            if len(price_snaps) >= needed:
                price_flat_start = price_snaps[-3]
                price_flat_end = price_snaps[-1]
                price_rise_start = price_snaps[-(3 + self.cfg.minute_window)]
                if price_flat_start > 0 and price_rise_start > 0:
                    flat_pct = abs((price_flat_end - price_flat_start) / price_flat_start * 100)
                    rise_pct = (price_flat_start - price_rise_start) / price_rise_start * 100
                    if rise_pct >= self.cfg.rise_pct and flat_pct <= 0.2:
                        alert.send(
                            code=code,
                            name=name,
                            signal_type="出货①",
                            direction="sell",
                            price=price_now,
                            net_flow=self._cum_net.get(code, 0.0),
                            maker_capital=self.cfg.maker_capital,
                            details=f"涨幅{rise_pct:.1f}%后停滞，散户净买入 ¥{retail_net/10000:.0f}万",
                        )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd flow && python -m pytest tests/test_detector.py -v 2>&1 | tail -20
```

预期：全部 PASS

- [ ] **Step 5: Commit**

```bash
git add flow/app/detector.py flow/tests/test_detector.py
git commit -m "feat(flow): add Detector with four maker signal types"
```

---

## Task 4: 修改 `plan_b.py` 接入 Detector，修复现有测试

**Files:**
- Modify: `flow/app/plan_b.py`
- Modify: `flow/tests/test_plan_b.py`

- [ ] **Step 1: 修复现有 test_plan_b.py 的 tuple 格式 bug**

现有测试使用 5-tuple，但 `_consume` 期望 6-tuple（带 "T" 前缀）。
将 `flow/tests/test_plan_b.py` 中所有 `queue.put` 改为 6-tuple 格式：

```python
# 将这两处：
await queue.put(("US.OKLO", 25.0, 100, "2026-05-18 14:30:05", "Buyer"))
await queue.put(("US.OKLO", 25.0, 100, "2026-05-18 14:31:02", "Buyer"))
# 改为：
await queue.put(("T", "US.OKLO", 25.0, 100, "2026-05-18 14:30:05", "Buyer"))
await queue.put(("T", "US.OKLO", 25.0, 100, "2026-05-18 14:31:02", "Buyer"))

# 以及第二个测试中的：
await queue.put(("T", "US.OKLO", 25.0, 2200, "2026-05-18 14:30:10", "Buyer"))
await queue.put(("T", "US.OKLO", 25.0, 100,  "2026-05-18 14:31:00", "Buyer"))
```

还需要更新 `_consume` 调用，加上两个新参数 `detector=None, alert=None`（签名改动在 Step 3）。

- [ ] **Step 2: 确认现有测试当前失败**

```bash
cd flow && python -m pytest tests/test_plan_b.py -v 2>&1 | tail -15
```

预期：`ValueError: not enough values to unpack`

- [ ] **Step 3: 修改 `plan_b.py`**

将 `_consume` 签名改为：

```python
async def _consume(
    queue: asyncio.Queue,
    classifier: Classifier,
    db: DB,
    ws: WSManager,
    detector=None,
    alert=None,
    stocks_by_code: dict | None = None,
):
```

在 `if item[0] == "Q":` 块中，`quotes[code] = (ask1, bid1)` 之后添加：

```python
    if detector:
        mid = (ask1 + bid1) / 2 if ask1 and bid1 else (ask1 or bid1)
        detector.update_quote(code, mid)
    continue
```

在 `if tier == "main":` 块末尾（`await ws.broadcast(...)` 之后）添加：

```python
        if detector and alert and stocks_by_code:
            stock = stocks_by_code.get(code)
            if stock:
                detector.on_main_tick(code, stock.name, direction, amount, alert)
```

将 `run()` 签名改为：

```python
async def run(cfg: Config, db: DB, ws: WSManager, detector=None, alert=None):
```

在 `run()` 内 `codes = [s.code for s in cfg.stocks]` 之后添加：

```python
    stocks_by_code = {s.code: s for s in cfg.stocks}
```

将 `_consume` 调用改为：

```python
    await _consume(queue, classifier, db, ws, detector, alert, stocks_by_code)
```

- [ ] **Step 4: 运行所有测试确认通过**

```bash
cd flow && python -m pytest tests/test_plan_b.py tests/test_classifier.py -v 2>&1 | tail -20
```

预期：全部 PASS

- [ ] **Step 5: Commit**

```bash
git add flow/app/plan_b.py flow/tests/test_plan_b.py
git commit -m "feat(flow): wire Detector into plan_b consume loop, fix tuple format in tests"
```

---

## Task 5: 修改 `main.py` 启动 Detector

**Files:**
- Modify: `flow/app/main.py`

- [ ] **Step 1: 确认 main.py 当前不引用 Alert/Detector**

```bash
grep -n "Alert\|Detector\|detector\|alert" flow/app/main.py
```

预期：无输出

- [ ] **Step 2: 修改 `main.py`**

在现有 import 块末尾（`import app.plan_b as plan_b` 之后）添加：

```python
from app.alert import Alert
from app.detector import Detector
```

将 `lifespan` 函数改为：

```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    await _db.open()
    _alert = Alert(cooldown_seconds=_cfg.detector.cooldown_seconds)
    _detector = Detector(_cfg.detector)
    asyncio.create_task(plan_a.run(_cfg, _db))
    asyncio.create_task(plan_b.run(_cfg, _db, _ws, _detector, _alert))
    asyncio.create_task(_detector.minute_scan_loop(_db, _cfg.stocks, _alert))
    asyncio.create_task(_broadcast_loop())
    yield
    await _db.close()
```

- [ ] **Step 3: 运行全套测试确认无回归**

```bash
cd flow && python -m pytest tests/ -v 2>&1 | tail -25
```

预期：全部 PASS

- [ ] **Step 4: Commit**

```bash
git add flow/app/main.py
git commit -m "feat(flow): instantiate Alert and Detector in app lifespan"
```

---

## Task 6: 更新 `flow_watch.yaml` 加入 detector 配置

**Files:**
- Modify: `flow/config/flow_watch.yaml`

- [ ] **Step 1: 在 YAML 末尾追加 detector 块**

将 `flow/config/flow_watch.yaml` 改为：

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

thresholds:
  main: 50000
  fat:  10000
  mid:  2000

db_path: data/flow.db

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

- [ ] **Step 2: 验证配置能正确加载**

```bash
cd flow && python -c "
from app.config import load
cfg = load()
print('detector.main_window:', cfg.detector.main_window)
print('detector.maker_capital:', cfg.detector.maker_capital)
print('stocks:', [s.code for s in cfg.stocks])
"
```

预期输出：
```
detector.main_window: 10
detector.maker_capital: 20000000.0
stocks: ['US.OKLO', 'US.SMR']
```

- [ ] **Step 3: 运行全套测试最终确认**

```bash
cd flow && python -m pytest tests/ -v 2>&1 | tail -30
```

预期：全部 PASS

- [ ] **Step 4: Commit**

```bash
git add flow/config/flow_watch.yaml
git commit -m "feat(flow): add detector config for OKLO monitoring"
```
