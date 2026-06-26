from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services import hb_facade, hummingbot_client
from app.services.htx_market import load_sample_klines


@pytest.fixture(autouse=True)
def _hb_enabled(monkeypatch):
    monkeypatch.setenv("HUMMINGBOT_ENABLED", "true")
    hummingbot_client.reset_client()
    yield
    hummingbot_client.reset_client()


def _make_controller():
    return {
        "controllerType": "directional_trading",
        "controllerName": "bollinger_v1",
        "config": {
            "exchange": "binance",
            "trading_pair": "BTC-USDT",
            "leverage": 1,
            "stop_loss": 0.03,
            "take_profit": 0.08,
            "trailing_stop_activation_price_delta": 0.05,
            "order_amount_usd": 1000.0,
            "candles_interval": "1h",
        },
        "generatedBy": "rules",
        "warnings": [],
    }


class _FakeClient:
    def __init__(self, reachable=True, backtest_payload=None, deploy_payload=None):
        self._reachable = reachable
        self._backtest_payload = backtest_payload
        self._deploy_payload = deploy_payload

    def is_reachable(self):
        return self._reachable

    def run_backtest(self, controller_config, **extra):
        if self._backtest_payload is None:
            raise hummingbot_client.HummingbotError("no mock")
        return self._backtest_payload

    def deploy_bot(self, payload):
        if self._deploy_payload is None:
            raise hummingbot_client.HummingbotError("no mock")
        return self._deploy_payload

    def get_candles(self, symbol, interval, max_records=120):
        return {"candles": []}


def test_run_backtest_uses_hummingbot_when_reachable(monkeypatch):
    fake = _FakeClient(
        reachable=True,
        backtest_payload={
            "final_equity": 1100,
            "initial_capital": 1000,
            "total_return_percent": 10.0,
            "win_rate_percent": 60.0,
            "max_drawdown_percent": 5.0,
            "trades": [],
            "equity_curve": [{"timestamp": "1", "equity": 1100}],
        },
    )
    monkeypatch.setattr(hb_facade, "_client", lambda: fake)

    result = hb_facade.run_backtest(_make_controller(), klines=load_sample_klines("BTC/USDT", "1h", 120))
    assert result["engine"] == "hummingbot"
    assert result["dataSource"] == "hummingbot"
    assert result["finalEquity"] == 1100


def test_run_backtest_falls_back_to_local_when_unreachable(monkeypatch):
    fake = _FakeClient(reachable=False)
    monkeypatch.setattr(hb_facade, "_client", lambda: fake)
    monkeypatch.setattr(hb_facade, "get_klines_with_fine",
                       lambda symbol, timeframe, limit: {
                           "source": "local_sample",
                           "metadata": {},
                           "klines": load_sample_klines(symbol, timeframe, limit),
                           "fineKlines": None,
                       })

    result = hb_facade.run_backtest(_make_controller(), limit=120)
    assert result["engine"] == "local"
    # Existing BacktestResult dict shape preserved.
    for key in ("symbol", "timeframe", "dataSource", "initialCapital", "finalEquity",
                "totalReturnPercent", "winRatePercent", "maxDrawdownPercent", "tradeCount",
                "trades", "equityCurve", "feeRate"):
        assert key in result


def test_get_klines_falls_back_to_local(monkeypatch):
    fake = _FakeClient(reachable=False)
    monkeypatch.setattr(hb_facade, "_client", lambda: fake)
    monkeypatch.setattr(hb_facade, "local_get_klines",
                       lambda symbol, timeframe, limit: {
                           "source": "local_sample",
                           "metadata": {},
                           "klines": load_sample_klines(symbol, timeframe, limit),
                       })

    result = hb_facade.get_klines("BTC/USDT", "1h", 30)
    assert result["engine"] == "local"
    assert result["source"] == "local_sample"
    assert result["klines"]


def test_deploy_unreachable_raises_503(monkeypatch):
    fake = _FakeClient(reachable=False)
    monkeypatch.setattr(hb_facade, "_client", lambda: fake)

    with pytest.raises(HTTPException) as exc:
        hb_facade.deploy_paper_trade_bot(_make_controller(), "test-bot")
    assert exc.value.status_code == 503
    assert "Hummingbot API unreachable" in exc.value.detail


def test_health_returns_false_when_client_unreachable(monkeypatch):
    fake = _FakeClient(reachable=False)
    monkeypatch.setattr(hb_facade, "_client", lambda: fake)

    result = hb_facade.health()
    assert result["reachable"] is False
    assert result["engine"] == "local"


def test_health_returns_true_when_reachable(monkeypatch):
    fake = _FakeClient(reachable=True)
    monkeypatch.setattr(hb_facade, "_client", lambda: fake)

    result = hb_facade.health()
    assert result["reachable"] is True
    assert result["engine"] == "hummingbot"
