# Backend Docs

Owner: Backend / Infra Lead

This folder is for API contracts, service layout, and backend integration notes.

## Proposed API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/strategy/parse` | Natural language to strategy JSON |
| `GET` | `/api/market/klines` | HTX or fallback K-line data |
| `POST` | `/api/backtest/run` | Deterministic strategy backtest |
| `POST` | `/api/risk/explain` | Risk report and improvement suggestions |
| `POST` | `/api/trade/simulate` | Mock execution lifecycle |
| `POST` | `/api/proof/hash` | Strategy, backtest, and log hashes |
| `POST` | `/api/demo/run` | One-click full demo run |

## Backend Rule

Keep the backend modular. The HTTP layer should be thin; behavior belongs in services.

```text
api route -> request model -> service -> response model
```
