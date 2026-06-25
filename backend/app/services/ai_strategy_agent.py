"""AI agent: natural language -> Hummingbot controller config.

Rule mapper is always available; LLM channel used when configured & key set.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.services import config
from app.services.strategy_parser import (
    _extract_capital,
    _extract_keyword_percent,
    _extract_risk_level,
    _extract_symbol,
    _normalize,
)


DEFAULT_EXCHANGE = "binance"
DEFAULT_LEVERAGE = 1


@dataclass
class ControllerConfig:
    controller_type: str
    controller_name: str
    config: Dict[str, Any]
    generated_by: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "controllerType": self.controller_type,
            "controllerName": self.controller_name,
            "config": self.config,
            "generatedBy": self.generated_by,
            "warnings": self.warnings,
        }


def generate_controller(text: str, default_symbol: str = "BTC/USDT") -> Dict[str, Any]:
    normalized = _normalize(text)
    controller, warnings = _rule_mapper(normalized, default_symbol)

    if config.llm_enabled() and config.openai_api_key():
        llm_result = _try_llm(normalized, default_symbol)
        if llm_result is not None:
            llm_result["warnings"] = warnings + llm_result.get("warnings", [])
            llm_result["generatedBy"] = "llm"
            return llm_result
        warnings.append("llm_unavailable: call_failed_or_invalid_response")
        controller.generated_by = "rules"
    elif config.llm_enabled() and not config.openai_api_key():
        warnings.append("llm_unavailable: missing_openai_api_key")

    return controller.to_dict()


def _rule_mapper(normalized: str, default_symbol: str) -> (ControllerConfig, List[str]):
    lowered = normalized.lower()
    symbol = _extract_symbol(normalized) or default_symbol
    capital = _extract_capital(normalized) or 1000.0
    risk_level = _extract_risk_level(normalized)
    warnings: List[str] = []

    take_profit_pct = _extract_keyword_percent(normalized, ("止盈", "涨", "上涨", "take profit", "profit")) or 8.0
    stop_loss_pct = _extract_keyword_percent(normalized, ("止损", "亏损", "最大亏损", "stop loss", "loss")) or 3.0
    drop_pct = _extract_keyword_percent(normalized, ("跌", "下跌", "回调", "drop")) or 5.0

    trading_pair = symbol.replace("/", "-")
    take_profit_dec = take_profit_pct / 100
    stop_loss_dec = stop_loss_pct / 100
    drop_dec = drop_pct / 100

    if any(k in lowered for k in ("做市", "spread", "market making", "pmm")):
        buy_spread = _extract_keyword_percent(normalized, ("买价差", "buy spread", "bid spread")) or 0.5
        sell_spread = _extract_keyword_percent(normalized, ("卖价差", "sell spread", "ask spread")) or 0.5
        cfg = ControllerConfig(
            controller_type="market_making",
            controller_name="pmm_simple",
            config={
                "exchange": DEFAULT_EXCHANGE,
                "trading_pair": trading_pair,
                "buy_spread": buy_spread / 100,
                "sell_spread": sell_spread / 100,
                "order_amount_usd": capital,
                "leverage": DEFAULT_LEVERAGE,
                "stop_loss": stop_loss_dec,
                "take_profit": take_profit_dec,
                "time_limit": 60 * 60 * 24,
                "cooldown_time": 60 * 10,
            },
            generated_by="rules",
            warnings=warnings,
        )
        return cfg, warnings

    if any(k in lowered for k in ("网格", "grid")):
        min_price_pct = _extract_keyword_percent(normalized, ("最低", "min price", "下限")) or None
        max_price_pct = _extract_keyword_percent(normalized, ("最高", "max price", "上限")) or None
        grid_levels = 10
        cfg = ControllerConfig(
            controller_type="generic",
            controller_name="grid_strike",
            config={
                "exchange": DEFAULT_EXCHANGE,
                "trading_pair": trading_pair,
                "min_price": float(min_price_pct) if min_price_pct else None,
                "max_price": float(max_price_pct) if max_price_pct else None,
                "grid_levels": grid_levels,
                "order_amount_usd": capital,
            },
            generated_by="rules",
            warnings=warnings,
        )
        return cfg, warnings

    # Default: directional trading with bollinger.
    if not any(k in lowered for k in ("跌", "回调", "drop", "趋势", "bollinger", "bb", "布林")):
        warnings.append("unsupported_scenario_default_bollinger")

    cfg = ControllerConfig(
        controller_type="directional_trading",
        controller_name="bollinger_v1",
        config={
            "exchange": DEFAULT_EXCHANGE,
            "trading_pair": trading_pair,
            "leverage": DEFAULT_LEVERAGE,
            "stop_loss": stop_loss_dec,
            "take_profit": take_profit_dec,
            "time_limit": 60 * 60 * 24,
            "trailing_stop_activation_price_delta": drop_dec,
            "trailing_stop_trailing_delta": 0.01,
            "order_amount_usd": capital,
            "cooldown_time": 60 * 10,
            "candles_exchange": DEFAULT_EXCHANGE,
            "candles_interval": "1h",
            "bb_length": 20,
            "bb_std": 2.0,
            "bb_long_threshold": 0.0,
            "bb_short_threshold": 1.0,
        },
        generated_by="rules",
        warnings=warnings,
    )
    return cfg, warnings


_LLM_SYSTEM_PROMPT = """You map a natural-language trading prompt to a Hummingbot controller config.

Output ONLY strict JSON matching this shape:
{
  "controllerType": "market_making"|"generic"|"directional_trading",
  "controllerName": "pmm_simple"|"grid_strike"|"bollinger_v1",
  "config": { ...controller params... },
  "warnings": ["..."]
}

Supported controllers and their config schemas:
1) market_making.pmm_simple (keywords: 做市/spread/market making/pmm)
   config: exchange(str, default binance), trading_pair(str "BTC-USDT"),
   buy_spread(decimal, 0.005=0.5%), sell_spread(decimal), order_amount_usd(number),
   leverage(int, 1), stop_loss(decimal, 0.03=3%), take_profit(decimal),
   time_limit(int seconds), cooldown_time(int seconds)
2) generic.grid_strike (keywords: 网格/grid)
   config: exchange, trading_pair, min_price(number|null), max_price(number|null),
   grid_levels(int), order_amount_usd
3) directional_trading.bollinger_v1 (default/keywords: 跌/回调/drop/趋势/bollinger/bb)
   config: exchange, trading_pair, leverage, stop_loss(decimal), take_profit(decimal),
   time_limit(int seconds), trailing_stop_activation_price_delta(decimal),
   trailing_stop_trailing_delta(decimal), order_amount_usd, cooldown_time(int seconds),
   candles_exchange, candles_interval(str "1h"), bb_length(int 20), bb_std(number 2.0),
   bb_long_threshold(decimal 0.0), bb_short_threshold(decimal 1.0)

Rules:
- Percent values in user prompt (e.g. 3%) MUST be converted to decimals (0.03).
- trading_pair uses dash format (BTC-USDT), never slash.
- exchange default "binance", leverage default 1.
- If no clear keyword matches, choose directional_trading.bollinger_v1 and add
  warning "unsupported_scenario_default_bollinger".
- Do not output any text outside the JSON object.
"""


def _try_llm(normalized: str, default_symbol: str) -> Optional[Dict[str, Any]]:
    try:
        from openai import OpenAI
    except Exception as exc:
        return None

    try:
        kwargs: Dict[str, Any] = {"api_key": config.openai_api_key()}
        base_url = config.openai_base_url()
        if base_url:
            kwargs["base_url"] = base_url
        client = OpenAI(**kwargs)
        completion = client.chat.completions.create(
            model=config.openai_model(),
            messages=[
                {"role": "system", "content": _LLM_SYSTEM_PROMPT},
                {"role": "user", "content": normalized or default_symbol},
            ],
            temperature=0.2,
            timeout=15,
        )
        content = completion.choices[0].message.content or ""
        parsed = _parse_llm_json(content)
        if not isinstance(parsed, dict):
            return None
        if not all(k in parsed for k in ("controllerType", "controllerName", "config")):
            return None
        parsed.setdefault("warnings", [])
        if not isinstance(parsed["config"], dict):
            return None
        return parsed
    except Exception:
        return None


def _parse_llm_json(content: str) -> Optional[Dict[str, Any]]:
    text = content.strip()
    if text.startswith("```"):
        # Strip ```json or ``` fences.
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        elif text.startswith("```"):
            text = text[3:].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None
    return data if isinstance(data, dict) else None
