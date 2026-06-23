from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ProofRecord:
    version: str
    timestamp: str
    strategy_hash: str
    backtest_hash: str
    execution_log_hash: str
    combined_hash: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "strategyHash": self.strategy_hash,
            "backtestHash": self.backtest_hash,
            "executionLogHash": self.execution_log_hash,
            "combinedHash": self.combined_hash,
        }
