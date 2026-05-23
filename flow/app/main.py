import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from app.config import load as load_config
from app.db import DB
from app.ws import WSManager
import app.plan_a as plan_a
import app.plan_b as plan_b
import app.kline as kline_mod

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger(__name__)

_cfg = load_config()
_db = DB(_cfg.db_path)
_ws = WSManager()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await _db.open()
    asyncio.create_task(plan_a.run(_cfg, _db))
    asyncio.create_task(plan_b.run(_cfg, _db, _ws))
    asyncio.create_task(_broadcast_loop())
    yield
    await _db.close()


app = FastAPI(lifespan=lifespan)


async def _broadcast_loop():
    while True:
        await asyncio.sleep(15)
        for stock in _cfg.stocks:
            await _ws.broadcast({"type": "flow_update", "code": stock.code, "source": "plan_b"})


def _market_tz(code: str) -> ZoneInfo:
    return ZoneInfo("Asia/Hong_Kong") if code.startswith("HK.") else ZoneInfo("America/New_York")


@app.get("/api/stocks")
async def get_stocks():
    return [{"code": s.code, "name": s.name} for s in _cfg.stocks]


@app.get("/api/flow/{code}")
async def get_flow(code: str, source: str = "plan_b", date: str | None = None):
    target = date or datetime.now(_market_tz(code)).strftime("%Y-%m-%d")
    rows = await _db.query_flow(code, source, f"{target} 00:00", f"{target} 23:59:59")
    result = []
    cum = 0.0
    for r in rows:
        net = (r["main_buy"] + r["fat_buy"] + r["mid_buy"] + r["small_buy"]) - \
              (r["main_sell"] + r["fat_sell"] + r["mid_sell"] + r["small_sell"])
        cum += net
        result.append({
            "minute":      r["minute"],
            "main_net":    round(r["main_buy"]  - r["main_sell"],  2),
            "fat_net":     round(r["fat_buy"]   - r["fat_sell"],   2),
            "mid_net":     round(r["mid_buy"]   - r["mid_sell"],   2),
            "small_net":   round(r["small_buy"] - r["small_sell"], 2),
            "cum_net_flow": round(cum, 2),
        })
    return result


@app.get("/api/kline/{code}")
async def get_kline(code: str, date: str | None = None):
    target = date or datetime.now(_market_tz(code)).strftime("%Y-%m-%d")
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, kline_mod.fetch_kline, _cfg.futu.host, _cfg.futu.port, code, target
    )


@app.get("/api/latest_date/{code}")
async def get_latest_date(code: str, source: str = "plan_b"):
    date = await _db.query_latest_date(code, source)
    return {"date": date}


@app.get("/api/ticks/{code}")
async def get_ticks(code: str, direction: str = "all", date: str | None = None):
    target = date or datetime.now(_market_tz(code)).strftime("%Y-%m-%d")
    return await _db.query_ticks(code, f"{target} 00:00", f"{target} 23:59:59", direction)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await _ws.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await _ws.disconnect(ws)


app.mount("/", StaticFiles(directory="frontend", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=_cfg.server.host, port=_cfg.server.port)
