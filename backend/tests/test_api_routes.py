from fastapi.testclient import TestClient

from app.main import app
from app.services.htx_market import load_sample_klines


client = TestClient(app)


def _sample_market(symbol="BTC/USDT", timeframe="1h", limit=120):
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "source": "local_sample",
        "metadata": {},
        "klines": load_sample_klines(symbol, timeframe, limit),
    }


def test_health_route_returns_service_status():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "htx-ai-trader"}


def test_strategy_parse_route_returns_strategy_json():
    response = client.post(
        "/api/strategy/parse",
        json={"text": "Use 1000 USDT on BTC/USDT. Buy drop 5%, take profit 10%, stop loss 3%."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["strategy"]["symbol"] == "BTC/USDT"
    assert payload["strategy"]["entry"]["dropPercent"] == 5.0
    assert payload["strategy"]["exit"]["takeProfitPercent"] == 10.0
    assert payload["strategy"]["exit"]["stopLossPercent"] == 3.0


def test_strategy_parse_route_rejects_empty_text():
    response = client.post("/api/strategy/parse", json={"text": ""})

    assert response.status_code == 400
    assert "strategy text is required" in response.json()["detail"]


def test_demo_run_route_returns_full_workflow(monkeypatch):
    monkeypatch.setattr("app.services.demo_runner.get_klines", _sample_market)

    response = client.post(
        "/api/demo/run",
        json={"text": "Use 1000 USDT on BTC/USDT. Buy drop 5%, take profit 10%, stop loss 3%, max drawdown 5%."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["market"]["source"] == "local_sample"
    assert payload["market"]["metadata"] == {}
    assert payload["strategy"]["symbol"] == "BTC/USDT"
    assert payload["backtest"]["tradeCount"] >= 1
    assert payload["risk"]["executionRecommendation"]
    assert payload["executionLogs"]
    assert payload["proof"]["combinedHash"]


def test_backtest_route_runs_with_payload_klines():
    strategy_response = client.post(
        "/api/strategy/parse",
        json={"text": "Use 1000 USDT on BTC/USDT. Buy drop 5%, take profit 10%, stop loss 3%."},
    )
    klines = [item.to_dict() for item in load_sample_klines("BTC/USDT", "1h", 120)]

    response = client.post(
        "/api/backtest/run",
        json={
            "strategy": strategy_response.json()["strategy"],
            "klines": klines,
            "dataSource": "test_payload",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataSource"] == "test_payload"
    assert payload["tradeCount"] >= 1
    assert payload["equityCurve"]


def test_market_route_returns_metadata(monkeypatch):
    metadata = {
        "fetchedAt": "2026-06-23T14:30:00Z",
        "endpoint": "https://api.htx.com/market/history/kline?symbol=btcusdt&period=60min&size=2",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "count": 2,
    }

    def _cached_market(symbol="BTC/USDT", timeframe="1h", limit=120):
        market = _sample_market(symbol, timeframe, limit)
        market["source"] = "htx_cached"
        market["metadata"] = metadata
        return market

    monkeypatch.setattr("app.api.market.get_klines", _cached_market)

    response = client.get("/api/market/klines?symbol=BTC/USDT&timeframe=1h&limit=2")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "htx_cached"
    assert payload["metadata"] == metadata
    assert payload["klines"]
