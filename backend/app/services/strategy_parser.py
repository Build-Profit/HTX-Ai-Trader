import re
from typing import Dict, Optional

from app.models.strategy import EntryRule, ExitRule, RiskRule, Strategy


RISK_LEVELS = {
    "low": ("低风险", "稳健", "保守", "low"),
    "medium": ("中风险", "均衡", "medium"),
    "high": ("高风险", "激进", "high"),
}


def parse_strategy_text(text: str, default_symbol: str = "BTC/USDT") -> Strategy:
    normalized = _normalize(text)
    symbol = _extract_symbol(normalized) or default_symbol
    timeframe = _extract_timeframe(normalized) or "1h"
    capital = _extract_capital(normalized) or 1000.0
    drop_percent = _extract_keyword_percent(normalized, ("跌", "下跌", "回调", "drop")) or 5.0
    take_profit = _extract_keyword_percent(normalized, ("止盈", "涨", "上涨", "take profit", "profit")) or 10.0
    stop_loss = _extract_keyword_percent(normalized, ("止损", "亏损", "最大亏损", "stop loss", "loss")) or 3.0
    max_drawdown = _extract_keyword_percent(normalized, ("最大回撤", "回撤", "drawdown")) or 5.0
    position_size = _extract_keyword_percent(normalized, ("仓位", "position")) or _default_position_size(normalized)
    risk_level = _extract_risk_level(normalized)

    strategy = Strategy(
        symbol=symbol,
        timeframe=timeframe,
        capital=capital,
        entry=EntryRule(type="price_drop", drop_percent=drop_percent),
        exit=ExitRule(take_profit_percent=take_profit, stop_loss_percent=stop_loss),
        risk=RiskRule(
            max_drawdown_percent=max_drawdown,
            position_size_percent=position_size,
            risk_level=risk_level,
        ),
    )
    strategy.validate()
    return strategy


def parse_strategy_payload(payload: Dict[str, object]) -> Dict[str, object]:
    text = str(payload.get("text") or payload.get("input") or "")
    if not text.strip():
        raise ValueError("strategy text is required")
    default_symbol = str(payload.get("symbol") or "BTC/USDT")
    strategy = parse_strategy_text(text, default_symbol=default_symbol)
    return {
        "input": text,
        "strategy": strategy.to_dict(),
        "explanation": _explain_strategy(strategy),
        "riskTags": _risk_tags(strategy),
    }


def _normalize(text: str) -> str:
    return (
        text.strip()
        .replace("％", "%")
        .replace("，", ",")
        .replace("。", ".")
        .replace("：", ":")
        .replace("／", "/")
    )


def _extract_symbol(text: str) -> Optional[str]:
    upper = text.upper()
    if "ETH/USDT" in upper or "ETHUSDT" in upper:
        return "ETH/USDT"
    if "BTC/USDT" in upper or "BTCUSDT" in upper:
        return "BTC/USDT"
    return None


def _extract_timeframe(text: str) -> Optional[str]:
    lowered = text.lower()
    mappings = {
        "1min": "1m",
        "1m": "1m",
        "1分": "1m",
        "5min": "5m",
        "5m": "5m",
        "5分": "5m",
        "15min": "15m",
        "15m": "15m",
        "15分": "15m",
        "30min": "30m",
        "30m": "30m",
        "30分": "30m",
        "1h": "1h",
        "1小时": "1h",
        "4h": "4h",
        "4小时": "4h",
        "1d": "1d",
        "1天": "1d",
        "日线": "1d",
        "1week": "1w",
        "1w": "1w",
        "week": "1w",
        "weekly": "1w",
        "周": "1w",
        "周线": "1w",
        "1mon": "1mon",
        "1month": "1mon",
        "month": "1mon",
        "monthly": "1mon",
        "月": "1mon",
        "月线": "1mon",
        "1year": "1y",
        "1y": "1y",
        "year": "1y",
        "yearly": "1y",
        "年": "1y",
        "年线": "1y",
    }
    for token, timeframe in mappings.items():
        if token in lowered:
            return timeframe
    return None


def _extract_capital(text: str) -> Optional[float]:
    patterns = (
        r"(\d+(?:\.\d+)?)\s*USDT",
        r"资金\s*(\d+(?:\.\d+)?)",
        r"capital\s*(\d+(?:\.\d+)?)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _extract_keyword_percent(text: str, keywords) -> Optional[float]:
    for keyword in keywords:
        escaped = re.escape(keyword)
        patterns = (
            rf"{escaped}[^\d,.;，。]{{0,12}}(\d+(?:\.\d+)?)\s*%",
            rf"(\d+(?:\.\d+)?)\s*%[^\n,.;，。]{{0,12}}{escaped}",
        )
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
    return None


def _extract_risk_level(text: str) -> str:
    lowered = text.lower()
    for level, tokens in RISK_LEVELS.items():
        if any(token in lowered for token in tokens):
            return level
    return "medium"


def _default_position_size(text: str) -> float:
    risk = _extract_risk_level(text)
    if risk == "low":
        return 20.0
    if risk == "high":
        return 50.0
    return 30.0


def _explain_strategy(strategy: Strategy) -> str:
    return (
        f"{strategy.symbol} {strategy.timeframe} strategy: buy after a "
        f"{strategy.entry.drop_percent:.2f}% pullback, take profit at "
        f"{strategy.exit.take_profit_percent:.2f}%, stop loss at "
        f"{strategy.exit.stop_loss_percent:.2f}%, using "
        f"{strategy.risk.position_size_percent:.2f}% position size."
    )


def _risk_tags(strategy: Strategy):
    tags = [strategy.risk.risk_level]
    if strategy.risk.max_drawdown_percent <= 5:
        tags.append("drawdown_controlled")
    if strategy.risk.position_size_percent >= 50:
        tags.append("high_position_size")
    return tags
