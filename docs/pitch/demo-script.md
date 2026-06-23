# Demo Script

Target duration: 3-5 minutes.

## Setup

Run backend:

```bash
cd backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run frontend:

```bash
cd frontend
python3 -m http.server 5173
```

Open:

```text
http://127.0.0.1:5173
```

## Script

### 0:00-0:30 Problem

"Many crypto traders can describe an idea, but they cannot easily convert it into a strategy, backtest it, understand drawdown, simulate execution, and prove the result has not changed. ProfitPrince turns this into one workflow for the HTX ecosystem."

### 0:30-1:00 Strategy Prompt

Use the default prompt:

```text
Use 1000 USDT on BTC/USDT. Buy drop 5%, take profit 10%, stop loss 3%, max drawdown 5%.
```

Click `Run Demo`.

Explain:

"The user can write a trading idea in plain English. The system parses it into a structured strategy schema."

### 1:00-1:35 Strategy JSON

Point to:

- Symbol.
- Timeframe.
- Capital.
- Entry rule.
- Take-profit and stop-loss.
- Risk settings.

Explain:

"The schema is shared by parser, backtest, simulator, and proof. This keeps the workflow reproducible."

### 1:35-2:20 Backtest

Point to:

- Total return.
- Buy-and-hold.
- Win rate.
- Max drawdown.
- Trade count.
- Equity curve.
- Data source label.

Explain:

"The metrics are calculated from K-line data. The demo can use HTX live data, but falls back to local samples so the roadshow does not depend on network availability."

### 2:20-3:00 AI Risk

Point to:

- Risk score.
- Risk level.
- Recommendation.
- Key risk.
- Parameter suggestion.

Explain:

"The risk agent does not invent performance numbers. It explains the backtest result, highlights underperformance or drawdown issues, and recommends parameter changes before execution."

### 3:00-3:35 Simulated Orders

Point to:

- Order created.
- Order filled.
- Stop-loss or take-profit trigger.

Explain:

"The MVP uses simulated execution only. It does not custody funds or send real exchange orders."

### 3:35-4:15 Proof Hash

Point to:

- Strategy hash.
- Backtest hash.
- Execution hash.
- Combined hash.

Explain:

"Each strategy version and result can be hashed into a tamper-evident record. The MVP shows local proof; P1 can anchor these records on testnet."

### 4:15-4:45 Roadmap

Explain:

"Next steps are optional LLM parsing, more strategy templates, HTX trading API integration, and testnet proof anchoring. The product can evolve into an HTX-native strategy marketplace with verifiable creator reputation."

## Backup Path

If the backend is unavailable, the frontend shows a local sample result on load. State that this is a preview fallback, then restart the backend and click `Run Demo` again.
