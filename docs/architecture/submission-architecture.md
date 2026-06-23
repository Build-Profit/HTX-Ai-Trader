# Submission Architecture

## System Overview

ProfitPrince is organized as a small vertical-slice application:

```text
Frontend Console
-> FastAPI Routes
-> Service Modules
-> Domain Models
-> Run Artifacts
```

The current MVP optimizes for reproducibility and demo stability. Core behavior is deterministic and testable without live network access.

## Components

### Frontend Console

Location: `frontend/`

Responsibilities:

- Capture strategy prompt.
- Call backend demo API.
- Render strategy JSON.
- Render backtest metrics and equity curve.
- Render risk explanation.
- Render simulated orders.
- Render proof hashes.
- Show sample fallback data on first load.

The frontend uses plain HTML, CSS, and browser ES modules. It does not require a build step.

### FastAPI Backend

Location: `backend/app/main.py` and `backend/app/api/`

Routes:

- `GET /api/health`
- `POST /api/strategy/parse`
- `GET /api/market/klines`
- `POST /api/backtest/run`
- `POST /api/risk/explain`
- `POST /api/trade/simulate`
- `POST /api/proof/hash`
- `POST /api/demo/run`

The HTTP layer is intentionally thin. Route modules validate basic payload shape and delegate behavior to services.

### Strategy Parser

Location: `backend/app/services/strategy_parser.py`

Responsibilities:

- Parse natural language into a shared strategy schema.
- Extract key trading parameters.
- Apply safe defaults.
- Validate strategy fields.

MVP uses deterministic parsing for stable demos. Optional LLM parsing can be added as a wrapper around the same schema.

### Market Adapter

Location: `backend/app/services/htx_market.py`

Responsibilities:

- Request HTX-compatible K-line endpoints.
- Normalize market data into `Kline`.
- Fall back to local sample data if live data is unavailable.
- Label data source.

### Backtest Engine

Location: `backend/app/services/backtest_engine.py`

Responsibilities:

- Execute the dip-buy strategy template.
- Apply fee model and position sizing.
- Resolve take-profit and stop-loss.
- Produce equity curve and trade list.
- Compare with buy-and-hold.

### Risk Explainer

Location: `backend/app/services/risk_explainer.py`

Responsibilities:

- Score strategy risk from backtest metrics.
- Explain drawdown, trade count, and benchmark underperformance.
- Recommend simulation, parameter change, or avoiding live execution.

### Simulator

Location: `backend/app/services/simulator.py`

Responsibilities:

- Generate mock order lifecycle.
- Simulate fill and exit events.
- Keep execution clearly separate from real trading.

### Proof Hasher

Location: `backend/app/services/proof_hasher.py`

Responsibilities:

- Canonicalize JSON.
- Hash strategy, backtest, and execution logs.
- Produce a combined proof record.

## Data Flow

```text
User prompt
-> parse_strategy_text
-> Strategy
-> get_klines
-> run_backtest
-> explain_risk
-> simulate_trade
-> generate_proof
-> frontend dashboard
```

## Demo Stability

The MVP has two fallback layers:

- Backend market fallback: live HTX data falls back to local samples.
- Frontend preview fallback: page load shows sample result before API refresh.

This keeps the demo usable even when external network access is unreliable.

## Security and Safety Boundary

- No private keys.
- No exchange API keys.
- No custody.
- No real-money order placement.
- No guaranteed-return claims.

## Current Limitations

- Route payloads are loose dictionaries rather than strict request/response models.
- API route tests are basic.
- Proof is local hash proof, not on-chain anchoring.
- Strategy parser is deterministic, not full LLM parsing.
- Backtesting uses a simple strategy template and limited sample data.
