import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from app.models.market import Kline


APP_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SAMPLE_DATA_DIR = APP_DATA_DIR / "sample_klines"
CACHE_DATA_DIR = APP_DATA_DIR / "cache"
PERIOD_MAP = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "60min",
    "4h": "4hour",
    "1d": "1day",
    "1w": "1week",
    "1mon": "1mon",
    "1y": "1year",
}
FINEST_TIMEFRAME = "1m"
MAX_HTX_CANDLES = 2000


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
    params = urllib.parse.urlencode({"symbol": htx_symbol, "period": period, "size": min(limit, MAX_HTX_CANDLES)})
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


def _timeframe_to_minutes(tf: str) -> int:
    return {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240, "1d": 1440, "1w": 10080, "1mon": 43200, "1y": 525600}.get(tf, 60)


def _timeframe_gt_5m(tf: str) -> bool:
    return _timeframe_to_minutes(tf) > 5


def _pick_intermediate_timeframe(coarse_tf: str) -> Optional[str]:
    coarse_min = _timeframe_to_minutes(coarse_tf)
    candidates = [("1d", 1440), ("4h", 240), ("1h", 60), ("5m", 5)]
    for tf, minutes in candidates:
        if minutes < coarse_min and minutes <= MAX_HTX_CANDLES:
            return tf
    return None


def fetch_fine_for_coarse_candle(
    symbol: str,
    candle_timestamp: str,
    coarse_timeframe: str,
) -> List[Kline]:
    """获取某根粗K线内部完整的1m粒度数据。

    当粗K线周期 <= 2000 分钟时直接获取1m数据；
    超过2000分钟时递归拆解：先获取中间时间框架，
    再逐段获取1m数据。
    """
    period_minutes = _timeframe_to_minutes(coarse_timeframe)
    if period_minutes <= 0:
        return []
    ts = int(candle_timestamp)
    period_seconds = period_minutes * 60

    if period_minutes <= MAX_HTX_CANDLES:
        return _fetch_fine_1m_range(symbol, ts, ts + period_seconds, period_minutes)
    else:
        return _fetch_fine_recursive(symbol, ts, coarse_timeframe)


def _fetch_fine_1m_range(
    symbol: str,
    start_ts: int,
    end_ts: int,
    fetch_count: int,
) -> List[Kline]:
    """获取指定时间范围内的1m K线数据。"""
    try:
        raw, _ = _fetch_htx_klines(symbol, FINEST_TIMEFRAME, min(fetch_count, MAX_HTX_CANDLES))
        return [k for k in raw if start_ts <= int(k.timestamp) < end_ts]
    except Exception:
        return []


def _fetch_fine_recursive(
    symbol: str,
    start_ts: int,
    coarse_timeframe: str,
) -> List[Kline]:
    """对大周期K线（>2000分钟）递归获取完整的1m数据。

    先获取中间时间框架的K线，然后为每根中间K线获取1m数据。
    """
    mid_tf = _pick_intermediate_timeframe(coarse_timeframe)
    if mid_tf is None:
        return []
    mid_minutes = _timeframe_to_minutes(mid_tf)
    coarse_minutes = _timeframe_to_minutes(coarse_timeframe)
    mid_count = coarse_minutes // mid_minutes + 1

    try:
        mid_klines, _ = _fetch_htx_klines(symbol, mid_tf, mid_count)
    except Exception:
        return []
    if not mid_klines:
        return []

    end_ts = start_ts + coarse_minutes * 60
    relevant = sorted(
        [k for k in mid_klines if start_ts <= int(k.timestamp) < end_ts],
        key=lambda k: int(k.timestamp),
    )

    result: List[Kline] = []
    for mid_k in relevant:
        mid_ts = int(mid_k.timestamp)
        mid_end = mid_ts + mid_minutes * 60
        sub = _fetch_fine_1m_range(symbol, mid_ts, mid_end, mid_minutes)
        result.extend(sub)
    return result


def make_fine_fetch_callback(symbol: str) -> Callable[[str, str], List[Kline]]:
    """创建用于回测引擎按需获取子K线的回调函数。

    回调签名: (candle_timestamp: str, coarse_timeframe: str) -> List[Kline]
    """
    def _callback(candle_timestamp: str, coarse_timeframe: str) -> List[Kline]:
        if not _timeframe_gt_5m(coarse_timeframe):
            return []
        return fetch_fine_for_coarse_candle(symbol, candle_timestamp, coarse_timeframe)
    return _callback


def _prefetch_fine_map(
    coarse_klines: List[Kline],
    symbol: str,
    timeframe: str,
) -> Dict[str, List[Kline]]:
    """预取尽可能多的1m数据作为缓存，以减少回测过程中的按需请求。

    使用 API 允许的最大 2000 根 1m K线覆盖最近的区间，
    并按粗K线时间戳分组。
    """
    if not _timeframe_gt_5m(timeframe) or not coarse_klines:
        return {}
    try:
        fine_klines, _ = _fetch_htx_klines(symbol, FINEST_TIMEFRAME, MAX_HTX_CANDLES)
    except Exception:
        return {}
    if not fine_klines:
        return {}

    period_seconds = _timeframe_to_minutes(timeframe) * 60
    sorted_fine = sorted(fine_klines, key=lambda k: int(k.timestamp))
    result: Dict[str, List[Kline]] = {}
    for ck in coarse_klines:
        start_ts = int(ck.timestamp)
        end_ts = start_ts + period_seconds
        bucket = [fk for fk in sorted_fine if start_ts <= int(fk.timestamp) < end_ts]
        if bucket:
            result[ck.timestamp] = bucket
    return result


def get_klines_with_fine(
    symbol: str,
    timeframe: str,
    limit: int = 120,
) -> Dict[str, object]:
    market = get_klines(symbol, timeframe, limit)
    data_source = str(market["source"])
    coarse_klines: List[Kline] = market["klines"]

    fine_map: Dict[str, List[Kline]] = {}
    if data_source == "htx_live":
        fine_map = _prefetch_fine_map(coarse_klines, symbol, timeframe)

    return {
        **market,
        "fineKlines": fine_map,
    }


def _coerce_fetch_result(fetch_result) -> Tuple[List[Kline], str]:
    if isinstance(fetch_result, tuple):
        return fetch_result
    return fetch_result, "unknown"
