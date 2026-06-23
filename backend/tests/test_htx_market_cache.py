import json

from app.models.market import Kline
from app.services import htx_market


def _kline(timestamp="1", close=100.0):
    return Kline(
        timestamp=timestamp,
        open=close - 1,
        high=close + 2,
        low=close - 2,
        close=close,
        volume=10,
    )


def test_live_klines_are_saved_as_last_successful_snapshot(monkeypatch, tmp_path):
    monkeypatch.setattr(htx_market, "CACHE_DATA_DIR", tmp_path)
    live_klines = [_kline("1", 100), _kline("2", 101)]
    endpoint = "https://api.htx.com/market/history/kline?symbol=btcusdt&period=60min&size=120"
    monkeypatch.setattr(htx_market, "_fetch_htx_klines", lambda symbol, timeframe, limit: (live_klines, endpoint))

    market = htx_market.get_klines("BTC/USDT", "1h", 120)

    assert market["source"] == "htx_live"
    assert market["klines"] == live_klines
    assert market["metadata"]["endpoint"] == endpoint
    assert market["metadata"]["symbol"] == "BTC/USDT"
    assert market["metadata"]["timeframe"] == "1h"
    assert market["metadata"]["count"] == 2
    assert market["metadata"]["fetchedAt"].endswith("Z")

    cached = htx_market.load_cached_klines("BTC/USDT", "1h", 120)
    assert cached == live_klines

    cache_path = tmp_path / "btcusdt_1h.json"
    assert cache_path.exists()
    cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cached_payload["metadata"] == market["metadata"]
    assert len(cached_payload["klines"]) == 2


def test_cached_snapshot_is_used_before_bundled_sample_when_live_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(htx_market, "CACHE_DATA_DIR", tmp_path)
    cached_klines = [_kline("1", 100), _kline("2", 102)]
    htx_market.save_cached_klines("ETH/USDT", "1h", cached_klines)

    def _raise_live_error(symbol, timeframe, limit):
        raise TimeoutError("live endpoint unavailable")

    def _raise_sample_error(symbol, timeframe, limit):
        raise AssertionError("bundled sample should not be used when cache exists")

    monkeypatch.setattr(htx_market, "_fetch_htx_klines", _raise_live_error)
    monkeypatch.setattr(htx_market, "load_sample_klines", _raise_sample_error)

    market = htx_market.get_klines("ETH/USDT", "1h", 120)

    assert market["source"] == "htx_cached"
    assert market["klines"] == cached_klines
    assert market["metadata"]["symbol"] == "ETH/USDT"
    assert market["metadata"]["timeframe"] == "1h"
    assert market["metadata"]["count"] == 2


def test_legacy_cached_array_still_loads(monkeypatch, tmp_path):
    monkeypatch.setattr(htx_market, "CACHE_DATA_DIR", tmp_path)
    legacy_payload = [_kline("1", 100).to_dict(), _kline("2", 101).to_dict()]
    (tmp_path / "btcusdt_1h.json").write_text(json.dumps(legacy_payload), encoding="utf-8")

    snapshot = htx_market.load_cached_snapshot("BTC/USDT", "1h", 120)

    assert snapshot["metadata"] == {}
    assert snapshot["klines"] == [_kline("1", 100), _kline("2", 101)]


def test_corrupt_cached_snapshot_falls_back_to_bundled_sample(monkeypatch, tmp_path):
    monkeypatch.setattr(htx_market, "CACHE_DATA_DIR", tmp_path)
    (tmp_path / "btcusdt_1h.json").write_text("not json", encoding="utf-8")

    def _raise_live_error(symbol, timeframe, limit):
        raise TimeoutError("live endpoint unavailable")

    sample_klines = [_kline("1", 100), _kline("2", 101)]

    monkeypatch.setattr(htx_market, "_fetch_htx_klines", _raise_live_error)
    monkeypatch.setattr(htx_market, "load_sample_klines", lambda symbol, timeframe, limit: sample_klines)

    market = htx_market.get_klines("BTC/USDT", "1h", 120)

    assert market["source"] == "local_sample"
    assert market["klines"] == sample_klines
