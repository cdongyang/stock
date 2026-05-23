import asyncio
import logging
from dataclasses import dataclass, field

from futu import OpenQuoteContext, RET_OK, SubType, TickerHandlerBase, StockQuoteHandlerBase

from app.classifier import Classifier
from app.config import Config
from app.db import DB, FlowData, TickRecord
from app.ws import WSManager

log = logging.getLogger(__name__)


@dataclass
class _Bucket:
    data: FlowData = field(default_factory=FlowData)

    def add(self, direction: str, tier: str, amount: float):
        attr = f"{tier}_{direction}"
        setattr(self.data, attr, getattr(self.data, attr) + amount)


class _TickHandler(TickerHandlerBase):
    def __init__(self, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue):
        self._loop = loop
        self._queue = queue

    def on_recv_rsp(self, rsp_pb):
        ret, df = super().on_recv_rsp(rsp_pb)
        if ret == RET_OK and df is not None and not df.empty:
            for _, row in df.iterrows():
                item = ("T",
                    str(row.get("code", "")),
                    float(row.get("price", 0) or 0),
                    int(row.get("volume", 0) or 0),
                    str(row.get("time", ""))[:19],
                    str(row.get("ticker_direction", "") or ""),
                )
                self._loop.call_soon_threadsafe(self._queue.put_nowait, item)
        return ret, df


class _QuoteHandler(StockQuoteHandlerBase):
    def __init__(self, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue):
        self._loop = loop
        self._queue = queue

    def on_recv_rsp(self, rsp_pb):
        ret, df = super().on_recv_rsp(rsp_pb)
        if ret == RET_OK and df is not None and not df.empty:
            for _, row in df.iterrows():
                item = ("Q",
                    str(row.get("code", "")),
                    float(row.get("ask_price", 0) or 0),
                    float(row.get("bid_price", 0) or 0),
                )
                self._loop.call_soon_threadsafe(self._queue.put_nowait, item)
        return ret, df


async def _consume(
    queue: asyncio.Queue,
    classifier: Classifier,
    db: DB,
    ws: WSManager,
):
    buckets: dict[str, tuple[str, _Bucket]] = {}
    quotes: dict[str, tuple[float, float]] = {}  # code -> (ask1, bid1)
    while True:
        item = await queue.get()
        if item[0] == "Q":
            _, code, ask1, bid1 = item
            quotes[code] = (ask1, bid1)
            continue
        _, code, price, volume, time_str, ticker_dir = item
        minute = time_str[:16]
        ask1, bid1 = quotes.get(code, (0.0, 0.0))
        direction, tier, amount = classifier.classify(code, price, volume, ticker_dir, ask1, bid1)

        if code in buckets and buckets[code][0] != minute:
            old_minute, old_bucket = buckets.pop(code)
            await db.upsert_flow(code, old_minute, "plan_b", old_bucket.data)

        if code not in buckets:
            buckets[code] = (minute, _Bucket())

        buckets[code][1].add(direction, tier, amount)

        if tier == "main":
            tick = TickRecord(
                code=code, time=time_str, price=price,
                volume=volume, amount=amount, direction=direction,
            )
            await db.insert_tick(tick)
            await ws.broadcast({
                "type": "tick",
                "data": {
                    "code": code, "time": time_str, "price": price,
                    "volume": volume, "amount": round(amount, 2), "direction": direction,
                },
            })


def _setup_futu(
    host: str, port: int, codes: list[str],
    loop: asyncio.AbstractEventLoop, queue: asyncio.Queue,
) -> OpenQuoteContext | None:
    try:
        ctx = OpenQuoteContext(host=host, port=port)
        ctx.set_handler(_TickHandler(loop, queue))
        ctx.set_handler(_QuoteHandler(loop, queue))
        ret, msg = ctx.subscribe(codes, [SubType.TICKER, SubType.QUOTE])
        if ret != RET_OK:
            log.error("Plan B subscribe 失败: %s", msg)
            ctx.close()
            return None
        return ctx
    except Exception as e:
        log.error("Plan B futu context 创建失败: %s", e)
        return None


async def run(cfg: Config, db: DB, ws: WSManager):
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    classifier = Classifier(cfg.thresholds)
    codes = [s.code for s in cfg.stocks]

    ctx = await loop.run_in_executor(
        None, _setup_futu, cfg.futu.host, cfg.futu.port, codes, loop, queue
    )
    if ctx is None:
        return

    log.info("Plan B 启动，监控: %s", codes)
    try:
        await _consume(queue, classifier, db, ws)
    finally:
        await loop.run_in_executor(None, ctx.close)
