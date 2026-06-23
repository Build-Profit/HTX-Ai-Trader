# QA and Demo Docs

Owner: Strategy / QA Lead

This folder is for test cases, demo mode, sample data, and acceptance criteria.

## Demo Mode

Demo Mode must run without external dependency risk:

- Load a known sample strategy.
- Load local BTC/USDT and ETH/USDT K-line samples if HTX API fails.
- Run backtest.
- Generate risk report.
- Generate simulated orders.
- Generate proof hashes.

## Acceptance Checklist

- Natural-language input produces strategy JSON.
- Backtest changes when parameters change.
- Metrics are not fixed display numbers.
- UI labels data source clearly.
- Simulated orders are linked to strategy version.
- Proof hash changes when strategy or result changes.
- No guaranteed-profit wording appears in the final demo.
