# Architecture Docs

Owner: Tech Lead + Backend Lead

This folder is for system boundaries, module design, and technical decisions.

## Target MVP Shape

```text
frontend/
  ProfitPrince terminal UI

backend/
  FastAPI service
  strategy parser
  HTX market loader
  backtest engine
  risk explanation
  simulated trading
  proof hasher

runs/
  reproducible per-run artifacts
```

## Design Rule

AI should not invent performance numbers. Performance comes from deterministic data and deterministic backtest rules. AI explains, summarizes, and suggests changes.

## Main Interfaces

| Module | Input | Output |
| --- | --- | --- |
| Strategy Parser | Natural language, symbol, risk preference | Strategy JSON |
| Market Loader | Symbol, timeframe, limit | K-line data and data source |
| Backtest Engine | Strategy JSON, K-lines, fee config | Metrics, trades, equity curve |
| Risk Agent | Strategy JSON, backtest result | Risk score and explanation |
| Simulator | Strategy JSON, latest market state | Orders, positions, logs |
| Proof Hasher | Strategy, backtest, logs | Deterministic hashes |
