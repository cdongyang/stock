from dataclasses import dataclass, field
from app.config import Thresholds

_DIR_MAP = {"Buyer": "buy", "Seller": "sell"}


@dataclass
class Classifier:
    thresholds: Thresholds
    _last: dict[str, str] = field(default_factory=dict, init=False)

    def classify(
        self, code: str, price: float, volume: int,
        ticker_direction: str, ask1: float = 0.0, bid1: float = 0.0,
    ) -> tuple[str, str, float]:
        """Returns (direction, tier, amount)."""
        amount = price * volume
        if ask1 > 0 and price >= ask1:
            direction = "buy"
        elif bid1 > 0 and price <= bid1:
            direction = "sell"
        else:
            direction = _DIR_MAP.get(str(ticker_direction).strip(), self._last.get(code, "buy"))
        self._last[code] = direction
        return direction, self.thresholds.tier(amount), amount
