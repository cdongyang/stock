import logging

from futu import OpenQuoteContext, RET_OK, KLType

log = logging.getLogger(__name__)


def fetch_kline(host: str, port: int, code: str, date: str) -> list[dict]:
    ctx = OpenQuoteContext(host=host, port=port)
    try:
        ret, df, _ = ctx.request_history_kline(
            code, start=date, end=date, ktype=KLType.K_1M,
            max_count=2000, extended_time=True,
        )
        if ret != RET_OK or df is None or df.empty:
            log.warning("request_history_kline %s %s 失败: %s", code, date, df)
            return []
        result = []
        for _, row in df.iterrows():
            t = str(row.get("time_key", ""))
            if not t or t == "nan":
                continue
            result.append({
                "time":  t[:16],
                "open":  float(row.get("open",  0) or 0),
                "close": float(row.get("close", 0) or 0),
                "high":  float(row.get("high",  0) or 0),
                "low":   float(row.get("low",   0) or 0),
            })
        return result
    finally:
        ctx.close()
