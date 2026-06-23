import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List

from app.models.market import Kline


APP_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SAMPLE_DATA_DIR = APP_DATA_DIR / "sample_klines"
CACHE_DATA_DIR = APP_DATA_DIR / "cache"
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
            save_cached_klines(symbol, timeframe, klines)
            return {"symbol": symbol, "timeframe": timeframe, "source": "htx_live", "klines": klines}
    except Exception:
        pass

    cached_klines = load_cached_klines(symbol, timeframe, limit)
    if cached_klines:
        return {"symbol": symbol, "timeframe": timeframe, "source": "htx_cached", "klines": cached_klines}

    klines = load_sample_klines(symbol, timeframe, limit)
    return {"symbol": symbol, "timeframe": timeframe, "source": "local_sample", "klines": klines}


def load_sample_klines(symbol: str, timeframe: str = "1h", limit: int = 120) -> List[Kline]:
    path = SAMPLE_DATA_DIR / _snapshot_filename(symbol, timeframe)
    if not path.exists():
        path = SAMPLE_DATA_DIR / "btcusdt_1h.json"
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return [Kline.from_dict(item) for item in raw[-limit:]]


def load_cached_klines(symbol: str, timeframe: str = "1h", limit: int = 120) -> List[Kline]:
    path = CACHE_DATA_DIR / _snapshot_filename(symbol, timeframe)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        return [Kline.from_dict(item) for item in raw[-limit:]]
    except (OSError, ValueError, KeyError, TypeError):
        return []


def save_cached_klines(symbol: str, timeframe: str, klines: List[Kline]) -> None:
    try:
        CACHE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        path = CACHE_DATA_DIR / _snapshot_filename(symbol, timeframe)
        temp_path = path.with_suffix(".tmp")
        payload = [kline.to_dict() for kline in klines]
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        temp_path.replace(path)
    except OSError:
        pass


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


def _snapshot_filename(symbol: str, timeframe: str) -> str:
    safe_symbol = symbol.replace("/", "").lower()
    safe_timeframe = timeframe.replace("/", "_").lower()
    return f"{safe_symbol}_{safe_timeframe}.json"
