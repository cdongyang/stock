import pytest
import pytest_asyncio
from app.db import DB, FlowData

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
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "other", FLOW)
    rows = await db.query_flow("US.OKLO", "other", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(rows) == 1
    assert rows[0]["main_buy"] == 100.0
    assert rows[0]["minute"] == "2026-05-18 14:30"

@pytest.mark.asyncio
async def test_upsert_idempotent(db):
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "other", FLOW)
    updated = FlowData(main_buy=999)
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "other", updated)
    rows = await db.query_flow("US.OKLO", "other", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(rows) == 1
    assert rows[0]["main_buy"] == 999.0

@pytest.mark.asyncio
async def test_source_isolation(db):
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "plan_a", FLOW)
    await db.upsert_flow("US.OKLO", "2026-05-18 14:30", "other", FLOW)
    ra = await db.query_flow("US.OKLO", "plan_a", "2026-05-18 00:00", "2026-05-18 23:59:59")
    ro = await db.query_flow("US.OKLO", "other", "2026-05-18 00:00", "2026-05-18 23:59:59")
    assert len(ra) == 1
    assert len(ro) == 1
