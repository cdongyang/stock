from app.classifier import Classifier
from app.config import Thresholds

T = Thresholds(main=50000, fat=10000, mid=2000)

def test_direction_buyer():
    c = Classifier(T)
    direction, tier, amount = c.classify("US.OKLO", 25.0, 100, "Buyer")
    assert direction == "buy"
    assert amount == 2500.0

def test_direction_seller():
    c = Classifier(T)
    direction, _, _ = c.classify("US.OKLO", 25.0, 100, "Seller")
    assert direction == "sell"

def test_direction_inherits_last():
    c = Classifier(T)
    c.classify("US.OKLO", 25.0, 100, "Buyer")
    direction, _, _ = c.classify("US.OKLO", 25.0, 100, "")
    assert direction == "buy"

def test_direction_default_buy_on_first_unknown():
    c = Classifier(T)
    direction, _, _ = c.classify("US.OKLO", 25.0, 100, "")
    assert direction == "buy"

def test_tier_main():
    c = Classifier(T)
    _, tier, amount = c.classify("US.OKLO", 25.0, 2200, "Buyer")
    assert tier == "main"
    assert amount == 55000.0

def test_tier_fat():
    c = Classifier(T)
    _, tier, _ = c.classify("US.OKLO", 25.0, 400, "Buyer")
    assert tier == "fat"

def test_tier_mid():
    c = Classifier(T)
    _, tier, _ = c.classify("US.OKLO", 25.0, 100, "Buyer")
    assert tier == "mid"

def test_tier_small():
    c = Classifier(T)
    _, tier, _ = c.classify("US.OKLO", 25.0, 79, "Buyer")
    assert tier == "small"

def test_per_code_isolation():
    c = Classifier(T)
    c.classify("US.OKLO", 25.0, 100, "Buyer")
    c.classify("US.SMR",  10.0, 100, "Seller")
    d1, _, _ = c.classify("US.OKLO", 25.0, 100, "")
    d2, _, _ = c.classify("US.SMR",  10.0, 100, "")
    assert d1 == "buy"
    assert d2 == "sell"
