# HTX Integration

## Current MVP Integration

ProfitPrince is HTX-native at the workflow and market-data layer.

Implemented:

- HTX-compatible K-line adapter.
- BTC/USDT and ETH/USDT strategy symbols.
- HTX market data source label.
- Last-successful HTX snapshot fallback for demo stability.
- Bundled local sample fallback when no live or cached data exists.
- Simulated HTX order lifecycle.

The MVP does not place real HTX orders.

## Market Data Adapter

Backend service:

```text
backend/app/services/htx_market.py
```

Behavior:

1. Convert `BTC/USDT` into HTX-compatible symbol format such as `btcusdt`.
2. Convert timeframe into HTX-compatible periods such as `60min`.
3. Request K-line data from HTX/Huobi-compatible endpoints.
4. Normalize response fields into the shared `Kline` model.
5. Persist each successful live response into `backend/app/data/cache/` as the latest valid HTX-compatible snapshot.
6. If the live endpoint is unavailable, fall back to the latest cached snapshot.
7. If no cached snapshot exists, fall back to bundled local sample data in `backend/app/data/sample_klines/`.

Data source labels:

- `htx_live`
- `htx_cached`
- `local_sample`
- `local_sample_preview`

The cache directory is runtime state and is intentionally gitignored. The committed `sample_klines/` files remain stable demo fixtures and are not overwritten by live market pulls.

## Simulated Execution Boundary

The MVP simulates order lifecycle events:

- Order created.
- Order filled.
- Take-profit triggered.
- Stop-loss triggered.
- Manual stop.

No real order is sent to HTX in the MVP. This is a deliberate safety boundary for hackathon demonstration and compliance.

## Future HTX API Extension

P1 can add:

- Read-only account import.
- Imported historical trade analysis.
- Paper-trading account abstraction.
- Optional real HTX order placement only after explicit user authorization.

Suggested progression:

1. Keep current simulated execution as default.
2. Add read-only HTX account import.
3. Add shadow account / paper execution.
4. Add real order placement only behind a separate permission and risk gate.

## HTX Ecosystem Fit

ProfitPrince can support:

- Strategy research for HTX users.
- HTX pair-specific backtesting.
- Risk-aware simulated execution.
- Verifiable strategy record history.
- Future strategy marketplace tied to creator reputation.

## Submission Wording

Use:

- "HTX market-data backed strategy workflow."
- "Simulated HTX execution in MVP."
- "Ready for HTX trading API integration."
- "No custody and no real order placement in MVP."

Avoid:

- "Live auto-trading."
- "Guaranteed HTX profit."
- "Risk-free strategy."
- "Real exchange execution" unless a real execution integration is added.
