# Frontend Docs

Owner: Frontend Lead

This folder is for UI structure, interaction design, and frontend implementation notes.

## Existing Asset

The existing ProfitPrince single-page terminal UI is valuable as the visual demo layer. It should be cleaned up and connected to real API state instead of being treated as the final product.

## Implemented Console

The MVP frontend lives in `frontend/` and is a React 18 + TypeScript SPA built with Vite.

Primary source files:

- `frontend/src/main.tsx` — React entry point.
- `frontend/src/App.tsx` — Main app component (state management & orchestration).
- `frontend/src/types.ts` — TypeScript interfaces (Strategy, BacktestResult, etc.).
- `frontend/src/api/hb.ts` — Hummingbot API client (via Vite proxy).
- `frontend/src/lib/` — Client-side logic:
  - `strategy.ts` — Strategy parser (mirrors backend).
  - `backtest.ts` — Backtest engine (mirrors backend).
  - `risk.ts` — Risk explainer (mirrors backend).
  - `proof.ts` — SHA-256 proof hasher (mirrors backend).
  - `llm.ts` — Client-side LLM integration.
  - `presets.ts` — Strategy presets.
  - `sample.ts` — Hardcoded sample result for preview.
  - `format.ts` — Formatting helpers.
- `frontend/src/components/` — 10 React components:
  - `TopBar.tsx` — Settings (LLM, HB auth, health indicator).
  - `ControlPanel.tsx` — Strategy input, presets, Run button.
  - `MetricsGrid.tsx` — Backtest metrics.
  - `EquityChart.tsx` — Canvas equity curve.
  - `RiskPanel.tsx` — Risk explanation display.
  - `ProofPanel.tsx` — Hash display.
  - `OrdersTable.tsx` — Execution log table.
  - `HbControllerPanel.tsx` — Hummingbot controller config.
  - `HbBotPanel.tsx` — Deploy/stop bot controls.
  - `HbApiDebugPanel.tsx` — API debug log viewer.
- `frontend/src/hooks/` — React hooks:
  - `useHbHealth.ts` — Hummingbot health polling.
  - `useBotPolling.ts` — Deployed bot status polling.

The console runs strategy parsing, backtesting, risk scoring, and proof hashing client-side by default, and optionally calls the backend API or Hummingbot API.

Run locally:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` with the backend running on `http://127.0.0.1:8000`.

## Required UI Panels

- [x] Strategy input.
- [x] Generated strategy JSON.
- [x] HTX market source.
- [x] Backtest metrics.
- [x] Strategy vs buy-and-hold benchmark.
- [x] Equity curve.
- [x] AI risk explanation.
- [x] Simulated order ledger.
- [x] Strategy version and proof hash.

## Cleanup Requirements

- [x] Remove or relabel hardcoded win-rate claims.
- [x] Replace "automatic profitable trading" wording with "simulated execution" and "risk-aware strategy workflow".
- [x] Replace fake fixed market arrays with API or sample-data-driven rendering.
- [x] Keep Demo Mode available for stable roadshow presentation.
