import os
from dataclasses import dataclass

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS capital_flow (
    id         INTEGER PRIMARY KEY,
    code       TEXT NOT NULL,
    minute     TEXT NOT NULL,
    source     TEXT NOT NULL,
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
CREATE INDEX IF NOT EXISTS idx_flow ON capital_flow(code, minute, source);
"""


@dataclass
class FlowData:
    main_buy: float = 0.0
    main_sell: float = 0.0
    fat_buy: float = 0.0
    fat_sell: float = 0.0
    mid_buy: float = 0.0
    mid_sell: float = 0.0
    small_buy: float = 0.0
    small_sell: float = 0.0


class DB:
    def __init__(self, path: str):
        self.path = path
        self._conn: aiosqlite.Connection | None = None

    async def open(self):
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._conn = await aiosqlite.connect(self.path)
        await self._conn.executescript(_SCHEMA)
        await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()

    async def upsert_flow(self, code: str, minute: str, source: str, data: FlowData):
        await self._conn.execute(
            """
            INSERT INTO capital_flow
                (code, minute, source, main_buy, main_sell, fat_buy, fat_sell,
                 mid_buy, mid_sell, small_buy, small_sell)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(code, minute, source) DO UPDATE SET
                main_buy=excluded.main_buy,   main_sell=excluded.main_sell,
                fat_buy=excluded.fat_buy,     fat_sell=excluded.fat_sell,
                mid_buy=excluded.mid_buy,     mid_sell=excluded.mid_sell,
                small_buy=excluded.small_buy, small_sell=excluded.small_sell
            """,
            (code, minute, source,
             data.main_buy, data.main_sell,
             data.fat_buy,  data.fat_sell,
             data.mid_buy,  data.mid_sell,
             data.small_buy, data.small_sell),
        )
        await self._conn.commit()

    async def query_flow(self, code: str, source: str, start: str, end: str) -> list[dict]:
        cols = ("minute", "main_buy", "main_sell", "fat_buy", "fat_sell",
                "mid_buy", "mid_sell", "small_buy", "small_sell")
        async with self._conn.execute(
            f"SELECT {','.join(cols)} FROM capital_flow "
            "WHERE code=? AND source=? AND minute BETWEEN ? AND ? ORDER BY minute",
            (code, source, start, end),
        ) as cur:
            return [dict(zip(cols, row)) async for row in cur]

    async def query_latest_date(self, code: str, source: str) -> str | None:
        async with self._conn.execute(
            "SELECT substr(minute,1,10) FROM capital_flow WHERE code=? AND source=? ORDER BY minute DESC LIMIT 1",
            (code, source),
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else None
