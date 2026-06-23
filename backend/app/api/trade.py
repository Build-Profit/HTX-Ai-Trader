from fastapi import APIRouter, HTTPException

from app.models.market import Kline
from app.models.strategy import Strategy
from app.services.htx_market import get_klines
from app.services.simulator import simulate_trade


router = APIRouter(prefix="/api/trade", tags=["trade"])


@router.post("/simulate")
def simulate(payload: dict):
    try:
        strategy = Strategy.from_dict(payload["strategy"])
        if payload.get("klines"):
            klines = [Kline.from_dict(item) for item in payload["klines"]]
        else:
            klines = get_klines(strategy.symbol, strategy.timeframe, int(payload.get("limit", 30)))["klines"]
        return {"executionLogs": [item.to_dict() for item in simulate_trade(strategy, klines)]}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
