from fastapi import APIRouter, HTTPException

from app.models.backtest import BacktestResult, EquityPoint, Trade
from app.models.strategy import Strategy
from app.services.risk_explainer import explain_risk


router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.post("/explain")
def explain(payload: dict):
    try:
        strategy = Strategy.from_dict(payload["strategy"])
        backtest = _backtest_from_dict(payload["backtest"])
        return explain_risk(strategy, backtest)
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _backtest_from_dict(data: dict) -> BacktestResult:
    trades = [
        Trade(
            entry_time=item["entryTime"],
            exit_time=item["exitTime"],
            entry_price=float(item["entryPrice"]),
            exit_price=float(item["exitPrice"]),
            quantity=float(item["quantity"]),
            gross_pnl=float(item["grossPnl"]),
            net_pnl=float(item["netPnl"]),
            return_percent=float(item["returnPercent"]),
            exit_reason=item["exitReason"],
        )
        for item in data.get("trades", [])
    ]
    equity = [
        EquityPoint(timestamp=item["timestamp"], equity=float(item["equity"]))
        for item in data.get("equityCurve", [])
    ]
    return BacktestResult(
        symbol=data["symbol"],
        timeframe=data["timeframe"],
        data_source=data["dataSource"],
        initial_capital=float(data["initialCapital"]),
        final_equity=float(data["finalEquity"]),
        total_return_percent=float(data["totalReturnPercent"]),
        buy_hold_return_percent=float(data["buyHoldReturnPercent"]),
        win_rate_percent=float(data["winRatePercent"]),
        max_drawdown_percent=float(data["maxDrawdownPercent"]),
        trade_count=int(data["tradeCount"]),
        profit_loss_ratio=float(data["profitLossRatio"]),
        fee_rate=float(data["feeRate"]),
        trades=trades,
        equity_curve=equity,
    )
