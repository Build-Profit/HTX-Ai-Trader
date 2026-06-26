from fastapi import APIRouter, HTTPException

from app.models.market import Kline
from app.models.strategy import Strategy
from app.services.backtest_engine import run_backtest
from app.services.htx_market import get_klines_with_fine, make_fine_fetch_callback


router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run")
def run(payload: dict):
    try:
        strategy = Strategy.from_dict(payload["strategy"])
        if payload.get("klines"):
            klines = [Kline.from_dict(item) for item in payload["klines"]]
            data_source = str(payload.get("dataSource", "request_payload"))
            fine_klines_map = None
            fetch_fine_cb = None
        else:
            market = get_klines_with_fine(strategy.symbol, strategy.timeframe, int(payload.get("limit", 120)))
            klines = market["klines"]
            data_source = str(market["source"])
            fine_klines_map = market.get("fineKlines")
            fetch_fine_cb = make_fine_fetch_callback(strategy.symbol) if data_source == "htx_live" else None
        result = run_backtest(
            strategy, klines,
            data_source=data_source,
            fee_rate=float(payload.get("feeRate", 0.001)),
            fine_klines_map=fine_klines_map,
            fetch_fine_callback=fetch_fine_cb,
        )
        return result.to_dict()
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
