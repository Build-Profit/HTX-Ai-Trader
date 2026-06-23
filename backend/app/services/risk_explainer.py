from typing import Dict, List

from app.models.backtest import BacktestResult
from app.models.strategy import Strategy


def explain_risk(strategy: Strategy, backtest: BacktestResult) -> Dict[str, object]:
    warnings: List[str] = []
    suggestions: List[str] = []

    if backtest.max_drawdown_percent > strategy.risk.max_drawdown_percent:
        warnings.append("Backtest drawdown exceeded the user-defined threshold.")
        suggestions.append("Reduce position size or tighten entry conditions before simulation.")
    if backtest.trade_count == 0:
        warnings.append("The strategy did not trigger any completed trades in the selected sample.")
        suggestions.append("Use a smaller drop trigger or test a longer historical window.")
    if strategy.risk.position_size_percent >= 50:
        warnings.append("Position size is high for a single-rule strategy.")
        suggestions.append("Lower position size to reduce single-trade exposure.")
    if backtest.total_return_percent < backtest.buy_hold_return_percent:
        warnings.append("The strategy underperformed buy-and-hold over this sample.")
        suggestions.append("Compare with V2 parameters before simulated execution.")

    if not warnings:
        warnings.append("No hard risk breach was detected in this backtest sample.")
    if not suggestions:
        suggestions.append("Run the strategy against additional time windows before real trading.")

    score = _risk_score(strategy, backtest)
    recommendation = "simulate_only"
    if score <= 35 and backtest.trade_count > 0:
        recommendation = "suitable_for_demo_simulation"
    elif score >= 70:
        recommendation = "do_not_execute_live"

    return {
        "riskScore": score,
        "riskLevel": _score_level(score),
        "summary": (
            f"Strategy return {backtest.total_return_percent:.2f}% vs buy-and-hold "
            f"{backtest.buy_hold_return_percent:.2f}%, max drawdown "
            f"{backtest.max_drawdown_percent:.2f}%, trades {backtest.trade_count}."
        ),
        "suitableMarket": "Range or pullback markets with enough volatility to trigger entries.",
        "unsuitableMarket": "Fast one-way crashes, thin liquidity, or strong trend markets without pullbacks.",
        "keyRisks": warnings,
        "suggestions": suggestions,
        "executionRecommendation": recommendation,
    }


def _risk_score(strategy: Strategy, backtest: BacktestResult) -> int:
    score = 25
    score += int(max(0, strategy.risk.position_size_percent - 30) * 0.8)
    score += int(max(0, backtest.max_drawdown_percent - strategy.risk.max_drawdown_percent) * 5)
    if backtest.trade_count == 0:
        score += 20
    if backtest.total_return_percent < 0:
        score += 15
    return max(0, min(100, score))


def _score_level(score: int) -> str:
    if score < 35:
        return "low"
    if score < 70:
        return "medium"
    return "high"
