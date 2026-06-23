# Trading Engine Docs

Owner: Trading Engine / Strategy Lead

This folder is for strategy schema, backtesting rules, execution simulation, and trading assumptions.

## MVP Strategy Templates

1. Dip Buy + Take Profit + Stop Loss.
2. EMA Crossover.
3. RSI Mean Reversion.

The first template is required for MVP. The second and third are stretch goals if the core loop is stable.

## Backtest Requirements

- Use historical K-line data.
- Include fee assumptions.
- Output total return, win rate, max drawdown, trade count, P/L ratio, equity curve, and trades.
- Compare strategy return against buy-and-hold for the same symbol and period.
- Results must be reproducible from strategy JSON and market data.

## Simulation Requirements

- No real money in MVP.
- Order lifecycle: created, filled, take-profit triggered, stop-loss triggered, manually stopped.
- Every simulated event is appended to an execution log.
