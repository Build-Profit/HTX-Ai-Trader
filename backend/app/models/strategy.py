from dataclasses import asdict, dataclass
from typing import Dict


SUPPORTED_SYMBOLS = {"BTC/USDT", "ETH/USDT"}
SUPPORTED_TIMEFRAMES = {"1m", "5m", "1h", "4h", "1d"}


@dataclass(frozen=True)
class EntryRule:
    type: str
    drop_percent: float

    def to_dict(self) -> Dict[str, float]:
        return {"type": self.type, "dropPercent": self.drop_percent}


@dataclass(frozen=True)
class ExitRule:
    take_profit_percent: float
    stop_loss_percent: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "takeProfitPercent": self.take_profit_percent,
            "stopLossPercent": self.stop_loss_percent,
        }


@dataclass(frozen=True)
class RiskRule:
    max_drawdown_percent: float
    position_size_percent: float
    risk_level: str

    def to_dict(self) -> Dict[str, float]:
        return {
            "maxDrawdownPercent": self.max_drawdown_percent,
            "positionSizePercent": self.position_size_percent,
            "riskLevel": self.risk_level,
        }


@dataclass(frozen=True)
class Strategy:
    symbol: str
    timeframe: str
    capital: float
    entry: EntryRule
    exit: ExitRule
    risk: RiskRule
    template: str = "dip_buy_take_profit_stop_loss"
    version: str = "v1"

    def validate(self) -> None:
        if self.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"Unsupported symbol: {self.symbol}")
        if self.timeframe not in SUPPORTED_TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe: {self.timeframe}")
        if self.capital <= 0:
            raise ValueError("capital must be positive")
        if self.entry.type != "price_drop":
            raise ValueError(f"Unsupported entry rule: {self.entry.type}")
        for name, value in (
            ("drop_percent", self.entry.drop_percent),
            ("take_profit_percent", self.exit.take_profit_percent),
            ("stop_loss_percent", self.exit.stop_loss_percent),
            ("max_drawdown_percent", self.risk.max_drawdown_percent),
            ("position_size_percent", self.risk.position_size_percent),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.risk.position_size_percent > 100:
            raise ValueError("position_size_percent cannot exceed 100")

    def to_dict(self) -> Dict[str, object]:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "capital": self.capital,
            "entry": self.entry.to_dict(),
            "exit": self.exit.to_dict(),
            "risk": self.risk.to_dict(),
            "template": self.template,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Strategy":
        entry_data = data["entry"]
        exit_data = data["exit"]
        risk_data = data["risk"]
        strategy = cls(
            symbol=str(data["symbol"]),
            timeframe=str(data["timeframe"]),
            capital=float(data["capital"]),
            entry=EntryRule(
                type=str(entry_data.get("type", "price_drop")),
                drop_percent=float(entry_data["dropPercent"]),
            ),
            exit=ExitRule(
                take_profit_percent=float(exit_data["takeProfitPercent"]),
                stop_loss_percent=float(exit_data["stopLossPercent"]),
            ),
            risk=RiskRule(
                max_drawdown_percent=float(risk_data["maxDrawdownPercent"]),
                position_size_percent=float(risk_data["positionSizePercent"]),
                risk_level=str(risk_data.get("riskLevel", "medium")),
            ),
            template=str(data.get("template", "dip_buy_take_profit_stop_loss")),
            version=str(data.get("version", "v1")),
        )
        strategy.validate()
        return strategy


def dataclass_to_dict(value):
    return asdict(value)
