# QA and Demo Docs

Owner: Strategy / QA Lead

This folder is for test cases, demo mode, sample data, and acceptance criteria.

## Demo Mode

Demo Mode must run without external dependency risk:

- Load a known sample strategy.
- Load the latest cached HTX-compatible K-line snapshot if the live API fails.
- Load bundled BTC/USDT and ETH/USDT K-line samples if no cached snapshot exists.
- Run backtest.
- Generate risk report.
- Generate simulated orders.
- Generate proof hashes.

## Acceptance Checklist

- [x] Natural-language input produces strategy JSON.
- [x] Backtest changes when parameters change.
- [x] Metrics are not fixed display numbers.
- [x] UI labels data source clearly.
- [x] Simulated orders are linked to strategy version.
- [x] Proof hash changes when strategy or result changes.
- [x] No guaranteed-profit wording appears in the final demo.

## Verified Commands

Backend tests:

```bash
cd backend
python3 -m pytest
```

Frontend TypeScript check:

```bash
cd frontend
npx tsc --noEmit
```

Full local demo:

```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.
