import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.models.proof import ProofRecord


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def generate_proof(strategy: Dict[str, Any], backtest: Dict[str, Any], execution_logs: List[Dict[str, Any]], version: str = "v1") -> ProofRecord:
    strategy_hash = sha256_hex(strategy)
    backtest_hash = sha256_hex(backtest)
    execution_hash = sha256_hex(execution_logs)
    combined_hash = sha256_hex(
        {
            "strategyHash": strategy_hash,
            "backtestHash": backtest_hash,
            "executionLogHash": execution_hash,
            "version": version,
        }
    )
    return ProofRecord(
        version=version,
        timestamp=datetime.now(timezone.utc).isoformat(),
        strategy_hash=strategy_hash,
        backtest_hash=backtest_hash,
        execution_log_hash=execution_hash,
        combined_hash=combined_hash,
    )
