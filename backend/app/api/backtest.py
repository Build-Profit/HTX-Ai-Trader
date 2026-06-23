from fastapi import APIRouter, HTTPException

from app.models.market import Kline
from app.models.strategy import Strategy
from app.services.backtest_engine import run_backtest
from app.services.htx_market import get_klines


router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run")
def run(payload: dict):
    try:
        strategy = Strategy.from_dict(payload["strategy"])
        if payload.get("klines"):
            klines = [Kline.from_dict(item) for item in payload["klines"]]
            data_source = str(payload.get("dataSource", "request_payload"))
        else:
            market = get_klines(strategy.symbol, strategy.timeframe, int(payload.get("limit", 120)))
            klines = market["klines"]
            data_source = str(market["source"])
        result = run_backtest(strategy, klines, data_source=data_source, fee_rate=float(payload.get("feeRate", 0.001)))
        return result.to_dict()
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
