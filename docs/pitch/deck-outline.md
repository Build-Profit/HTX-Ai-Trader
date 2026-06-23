# Pitch Deck Outline

Recommended length: 10-12 slides.

## 1. Title

ProfitPrince: AI Self-Evolving Strategy Agent for the HTX Ecosystem

Include:

- Product name.
- HTX Genesis Hackathon track.
- One-line product statement.
- Demo URL or repository QR code.

## 2. Problem

Crypto traders have ideas, but most cannot:

- Code strategies.
- Backtest ideas reliably.
- Understand drawdown and position sizing.
- Simulate execution before using funds.
- Prove strategy records are unchanged.

## 3. Solution

ProfitPrince turns a natural-language trading idea into:

- Strategy JSON.
- HTX market-data backtest.
- Risk explanation.
- Simulated order lifecycle.
- Proof hashes.

## 4. Demo Workflow

Show the MVP loop:

```text
Prompt -> Strategy JSON -> Backtest -> Risk -> Simulated Orders -> Proof
```

Use one BTC/USDT prompt and one screenshot of the console.

## 5. AI Contribution

Current MVP:

- Natural-language strategy parsing.
- Risk explanation grounded in metrics.
- Parameter suggestions.

Near-term:

- Optional LLM parser and risk narrator.
- Deterministic validator remains the safety layer.

## 6. HTX Integration

Current MVP:

- HTX-compatible market K-line adapter.
- BTC/USDT and ETH/USDT trading pairs.
- Local fallback for demo stability.
- Simulated HTX execution workflow.

Future:

- HTX trading API integration.
- Imported user trade history.
- HTX-native strategy marketplace.

## 7. Web3 Contribution

Current MVP:

- Canonical JSON hashing.
- Strategy hash.
- Backtest hash.
- Execution log hash.
- Combined proof record.

Future:

- Testnet proof anchor.
- Strategy version chain.
- Creator reputation.

## 8. Product Experience

Show the dashboard:

- Prompt editor.
- Strategy JSON.
- Metrics.
- Equity curve.
- Risk report.
- Simulated orders.
- Proof hashes.

## 9. Architecture

High-level modules:

- Frontend console.
- FastAPI backend.
- Strategy parser.
- Market adapter.
- Backtest engine.
- Risk explainer.
- Simulator.
- Proof hasher.
- Run artifacts.

## 10. Safety and Compliance

State clearly:

- No custody.
- No real-money orders in MVP.
- No guaranteed returns.
- Risk-aware research and simulation only.

## 11. Roadmap

MVP:

- One complete strategy workflow.

P1:

- Testnet proof contract.
- Optional LLM parser.
- More strategy templates.
- Route-level API hardening.

P2:

- Marketplace.
- Creator reputation.
- Imported HTX trade history.
- Shadow-account analysis.

## 12. Ask / Closing

ProfitPrince helps HTX users convert ideas into verifiable, risk-aware strategy workflows. The MVP proves the technical loop, and the roadmap extends it into an HTX-native strategy ecosystem.
