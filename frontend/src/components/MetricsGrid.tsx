import { formatPercent } from "../lib/format";
import type { BacktestResult } from "../types";

interface Props {
  backtest: BacktestResult | null;
}

export function MetricsGrid({ backtest }: Props) {
  return (
    <div className="metric-grid">
      <article className="metric-tile accent-green">
        <span>Total Return</span>
        <strong>{backtest ? formatPercent(backtest.totalReturnPercent) : "--"}</strong>
      </article>
      <article className="metric-tile accent-amber">
        <span>Buy & Hold</span>
        <strong>{backtest ? formatPercent(backtest.buyHoldReturnPercent) : "--"}</strong>
      </article>
      <article className="metric-tile accent-cyan">
        <span>Win Rate</span>
        <strong>{backtest ? formatPercent(backtest.winRatePercent) : "--"}</strong>
      </article>
      <article className="metric-tile accent-red">
        <span>Max Drawdown</span>
        <strong>{backtest ? formatPercent(backtest.maxDrawdownPercent) : "--"}</strong>
      </article>
      <article className="metric-tile accent-violet">
        <span>Trades</span>
        <strong>{backtest ? String(backtest.tradeCount) : "--"}</strong>
      </article>
    </div>
  );
}
