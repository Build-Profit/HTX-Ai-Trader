# HTX-Ai-Trader MVP Implementation Plan

Status: Waiting for owner approval  
Owner for approval: Wang Mia  
Date: 2026-06-18  
Scope: Planning and repository documentation only. No implementation starts until approval.

## 1. Inputs Used

This plan is based on:

- `ProfitPrince_HTX_Genesis_PRD_v1.docx`
- Existing ProfitPrince single-page HTML/CSS/JS terminal prototype.
- Existing project README.
- Lessons from `HKUDS/Vibe-Trading`.
- Lessons from `marketcalls/vectorbt-backtesting-skills`.

## 2. Design Principles

We will follow practical "Linus-style" engineering principles:

1. Good data structures beat clever code.
   - Define `Strategy`, `Kline`, `BacktestResult`, `Trade`, `ExecutionLog`, and `ProofRecord` first.
   - Keep the rest of the system as transformations between these structures.

2. Kill special cases.
   - One strategy schema should serve parser, backtest, simulation, dashboard, and proof.
   - Demo Mode should use the same endpoints as normal mode, only with sample data.

3. Make errors impossible where possible.
   - Validate strategy JSON before backtesting.
   - Reject missing symbol, invalid percentages, negative capital, unsupported timeframe, and unsafe claims.

4. Small interfaces, boring modules.
   - HTTP routes stay thin.
   - Each service has one job.
   - No large "AI does everything" blob.

5. Never fake core metrics.
   - Return, win rate, drawdown, trade count, and equity curve must come from market data and deterministic rules.
   - AI can explain metrics, but cannot invent them.

6. Prefer a working vertical slice over broad incomplete features.
   - First make one complete path run from input to proof.
   - Add more templates only after the first path is stable.

7. Do not over-engineer the hackathon MVP.
   - No real-money execution in MVP.
   - No full multi-agent swarm in MVP.
   - No ZK implementation in MVP.
   - Leave clean extension points for P1/P2.

## 3. Product Target

Build a credible HTX-native AI strategy workflow:

```text
Natural-language strategy idea
-> strategy JSON
-> HTX K-line data or local fallback
-> deterministic backtest
-> AI risk explanation
-> simulated execution ledger
-> proof hash
-> dashboard display
```

The product must not claim guaranteed returns, risk-free profit, or unverifiable fixed win rates.

## 4. Lessons to Absorb

### From Vibe-Trading

- Treat every user request as a trackable research run.
- Store artifacts under a run ID.
- Keep broker / real trading disabled by default.
- Separate market loading, backtesting, reporting, execution, and memory.
- Provide stable local fallback so demos do not depend entirely on live APIs.

### From vectorbt-backtesting-skills

- Backtests must include fees and realistic assumptions.
- Compare strategy performance against buy-and-hold.
- Use templates to make natural-language parsing reliable.
- Report metrics in a format both traders and judges can understand.
- Put walk-forward validation and Monte Carlo stress tests into later phases.

## 5. Repository Structure to Build

After approval, implement this structure:

```text
HTX-Ai-Trader/
├── README.md
├── docs/
│   ├── plans/
│   ├── product/
│   ├── architecture/
│   ├── engineering/
│   ├── frontend/
│   ├── backend/
│   ├── trading-engine/
│   ├── web3/
│   ├── qa-demo/
│   └── pitch/
├── frontend/
│   ├── index.html
│   ├── src/
│   │   ├── app.js
│   │   ├── api.js
│   │   ├── charts.js
│   │   ├── demo.js
│   │   └── ui-state.js
│   └── styles/
│       └── main.css
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── strategy.py
│   │   │   ├── market.py
│   │   │   ├── backtest.py
│   │   │   ├── risk.py
│   │   │   ├── trade.py
│   │   │   ├── proof.py
│   │   │   └── demo.py
│   │   ├── models/
│   │   │   ├── strategy.py
│   │   │   ├── market.py
│   │   │   ├── backtest.py
│   │   │   ├── trade.py
│   │   │   └── proof.py
│   │   ├── services/
│   │   │   ├── strategy_parser.py
│   │   │   ├── htx_market.py
│   │   │   ├── backtest_engine.py
│   │   │   ├── risk_explainer.py
│   │   │   ├── simulator.py
│   │   │   └── proof_hasher.py
│   │   └── data/
│   │       └── sample_klines/
│   └── tests/
│       ├── test_strategy_parser.py
│       ├── test_backtest_engine.py
│       ├── test_simulator.py
│       └── test_proof_hasher.py
├── runs/
│   └── .gitkeep
└── .gitignore
```

## 6. Code Areas and Responsibilities

### 6.1 Frontend

Primary owner: Frontend Lead

What to write:

- Extract the existing static terminal UI into `frontend/`.
- Fix malformed HTML conversion issues from the docx export.
- Replace hardcoded metrics with API state.
- Add Demo Mode button.
- Add strategy JSON viewer.
- Add backtest and benchmark panels.
- Add simulated order ledger.
- Add proof hash panel.

Keep:

- Terminal visual identity.
- Six-zone layout idea.
- K-line and dashboard presentation.

Remove or revise:

- Fixed `90.12%` win-rate claims.
- "Automatic profitable trading" wording.
- Fake on-chain certainty.
- Hardcoded market arrays as final data.

### 6.2 Backend API

Primary owner: Backend / Infra Lead

What to write:

- FastAPI application skeleton.
- Pydantic request and response models.
- API routes for strategy, market, backtest, risk, trade, proof, and demo.
- Unified error responses.
- Local run artifact writer.

Backend rule:

```text
routes call services; services own behavior
```

### 6.3 Strategy Parser

Primary owner: Backend Lead + Strategy Lead

What to write:

- Template-based parser for MVP.
- Rule extraction for:
  - symbol
  - timeframe
  - capital
  - entry drop percent
  - take profit percent
  - stop loss percent
  - max drawdown
  - position size
- Validation and safe defaults.

MVP does not require paid LLM integration. A deterministic parser is acceptable for demo stability. LLM integration can wrap the same schema later.

### 6.4 HTX Market Loader

Primary owner: Backend / Infra Lead

What to write:

- `get_klines(symbol, timeframe, limit)`.
- HTX API adapter.
- Local sample-data fallback.
- Data normalization into one `Kline` model.
- Source label: `htx_live`, `htx_cached`, or `local_sample`.

### 6.5 Backtest Engine

Primary owner: Trading Engine Lead

What to write:

- Dip-buy strategy executor.
- Fee model.
- Position sizing.
- Take-profit and stop-loss handling.
- Equity curve.
- Trade list.
- Buy-and-hold benchmark.
- Metrics:
  - total return
  - win rate
  - max drawdown
  - trade count
  - P/L ratio

Important constraint:

The backtest engine must be deterministic and testable without network access.

### 6.6 Risk Explainer

Primary owner: Strategy / QA Lead + Backend Lead

What to write:

- Rule-based risk summary first.
- Optional LLM-generated language later.
- Output structure:
  - summary
  - suitable market
  - unsuitable market
  - key risks
  - parameter suggestions
  - execution recommendation

AI explanation must be grounded in backtest metrics.

### 6.7 Simulated Trading Engine

Primary owner: Trading Engine Lead

What to write:

- Mock order creation.
- Mock fill.
- Position state.
- Take-profit trigger.
- Stop-loss trigger.
- Manual stop.
- JSONL execution log.

No real funds, no real exchange orders in MVP.

### 6.8 Proof Hasher

Primary owner: Web3 / Proof Lead

What to write:

- Canonical JSON serializer.
- SHA-256 hash for:
  - strategy
  - backtest
  - execution log
- Proof record with version and timestamp.
- UI-ready response.

P1 can add a testnet contract. MVP only needs local proof records.

### 6.9 Run Artifacts

Primary owner: Backend / Infra Lead

What to write:

Every full demo run should produce:

```text
runs/<run_id>/
├── input.txt
├── strategy_v1.json
├── market_meta.json
├── backtest_v1.json
├── risk_report_v1.json
├── simulated_orders.jsonl
└── proof.json
```

This is the audit trail learned from Vibe-Trading.

## 7. Implementation Steps

### Phase 0: Repository Hygiene

1. Keep existing README.
2. Add `.gitignore`.
3. Add frontend and backend folders.
4. Move old UI into `frontend/index.html` and split CSS/JS only if it does not slow the MVP.
5. Add sample K-line data.

Acceptance:

- Repository opens cleanly.
- No secrets committed.
- README and docs remain intact.

### Phase 1: Backend Vertical Slice

1. Create FastAPI app.
2. Add `/api/strategy/parse`.
3. Add `/api/market/klines` with local fallback.
4. Add `/api/backtest/run`.
5. Add `/api/proof/hash`.

Acceptance:

- One strategy can be parsed.
- One local sample can be backtested.
- Proof hashes are deterministic.
- Tests pass for parser, backtest, and hash.

### Phase 2: Frontend Connection

1. Wire strategy input to `/api/strategy/parse`.
2. Render generated JSON.
3. Load K-lines from backend.
4. Render backtest metrics and equity curve.
5. Replace fixed claims with real metrics.

Acceptance:

- User can enter one strategy and see real backend results.
- UI still works in Demo Mode.
- No fixed win-rate claims remain in main flow.

### Phase 3: Risk and Simulation

1. Add `/api/risk/explain`.
2. Add `/api/trade/simulate`.
3. Show risk report in dashboard.
4. Show order lifecycle and execution logs.
5. Link proof record to strategy, backtest, and logs.

Acceptance:

- Full PRD loop runs end to end.
- Execution remains simulated.
- Proof hash changes if strategy/backtest/log changes.

### Phase 4: Demo Hardening

1. Add `/api/demo/run`.
2. Add one-click Demo Mode.
3. Add sample BTC/USDT and ETH/USDT scenarios.
4. Add acceptance tests.
5. Add run instructions.

Acceptance:

- Demo runs in 3-5 minutes.
- Demo works without live HTX API.
- Data source is clearly labeled.
- Judge-facing story is consistent with README.

### Phase 5: P1 Enhancements Only After MVP

1. Strategy V1 vs V2 comparison.
2. EMA crossover and RSI templates.
3. VectorBT integration.
4. QuantStats-style report.
5. Testnet proof contract.
6. Shadow Account from imported HTX trade history.

## 8. Task Assignment Map

| Area | Suggested Owner | First Deliverable |
| --- | --- | --- |
| Product and pitch | Product Lead | Demo story and compliance-safe wording |
| Frontend | Frontend Lead | Functional terminal UI connected to backend |
| Backend API | Backend / Infra Lead | FastAPI skeleton and API routes |
| Trading engine | Trading Engine Lead | Deterministic backtest and simulator |
| Strategy and QA | Strategy / QA Lead | Strategy templates and test cases |
| Web3 proof | Web3 / Proof Lead | Hash proof module and P1 contract plan |

## 9. Risks

| Risk | Mitigation |
| --- | --- |
| Live HTX API fails during demo | Local sample fallback and Demo Mode |
| UI looks good but behavior is fake | Replace hardcoded metrics with backend results |
| Backtest results are questioned | Deterministic engine, visible fee assumptions, sample data |
| AI output becomes unsafe marketing | Use structured risk explainer and compliance wording |
| Scope expands too much | Finish one vertical slice before adding templates |
| Team overwrites each other's work | Use docs ownership, branches, and small commits |

## 10. Approval Gate

No implementation code should be written until this plan is approved.

Pending approval question:

```text
Approve Phase 0 and Phase 1 implementation?
```

If approved, the first coding task will be:

```text
Create backend FastAPI skeleton, shared models, local sample K-line loader, strategy parser, deterministic dip-buy backtest, proof hasher, and tests.
```

## 11. Todo State

`todo_write` is not available in the current tool environment. The active task state is therefore tracked through the assistant task plan and this approval-gated document.

Current state:

- [x] Read PRD and local source materials.
- [x] Study reference projects.
- [x] Create documentation directory structure.
- [x] Write implementation plan.
- [ ] Wait for owner approval before coding.
