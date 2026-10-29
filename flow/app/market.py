"""市场时区与交易时段工具。

DB 中的 minute/time 字符串均为各市场本地时间（来自 futu 推送），
所有按时间查询、按日期重置的逻辑都必须使用对应市场时区。
"""
from datetime import datetime, time
from zoneinfo import ZoneInfo

_HK_TZ = ZoneInfo("Asia/Hong_Kong")
_US_TZ = ZoneInfo("America/New_York")

# 粗粒度常规交易时段（港股含午休、不含节假日，按需再细化）
_SESSION_START = time(9, 30)
_SESSION_END = time(16, 0)


def market_tz(code: str) -> ZoneInfo:
    return _HK_TZ if code.startswith("HK.") else _US_TZ


def market_now(code: str) -> datetime:
    return datetime.now(market_tz(code))


def in_session(code: str, now: datetime | None = None) -> bool:
    if now is None:
        now = market_now(code)
    if now.weekday() >= 5:
        return False
    return _SESSION_START <= now.time() < _SESSION_END
