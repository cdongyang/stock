from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from app.plan_a import _fetch_all, _f
from app.config import Config, Stock, ServerConfig, FutuConfig, Thresholds

CFG = Config(
    stocks=[Stock("US.OKLO", "Oklo")],
    server=ServerConfig("127.0.0.1", 8080),
    futu=FutuConfig("127.0.0.1", 11111),
    thresholds=Thresholds(50000, 10000, 2000),
    db_path="data/flow.db",
)

def _make_df():
    return pd.DataFrame([{
        "capital_flow_item_time": "2026-05-18 14:30:00",
        "super_in_flow": 10000.0,
        "big_in_flow":   5000.0,
        "mid_in_flow":   1000.0,
        "sml_in_flow":   300.0,
    }])

def test_fetch_all_maps_fields():
    mock_ctx = MagicMock()
    mock_ctx.get_capital_flow.return_value = (0, _make_df())

    with patch("app.plan_a.OpenQuoteContext", return_value=mock_ctx):
        results = _fetch_all(CFG)

    assert len(results) == 1
    code, minute, data = results[0]
    assert code == "US.OKLO"
    assert minute == "2026-05-18 14:30"
    assert data.main_buy == 10000.0
    assert data.fat_buy  == 5000.0
    assert data.mid_buy  == 1000.0
    assert data.small_buy == 300.0
    assert data.main_sell == 0.0

def test_fetch_all_skips_na():
    df = pd.DataFrame([{
        "capital_flow_item_time": "2026-05-18 14:31:00",
        "super_in_flow": "N/A",
        "big_in_flow": None,
        "mid_in_flow": 0,
        "sml_in_flow": 0,
    }])
    mock_ctx = MagicMock()
    mock_ctx.get_capital_flow.return_value = (0, df)
    with patch("app.plan_a.OpenQuoteContext", return_value=mock_ctx):
        results = _fetch_all(CFG)
    _, _, data = results[0]
    assert data.main_buy == 0.0
    assert data.fat_buy == 0.0

def test_f_handles_na():
    assert _f("N/A") == 0.0
    assert _f(None) == 0.0
    assert _f(123.4) == 123.4
