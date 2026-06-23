# Backend Docs

Owner: Backend / Infra Lead

This folder is for API contracts, service layout, and backend integration notes.

## Implemented API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/strategy/parse` | Natural language to strategy JSON |
| `GET` | `/api/market/klines` | HTX or fallback K-line data |
| `POST` | `/api/backtest/run` | Deterministic strategy backtest |
| `POST` | `/api/risk/explain` | Risk report and improvement suggestions |
| `POST` | `/api/trade/simulate` | Mock execution lifecycle |
| `POST` | `/api/proof/hash` | Strategy, backtest, and log hashes |
| `POST` | `/api/demo/run` | One-click full demo run |

## Local Run

Install dependencies:

```bash
cd backend
python3 -m pip install -e '.[dev]'
```

Run tests:

```bash
python3 -m pytest
```

Start API:

```bash
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

## Backend Rule

Keep the backend modular. The HTTP layer should be thin; behavior belongs in services.

```text
api route -> request model -> service -> response model
```

Current MVP services own the behavior and route files stay thin. P1 should replace loose `dict` route payloads with explicit request and response schemas once the demo contract stabilizes.
