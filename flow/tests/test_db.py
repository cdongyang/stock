import pytest
import pytest_asyncio
from app.db import DB, FlowData, TickRecord

@pytest_asyncio.fixture
async def db(tmp_path):
    d = DB(str(tmp_path / "test.db"))
    await d.open()
    yield d
    await d.close()

FLOW = FlowData(main_buy=100, main_sell=40, fat_buy=50, fat_sell=20,
                mid_buy=30, mid_sell=10, small_buy=10, small_sell=5)

@pytest.mark.asyncio
async def test_upsert_and_query(db):
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "plan_b", FLOW)
    rows = await db.query_flow("US.OKLO", "plan_b", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(rows) == 1
    assert rows[0]["main_buy"] == 100.0
    assert rows[0]["minute"] == "2026-05-18 14:30"

@pytest.mark.asyncio
async def test_upsert_idempotent(db):
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "plan_b", FLOW)
    updated = FlowData(main_buy=999)
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "plan_b", updated)
    rows = await db.query_flow("US.OKLO", "plan_b", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(rows) == 1
    assert rows[0]["main_buy"] == 999.0

@pytest.mark.asyncio
async def test_source_isolation(db):
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "plan_a", FLOW)
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "plan_b", FLOW)
    ra = await db.query_flow("US.OKLO", "plan_a", "2026-05-18 00:00", "2026-05-18 23:59:59")
    rb = await db.query_flow("US.OKLO", "plan_b", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(ra) == 1
    assert len(rb) == 1

@pytest.mark.asyncio
async def test_insert_and_query_ticks(db):
    tick = TickRecord(code="US.OKLO", time="2026-05-18 14:30:05",
                      price=25.5, volume=2100, amount=53550.0, direction="buy")
    await db.insert_tick(tick)
    rows = await db.query_ticks("US.OKLO", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(rows) == 1
    assert rows[0]["direction"] == "buy"
    assert rows[0]["amount"] == 53550.0

@pytest.mark.asyncio
async def test_query_ticks_direction_filter(db):
    await db.insert_tick(TickRecord("US.OKLO", "2026-05-18 14:30:05", 25.0, 2100, 52500.0, "buy"))
    await db.insert_tick(TickRecord("US.OKLO", "2026-05-18 14:31:00", 25.0, 2200, 55000.0, "sell"))
    buys = await db.query_ticks("US.OKLO", "2026-05-18 00:00", "2026-05-18 23:59:59", "buy")
    assert len(buys) == 1
    assert buys[0]["direction"] == "buy"
