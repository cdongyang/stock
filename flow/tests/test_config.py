import textwrap
from pathlib import Path
import pytest
from app.config import load, Thresholds

YAML = textwrap.dedent("""
    stocks:
      - code: US.OKLO
        name: Oklo
    server:
      host: 127.0.0.1
      port: 8080
    futu:
      host: 127.0.0.1
      port: 11111
    thresholds:
      main: 50000
      fat: 10000
      mid: 2000
    db_path: data/flow.db
""")

def test_load(tmp_path):
    f = tmp_path / "cfg.yaml"
    f.write_text(YAML)
    cfg = load(f)
    assert cfg.stocks[0].code == "US.OKLO"
    assert cfg.server.port == 8080
    assert cfg.futu.port == 11111
    assert cfg.db_path == "data/flow.db"

def test_thresholds_tier():
    t = Thresholds(main=50000, fat=10000, mid=2000)
    assert t.tier(60000) == "main"
    assert t.tier(50000) == "main"
    assert t.tier(49999) == "fat"
    assert t.tier(10000) == "fat"
    assert t.tier(9999)  == "mid"
    assert t.tier(2000)  == "mid"
    assert t.tier(1999)  == "small"
