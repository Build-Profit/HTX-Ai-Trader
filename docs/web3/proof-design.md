# Proof Design

## Goal

ProfitPrince needs a lightweight way to show that strategy versions, backtest results, and simulated execution logs are traceable and tamper-evident.

The MVP implements local proof hashes. Testnet anchoring is a P1 extension.

## MVP Proof Record

Inputs:

- Strategy JSON.
- Backtest result JSON.
- Simulated execution log JSON.
- Strategy version.

Outputs:

- `strategyHash`
- `backtestHash`
- `executionLogHash`
- `combinedHash`
- `version`
- `timestamp`

## Hashing Method

The backend serializes JSON with:

- Sorted keys.
- Compact separators.
- UTF-8 encoding.

Then it hashes the canonical string with SHA-256.

This gives deterministic hashes for semantically identical JSON objects with different key order.

## Combined Hash

The combined proof hash is derived from:

```json
{
  "strategyHash": "...",
  "backtestHash": "...",
  "executionLogHash": "...",
  "version": "v1"
}
```

This lets the UI show one record that links the strategy, backtest, and simulated execution together.

## What This Proves

The MVP proof can show:

- A displayed strategy has a stable hash.
- A displayed backtest has a stable hash.
- A displayed simulated execution log has a stable hash.
- Any change to these records changes the proof hash.

## What This Does Not Prove

The MVP does not prove:

- That trades happened on a real exchange.
- That a result was anchored on-chain.
- That the strategy will perform similarly in the future.
- That the user should execute it with real funds.

## P1 Testnet Contract

A minimal contract can store:

- `strategyHash`
- `backtestHash`
- `executionLogHash`
- `combinedHash`
- `version`
- `timestamp`
- `submitter`

Suggested event:

```solidity
event StrategyProofRecorded(
    address indexed submitter,
    bytes32 indexed combinedHash,
    bytes32 strategyHash,
    bytes32 backtestHash,
    bytes32 executionLogHash,
    string version,
    uint256 timestamp
);
```

Suggested function:

```solidity
function recordProof(
    bytes32 strategyHash,
    bytes32 backtestHash,
    bytes32 executionLogHash,
    bytes32 combinedHash,
    string calldata version
) external;
```

## Submission Positioning

For the hackathon MVP, describe the Web3 contribution as:

"A tamper-evident strategy proof module that hashes strategy, backtest, and execution records locally, with a clean path to testnet anchoring."

Avoid claiming:

- On-chain execution.
- On-chain performance guarantee.
- Live trading verification.
