import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

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
        klines, endpoint = _coerce_fetch_result(_fetch_htx_klines(symbol, timeframe, limit))
        if klines:
            metadata = save_cached_klines(symbol, timeframe, klines, endpoint)
            return {"symbol": symbol, "timeframe": timeframe, "source": "htx_live", "metadata": metadata, "klines": klines}
    except Exception:
        pass

    cached_snapshot = load_cached_snapshot(symbol, timeframe, limit)
    if cached_snapshot["klines"]:
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "source": "htx_cached",
            "metadata": cached_snapshot["metadata"],
            "klines": cached_snapshot["klines"],
        }

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
    return load_cached_snapshot(symbol, timeframe, limit)["klines"]


def load_cached_snapshot(symbol: str, timeframe: str = "1h", limit: int = 120) -> Dict[str, object]:
    path = CACHE_DATA_DIR / _snapshot_filename(symbol, timeframe)
    if not path.exists():
        return {"metadata": {}, "klines": []}
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if isinstance(raw, list):
            return {"metadata": {}, "klines": [Kline.from_dict(item) for item in raw[-limit:]]}

        raw_klines = raw.get("klines", [])
        metadata = raw.get("metadata", {})
        return {"metadata": metadata, "klines": [Kline.from_dict(item) for item in raw_klines[-limit:]]}
    except (OSError, ValueError, KeyError, TypeError):
        return {"metadata": {}, "klines": []}


def save_cached_klines(symbol: str, timeframe: str, klines: List[Kline], endpoint: str = "unknown") -> Dict[str, object]:
    metadata = _cache_metadata(symbol, timeframe, len(klines), endpoint)
    try:
        CACHE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        path = CACHE_DATA_DIR / _snapshot_filename(symbol, timeframe)
        temp_path = path.with_suffix(".tmp")
        payload = {
            "metadata": metadata,
            "klines": [kline.to_dict() for kline in klines],
        }
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        temp_path.replace(path)
    except OSError:
        pass
    return metadata


def _fetch_htx_klines(symbol: str, timeframe: str, limit: int) -> Tuple[List[Kline], str]:
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
            klines = [
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
            return klines, url
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    return [], "unknown"


def klines_to_dict(klines: List[Kline]) -> List[Dict[str, object]]:
    return [kline.to_dict() for kline in klines]


def _snapshot_filename(symbol: str, timeframe: str) -> str:
    safe_symbol = symbol.replace("/", "").lower()
    safe_timeframe = timeframe.replace("/", "_").lower()
    return f"{safe_symbol}_{safe_timeframe}.json"


def _cache_metadata(symbol: str, timeframe: str, count: int, endpoint: str) -> Dict[str, object]:
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "fetchedAt": fetched_at,
        "endpoint": endpoint,
        "symbol": symbol,
        "timeframe": timeframe,
        "count": count,
    }


def _coerce_fetch_result(fetch_result) -> Tuple[List[Kline], str]:
    if isinstance(fetch_result, tuple):
        return fetch_result
    return fetch_result, "unknown"
