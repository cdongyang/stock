from datetime import datetime
from zoneinfo import ZoneInfo

from app.market import market_tz, in_session

ET = ZoneInfo("America/New_York")
HKT = ZoneInfo("Asia/Hong_Kong")


def test_market_tz_us():
    assert market_tz("US.OKLO").key == "America/New_York"


def test_market_tz_hk():
    assert market_tz("HK.00700").key == "Asia/Hong_Kong"


def test_in_session_us_trading_hours():
    # 2026-06-10 是周三
    assert in_session("US.OKLO", datetime(2026, 6, 10, 10, 0, tzinfo=ET))


def test_in_session_us_after_close():
    assert not in_session("US.OKLO", datetime(2026, 6, 10, 20, 0, tzinfo=ET))


def test_in_session_us_before_open():
    assert not in_session("US.OKLO", datetime(2026, 6, 10, 9, 0, tzinfo=ET))


def test_in_session_weekend():
    # 2026-06-13 是周六
    assert not in_session("US.OKLO", datetime(2026, 6, 13, 10, 0, tzinfo=ET))


def test_in_session_hk_trading_hours():
    assert in_session("HK.00700", datetime(2026, 6, 10, 10, 0, tzinfo=HKT))
