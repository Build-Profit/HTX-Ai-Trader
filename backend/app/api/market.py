from fastapi import APIRouter, Query

from app.services.htx_market import get_klines, klines_to_dict


router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/klines")
def klines(symbol: str = Query("BTC/USDT"), timeframe: str = Query("1h"), limit: int = Query(120)):
    market = get_klines(symbol, timeframe, limit)
    return {
        "symbol": market["symbol"],
        "timeframe": market["timeframe"],
        "source": market["source"],
        "klines": klines_to_dict(market["klines"]),
    }
