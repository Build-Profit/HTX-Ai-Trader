from fastapi import APIRouter, HTTPException, Query

from app.services import hb_facade


router = APIRouter(prefix="/api/hb", tags=["hummingbot"])


@router.get("/health")
def health():
    return hb_facade.health()


@router.get("/market/candles")
def candles(
    symbol: str = Query("BTC/USDT"),
    interval: str = Query("1h"),
    max_records: int = Query(120),
):
    return hb_facade.get_klines(symbol, interval, max_records)


@router.post("/backtest")
def backtest(payload: dict):
    controller = payload.get("controller") or payload.get("controller_config")
    if not isinstance(controller, dict):
        raise HTTPException(status_code=400, detail="controller config is required")
    limit = int(payload.get("limit", payload.get("tradingDays", 120)))
    fee_rate = float(payload.get("feeRate", 0.001))
    return hb_facade.run_backtest(controller, limit=limit, fee_rate=fee_rate)


@router.post("/bot/deploy")
def deploy_bot(payload: dict):
    controller = payload.get("controller") or payload.get("controller_config")
    if not isinstance(controller, dict):
        raise HTTPException(status_code=400, detail="controller config is required")
    bot_name = str(payload.get("botName") or payload.get("bot_name") or "")
    if not bot_name:
        raise HTTPException(status_code=400, detail="botName is required")
    return hb_facade.deploy_paper_trade_bot(controller, bot_name)


@router.get("/bot/{bot_id}/status")
def bot_status(bot_id: str):
    return hb_facade.get_bot_status(bot_id)


@router.post("/bot/{bot_id}/stop")
def stop_bot(bot_id: str):
    return hb_facade.stop_bot(bot_id)


@router.get("/portfolio")
def portfolio():
    return hb_facade.get_portfolio()
