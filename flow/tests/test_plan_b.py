import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.plan_b import _Bucket, _consume
from app.classifier import Classifier
from app.config import Thresholds
from app.db import DB

T = Thresholds(main=50000, fat=10000, mid=2000)

def test_bucket_add_buy():
    b = _Bucket()
    b.add("buy", "main", 55000.0)
    assert b.data.main_buy == 55000.0
    assert b.data.main_sell == 0.0

def test_bucket_add_sell():
    b = _Bucket()
    b.add("sell", "fat", 12000.0)
    assert b.data.fat_sell == 12000.0

def test_bucket_accumulates():
    b = _Bucket()
    b.add("buy", "mid", 3000.0)
    b.add("buy", "mid", 2500.0)
    assert b.data.mid_buy == 5500.0

@pytest.mark.asyncio
async def test_consumer_flushes_on_minute_change(tmp_path):
    db = DB(str(tmp_path / "test.db"))
    await db.open()
    ws = MagicMock()
    ws.broadcast = AsyncMock()
    classifier = Classifier(T)
    queue: asyncio.Queue = asyncio.Queue()

    await queue.put(("US.OKLO", 25.0, 100, "2026-05-18 14:30:05", "Buyer"))  # mid buy, 2500
    await queue.put(("US.OKLO", 25.0, 100, "2026-05-18 14:31:02", "Buyer"))  # flush trigger

    async def run_consumer():
        await _consume(queue, classifier, db, ws)

    task = asyncio.create_task(run_consumer())
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    rows = await db.query_flow("US.OKLO", "plan_b", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(rows) == 1
    assert rows[0]["minute"] == "2026-05-18 14:30"
    assert rows[0]["mid_buy"] == 2500.0
    await db.close()

@pytest.mark.asyncio
async def test_consumer_writes_tick_for_main(tmp_path):
    db = DB(str(tmp_path / "test2.db"))
    await db.open()
    ws = MagicMock()
    ws.broadcast = AsyncMock()
    classifier = Classifier(T)
    queue: asyncio.Queue = asyncio.Queue()

    # 特大单 buy: 25 * 2200 = 55000 >= 50000
    await queue.put(("US.OKLO", 25.0, 2200, "2026-05-18 14:30:10", "Buyer"))
    await queue.put(("US.OKLO", 25.0, 100,  "2026-05-18 14:31:00", "Buyer"))  # flush trigger

    async def run_consumer():
        await _consume(queue, classifier, db, ws)

    task = asyncio.create_task(run_consumer())
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    ticks = await db.query_ticks("US.OKLO", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(ticks) == 1
    assert ticks[0]["amount"] == 55000.0
    ws.broadcast.assert_called_once()
    call_arg = ws.broadcast.call_args[0][0]
    assert call_arg["type"] == "tick"
    assert call_arg["data"]["direction"] == "buy"
    await db.close()
