import json
from types import SimpleNamespace

import pytest

from app.services import ai_strategy_agent


_openai_available = True
try:
    import openai  # noqa: F401
except ImportError:
    _openai_available = False


@pytest.fixture(autouse=True)
def _disable_llm(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "false")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    yield


def test_rule_mapper_pmm_simple_on_market_making_keywords():
    result = ai_strategy_agent.generate_controller(
        "用 1000 USDT 在 BTC/USDT 做市 spread 0.5% 止损3%",
        default_symbol="BTC/USDT",
    )
    assert result["controllerType"] == "market_making"
    assert result["controllerName"] == "pmm_simple"
    assert result["generatedBy"] == "rules"
    cfg = result["config"]
    assert cfg["trading_pair"] == "BTC-USDT"
    assert cfg["exchange"] == "binance"
    assert cfg["stop_loss"] == 0.03
    assert cfg["leverage"] == 1
    assert cfg["order_amount_usd"] == 1000.0


def test_rule_mapper_grid_strike_on_grid_keywords():
    result = ai_strategy_agent.generate_controller(
        "网格 grid 策略 BTC/USDT 用 500 USDT",
        default_symbol="BTC/USDT",
    )
    assert result["controllerType"] == "generic"
    assert result["controllerName"] == "grid_strike"
    assert result["generatedBy"] == "rules"
    cfg = result["config"]
    assert cfg["trading_pair"] == "BTC-USDT"
    assert cfg["grid_levels"] == 10
    assert cfg["order_amount_usd"] == 500.0


def test_rule_mapper_default_bollinger_with_warnings():
    result = ai_strategy_agent.generate_controller(
        "随便写一段 BTC/USDT 的策略",
        default_symbol="BTC/USDT",
    )
    assert result["controllerType"] == "directional_trading"
    assert result["controllerName"] == "bollinger_v1"
    assert result["generatedBy"] == "rules"
    assert "unsupported_scenario_default_bollinger" in result["warnings"]


@pytest.mark.skipif(not _openai_available, reason="openai package not installed")
def test_llm_channel_used_when_configured(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    canned = {
        "controllerType": "directional_trading",
        "controllerName": "bollinger_v1",
        "config": {
            "exchange": "binance",
            "trading_pair": "BTC-USDT",
            "leverage": 1,
            "stop_loss": 0.03,
            "take_profit": 0.08,
        },
        "warnings": [],
    }

    class _FakeCompletions:
        def create(self, **kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=json.dumps(canned))
                    )
                ]
            )

    class _FakeOpenAI:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.chat = SimpleNamespace(completions=_FakeCompletions())

    monkeypatch.setattr("openai.OpenAI", _FakeOpenAI, raising=False)

    result = ai_strategy_agent.generate_controller(
        "用 1000 USDT 在 BTC/USDT 做布林带趋势，止损3% 止盈8%",
        default_symbol="BTC/USDT",
    )
    assert result["generatedBy"] == "llm"
    assert result["controllerType"] == "directional_trading"
    assert result["controllerName"] == "bollinger_v1"
    assert result["config"]["trading_pair"] == "BTC-USDT"


@pytest.mark.skipif(not _openai_available, reason="openai package not installed")
def test_llm_failure_falls_back_to_rules_with_warning(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    class _FakeCompletions:
        def create(self, **kwargs):
            raise RuntimeError("network down")

    class _FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=_FakeCompletions())

    monkeypatch.setattr("openai.OpenAI", _FakeOpenAI, raising=False)

    result = ai_strategy_agent.generate_controller(
        "做市 spread BTC/USDT 止损 3%",
        default_symbol="BTC/USDT",
    )
    assert result["generatedBy"] == "rules"
    assert any("llm_unavailable" in w for w in result["warnings"])
    assert result["controllerType"] == "market_making"


def test_llm_missing_key_warning(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "")

    result = ai_strategy_agent.generate_controller(
        "BTC/USDT 跌5% 买入 止损3% 止盈8%",
        default_symbol="BTC/USDT",
    )
    assert result["generatedBy"] == "rules"
    assert any("missing_openai_api_key" in w for w in result["warnings"])
