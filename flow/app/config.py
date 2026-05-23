from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class Stock:
    code: str
    name: str


@dataclass
class ServerConfig:
    host: str
    port: int


@dataclass
class FutuConfig:
    host: str
    port: int


@dataclass
class Thresholds:
    main: float
    fat: float
    mid: float

    def tier(self, amount: float) -> str:
        if amount >= self.main:
            return "main"
        if amount >= self.fat:
            return "fat"
        if amount >= self.mid:
            return "mid"
        return "small"


@dataclass
class Config:
    stocks: list[Stock]
    server: ServerConfig
    futu: FutuConfig
    thresholds: Thresholds
    db_path: str


def load(path: str | Path | None = None) -> Config:
    if path is None:
        path = Path(__file__).parent.parent / "config" / "flow_watch.yaml"
    data = yaml.safe_load(Path(path).read_text())
    return Config(
        stocks=[Stock(**s) for s in data["stocks"]],
        server=ServerConfig(**data["server"]),
        futu=FutuConfig(**data["futu"]),
        thresholds=Thresholds(**data["thresholds"]),
        db_path=data.get("db_path", "data/flow.db"),
    )
