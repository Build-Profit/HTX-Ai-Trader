import type { BacktestResult, RiskReport, Strategy } from "../types";

export function explainRisk(strategy: Strategy, backtest: BacktestResult): RiskReport {
  const warnings: string[] = [];
  const suggestions: string[] = [];

  if (backtest.maxDrawdownPercent > strategy.risk.max_drawdown_percent) {
    warnings.push("Backtest drawdown exceeded the user-defined threshold.");
    suggestions.push("Reduce position size or tighten entry conditions before simulation.");
  }
  if (backtest.tradeCount === 0) {
    warnings.push("The strategy did not trigger any completed trades in the selected sample.");
    suggestions.push("Use a smaller drop trigger or test a longer historical window.");
  }
  if (strategy.risk.position_size_percent >= 50) {
    warnings.push("Position size is high for a single-rule strategy.");
    suggestions.push("Lower position size to reduce single-trade exposure.");
  }
  if (backtest.totalReturnPercent < backtest.buyHoldReturnPercent) {
    warnings.push("The strategy underperformed buy-and-hold over this sample.");
    suggestions.push("Compare with V2 parameters before simulated execution.");
  }

  if (!warnings.length) warnings.push("No hard risk breach was detected in this backtest sample.");
  if (!suggestions.length) suggestions.push("Run the strategy against additional time windows before real trading.");

  const score = riskScore(strategy, backtest);
  let recommendation = "simulate_only";
  if (score <= 35 && backtest.tradeCount > 0) recommendation = "suitable_for_demo_simulation";
  else if (score >= 70) recommendation = "do_not_execute_live";

  return {
    riskScore: score,
    riskLevel: scoreLevel(score),
    summary: `Strategy return ${backtest.totalReturnPercent.toFixed(2)}% vs buy-and-hold ${backtest.buyHoldReturnPercent.toFixed(2)}%, max drawdown ${backtest.maxDrawdownPercent.toFixed(2)}%, trades ${backtest.tradeCount}.`,
    suitableMarket: "Range or pullback markets with enough volatility to trigger entries.",
    unsuitableMarket: "Fast one-way crashes, thin liquidity, or strong trend markets without pullbacks.",
    keyRisks: warnings,
    suggestions,
    executionRecommendation: recommendation,
  };
}

function riskScore(strategy: Strategy, backtest: BacktestResult): number {
  let score = 25;
  score += Math.trunc(Math.max(0, strategy.risk.position_size_percent - 30) * 0.8);
  score += Math.trunc(Math.max(0, backtest.maxDrawdownPercent - strategy.risk.max_drawdown_percent) * 5);
  if (backtest.tradeCount === 0) score += 20;
  if (backtest.totalReturnPercent < 0) score += 15;
  return Math.max(0, Math.min(100, score));
}

function scoreLevel(score: number): string {
  if (score < 35) return "low";
  if (score < 70) return "medium";
  return "high";
}
