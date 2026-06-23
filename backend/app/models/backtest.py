from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Trade:
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    quantity: float
    gross_pnl: float
    net_pnl: float
    return_percent: float
    exit_reason: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "entryTime": self.entry_time,
            "exitTime": self.exit_time,
            "entryPrice": self.entry_price,
            "exitPrice": self.exit_price,
            "quantity": self.quantity,
            "grossPnl": self.gross_pnl,
            "netPnl": self.net_pnl,
            "returnPercent": self.return_percent,
            "exitReason": self.exit_reason,
        }


@dataclass(frozen=True)
class EquityPoint:
    timestamp: str
    equity: float

    def to_dict(self) -> Dict[str, object]:
        return {"timestamp": self.timestamp, "equity": self.equity}


@dataclass(frozen=True)
class BacktestResult:
    symbol: str
    timeframe: str
    data_source: str
    initial_capital: float
    final_equity: float
    total_return_percent: float
    buy_hold_return_percent: float
    win_rate_percent: float
    max_drawdown_percent: float
    trade_count: int
    profit_loss_ratio: float
    fee_rate: float
    trades: List[Trade]
    equity_curve: List[EquityPoint]

    def to_dict(self) -> Dict[str, object]:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "dataSource": self.data_source,
            "initialCapital": self.initial_capital,
            "finalEquity": self.final_equity,
            "totalReturnPercent": self.total_return_percent,
            "buyHoldReturnPercent": self.buy_hold_return_percent,
            "winRatePercent": self.win_rate_percent,
            "maxDrawdownPercent": self.max_drawdown_percent,
            "tradeCount": self.trade_count,
            "profitLossRatio": self.profit_loss_ratio,
            "feeRate": self.fee_rate,
            "trades": [trade.to_dict() for trade in self.trades],
            "equityCurve": [point.to_dict() for point in self.equity_curve],
        }
