import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

from app.models.market import Kline


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sample_klines"
PERIOD_MAP = {
    "1m": "1min",
    "5m": "5min",
    "1h": "60min",
    "4h": "4hour",
    "1d": "1day",
}


def get_klines(symbol: str, timeframe: str = "1h", limit: int = 120) -> Dict[str, object]:
    try:
        klines = _fetch_htx_klines(symbol, timeframe, limit)
        if klines:
            return {"symbol": symbol, "timeframe": timeframe, "source": "htx_live", "klines": klines}
    except Exception:
        pass

    klines = load_sample_klines(symbol, timeframe, limit)
    return {"symbol": symbol, "timeframe": timeframe, "source": "local_sample", "klines": klines}


def load_sample_klines(symbol: str, timeframe: str = "1h", limit: int = 120) -> List[Kline]:
    filename = f"{symbol.replace('/', '').lower()}_{timeframe}.json"
    path = DATA_DIR / filename
    if not path.exists():
        path = DATA_DIR / "btcusdt_1h.json"
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return [Kline.from_dict(item) for item in raw[-limit:]]


def _fetch_htx_klines(symbol: str, timeframe: str, limit: int) -> List[Kline]:
    htx_symbol = symbol.replace("/", "").lower()
    period = PERIOD_MAP.get(timeframe, "60min")
    params = urllib.parse.urlencode({"symbol": htx_symbol, "period": period, "size": min(limit, 200)})
    urls = (
        f"https://api.huobi.pro/market/history/kline?{params}",
        f"https://api.htx.com/market/history/kline?{params}",
    )
    last_error = None
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("status") != "ok":
                continue
            data = list(reversed(payload.get("data", [])))
            return [
                Kline(
                    timestamp=str(item["id"]),
                    open=float(item["open"]),
                    high=float(item["high"]),
                    low=float(item["low"]),
                    close=float(item["close"]),
                    volume=float(item.get("vol", item.get("amount", 0))),
                )
                for item in data
            ]
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    return []


def klines_to_dict(klines: List[Kline]) -> List[Dict[str, object]]:
    return [kline.to_dict() for kline in klines]
