# ProfitPrince MVP PRD

## Product Summary

ProfitPrince is an HTX-native AI strategy workflow for crypto traders. It converts natural-language strategy ideas into structured rules, validates them with market-data backtests, explains risk, simulates execution, and produces tamper-evident proof hashes for strategy records.

The MVP is intentionally scoped to a research and simulation workflow. It does not custody funds, does not place real exchange orders, and does not promise returns.

## Target Users

### Retail Strategy Builder

User profile:

- Has trading ideas but cannot code a strategy.
- Wants to understand return, drawdown, and failure cases before risking capital.
- Needs a clear workflow instead of a black-box signal.

Core need:

- Turn a plain-language idea into a testable strategy and risk report.

### Hackathon Judge

User profile:

- Evaluates whether the project has a credible AI x Web3 x HTX integration.
- Needs to understand the product in a 3-5 minute demo.

Core need:

- See one complete, reproducible workflow with clear technical boundaries.

### Future Strategy Creator

User profile:

- Publishes parameterized strategies for a community.
- Needs version history, performance evidence, and reputation.

Core need:

- Produce verifiable strategy records that can later support a marketplace.

## Problem

Many crypto traders can describe strategy ideas in natural language, but they cannot easily:

- Convert ideas into structured strategy rules.
- Backtest those rules against historical market data.
- Compare strategy results with buy-and-hold.
- Understand drawdown and position-size risk.
- Simulate order lifecycle before using real funds.
- Prove that a strategy version or backtest result was not modified after the fact.

General chat tools can explain concepts, but they usually do not produce a complete, reproducible trading workflow. Traditional quant tools are powerful, but are difficult for non-technical users.

## MVP Scope

The MVP proves one vertical slice:

```text
Natural-language strategy idea
-> structured strategy JSON
-> HTX market data request with local fallback
-> deterministic backtest
-> AI/rule-based risk explanation
-> simulated execution ledger
-> proof hash
-> dashboard display
```

Supported strategy template:

- Buy after a configured price drop.
- Take profit at a configured percent.
- Stop loss at a configured percent.
- Respect position-size and max-drawdown settings.

Supported market symbols:

- BTC/USDT
- ETH/USDT

Supported demo timeframe:

- 1h sample K-line data, with adapter support for other common intervals.

## Core User Flow

1. User opens the ProfitPrince console.
2. User enters a natural-language strategy idea.
3. System parses the text into strategy JSON.
4. System loads HTX K-line data or local fallback sample data.
5. System runs deterministic backtest.
6. System displays total return, buy-and-hold return, win rate, max drawdown, trade count, and equity curve.
7. System explains key risks and parameter suggestions.
8. System simulates order creation, fill, and exit.
9. System generates strategy, backtest, execution log, and combined proof hashes.

## Functional Requirements

### Strategy Parser

- Extract symbol, timeframe, capital, entry drop percent, take-profit percent, stop-loss percent, max drawdown, position size, and risk level.
- Validate unsupported symbols, unsupported timeframes, negative capital, and unsafe percentages.
- Use deterministic fallback parsing for stable demos.

### Market Data

- Try live HTX-compatible K-line endpoints first.
- Fall back to local sample data if live data is unavailable.
- Label the data source in the UI.

### Backtest

- Use deterministic rules, not fixed metrics.
- Include fee assumptions.
- Produce equity curve and trade list.
- Compare with buy-and-hold.

### Risk Explanation

- Explain drawdown, underperformance, trade count, and position-size concerns.
- Recommend simulation, parameter change, or avoiding live execution based on score.
- Avoid guaranteed-return language.

### Simulated Execution

- Create mock order logs.
- Simulate fills and exits.
- Clearly state that no real exchange order was sent.

### Proof

- Hash canonical JSON for strategy, backtest, and execution logs.
- Display a combined hash as a version record.
- Keep testnet anchoring as P1.

## Non-Goals

- Real-money trading.
- Custody.
- Guaranteed signals.
- Full strategy marketplace.
- ZK proof implementation.
- Production-grade portfolio management.

## Success Criteria

- Demo runs locally without external API dependency.
- Natural-language prompt generates strategy JSON.
- Backtest metrics come from deterministic calculations.
- UI displays data source and proof hashes.
- No guaranteed-profit wording appears in the demo.
- Repository contains clear run instructions and architecture docs.

## Compliance Boundary

ProfitPrince is a strategy research, backtesting, risk explanation, and simulated execution tool. Public wording should use:

- AI-assisted strategy workflow.
- Backtest validation.
- Risk-aware simulation.
- Verifiable strategy record.

Public wording must avoid:

- Guaranteed profit.
- Risk-free trading.
- Always-win claims.
- Fixed unverifiable win rates.
- Real-money execution claims for the MVP.
