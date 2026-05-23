import asyncio
import logging

from futu import OpenQuoteContext, RET_OK

from app.config import Config
from app.db import DB, FlowData

log = logging.getLogger(__name__)


def _f(val, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _fetch_all(cfg: Config) -> list[tuple[str, str, FlowData]]:
    ctx = OpenQuoteContext(host=cfg.futu.host, port=cfg.futu.port)
    results = []
    try:
        for stock in cfg.stocks:
            ret, df = ctx.get_capital_flow(stock.code)
            if ret != RET_OK:
                log.warning("Plan A get_capital_flow %s 失败: %s", stock.code, df)
                continue
            for _, row in df.iterrows():
                t = str(row.get("capital_flow_item_time", ""))[:16]
                if not t or t == "nan":
                    continue
                results.append((
                    stock.code,
                    t,
                    FlowData(
                        main_buy=_f(row.get("super_in_flow")),
                        fat_buy=_f(row.get("big_in_flow")),
                        mid_buy=_f(row.get("mid_in_flow")),
                        small_buy=_f(row.get("sml_in_flow")),
                    ),
                ))
            log.info("Plan A 写入 %s: %d 条", stock.code, len(df))
    finally:
        ctx.close()
    return results


async def run(cfg: Config, db: DB):
    log.info("Plan A 启动，监控: %s", [s.code for s in cfg.stocks])
    loop = asyncio.get_running_loop()
    while True:
        try:
            rows = await loop.run_in_executor(None, _fetch_all, cfg)
            for code, minute, data in rows:
                await db.upsert_flow(code, minute, "plan_a", data)
        except Exception as e:
            log.error("Plan A 轮询失败: %s", e)
        await asyncio.sleep(30)
