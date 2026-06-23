# Frontend Docs

Owner: Frontend Lead

This folder is for UI structure, interaction design, and frontend implementation notes.

## Existing Asset

The existing ProfitPrince single-page terminal UI is valuable as the visual demo layer. It should be cleaned up and connected to real API state instead of being treated as the final product.

## Implemented Console

The MVP frontend now lives in `frontend/` and uses plain HTML, CSS, and browser ES modules. It has no build step.

Primary files:

- `frontend/index.html`
- `frontend/styles/main.css`
- `frontend/src/app.js`
- `frontend/src/api.js`
- `frontend/src/charts.js`
- `frontend/src/demo.js`
- `frontend/src/ui-state.js`

The console calls `POST /api/demo/run` and renders the full backend response:

- Generated strategy JSON.
- Backtest metrics.
- Equity curve.
- AI risk explanation.
- Simulated execution logs.
- Proof hashes.

Run locally:

```bash
cd frontend
python3 -m http.server 5173
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
