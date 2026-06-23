# Project Documentation Index

This directory is the working documentation hub for ProfitPrince / HTX-Ai-Trader.

The repository is organized so each member can find the documents that match their role. Product decisions, architecture, implementation plans, demo scripts, API contracts, and verification notes should live here instead of being scattered in chat history.

## Directory Map

| Directory | Owner Role | Purpose |
| --- | --- | --- |
| `plans/` | Product Lead + Tech Lead | Approval-gated implementation plans and milestone plans |
| `product/` | Product / Business / Pitch Lead | PRD notes, positioning, user flows, business model, compliance wording |
| `architecture/` | Tech Lead + Backend Lead | System architecture, module boundaries, data flow, deployment shape |
| `engineering/` | Engineering Lead | Git workflow, coding rules, task ownership, review checklist |
| `frontend/` | Frontend Lead | UI structure, interaction states, dashboard panels, visual cleanup notes |
| `backend/` | Backend / Infra Lead | API contracts, service layout, data models, integration notes |
| `trading-engine/` | Trading Engine / Strategy Lead | Strategy DSL, backtest rules, fee model, simulation ledger |
| `web3/` | Web3 / Proof Lead | Hash proof, version records, testnet contract plan, future ZK notes |
| `qa-demo/` | QA / Demo Lead | Test cases, demo mode, sample data, acceptance checklist |
| `pitch/` | Pitch Lead | Roadshow script, deck outline, judge-facing story |

## Rules

- Plans in `docs/plans/` are not implementation approval by themselves. Work starts only after the plan is approved.
- Keep product claims compliance-safe: no guaranteed profit, no unverifiable win-rate claims, no "risk-free" wording.
- Prefer small documents with clear ownership over one giant shared file.
- When a technical decision changes, update the relevant document before or with the code change.
