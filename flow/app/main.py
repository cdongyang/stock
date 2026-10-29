import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from app.config import load as load_config
from app.db import DB
from app.market import market_tz
from app.ws import WSManager
import app.plan_a as plan_a
import app.kline as kline_mod

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger(__name__)

_cfg = load_config()
_db = DB(_cfg.db_path)
_ws = WSManager()
_tasks: set[asyncio.Task] = set()


def _spawn(coro, name: str) -> None:
    # 保留引用防止任务被 GC，异常退出时记录日志
    task = asyncio.create_task(coro, name=name)
    _tasks.add(task)
    task.add_done_callback(_on_task_done)


def _on_task_done(task: asyncio.Task) -> None:
    _tasks.discard(task)
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        log.error("后台任务 %s 异常退出: %r", task.get_name(), exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await _db.open()
    _spawn(plan_a.run(_cfg, _db), "plan_a")
    yield
    for task in list(_tasks):
        task.cancel()
    await _db.close()


app = FastAPI(lifespan=lifespan)


@app.get("/api/stocks")
async def get_stocks():
    return [{"code": s.code, "name": s.name} for s in _cfg.stocks]


@app.get("/api/flow/{code}")
async def get_flow(code: str, source: str = "plan_a", date: str | None = None):
    target = date or datetime.now(market_tz(code)).strftime("%Y-%m-%d")
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
    target = date or datetime.now(market_tz(code)).strftime("%Y-%m-%d")
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, kline_mod.fetch_kline, _cfg.futu.host, _cfg.futu.port, code, target
    )


@app.get("/api/latest_date/{code}")
async def get_latest_date(code: str, source: str = "plan_a"):
    date = await _db.query_latest_date(code, source)
    return {"date": date}


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
