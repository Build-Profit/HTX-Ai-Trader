import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from app.models.strategy import Strategy
from app.services.backtest_engine import run_backtest
from app.services.htx_market import get_klines, klines_to_dict
from app.services.proof_hasher import generate_proof
from app.services.risk_explainer import explain_risk
from app.services.simulator import simulate_trade
from app.services.strategy_parser import parse_strategy_text


ROOT_DIR = Path(__file__).resolve().parents[3]
RUNS_DIR = ROOT_DIR / "runs"


def run_demo(strategy_text: str) -> Dict[str, object]:
    strategy = parse_strategy_text(strategy_text)
    market = get_klines(strategy.symbol, strategy.timeframe, limit=120)
    klines = market["klines"]
    backtest = run_backtest(strategy, klines, data_source=str(market["source"]))
    risk = explain_risk(strategy, backtest)
    logs = simulate_trade(strategy, klines[:30])
    proof = generate_proof(
        strategy.to_dict(),
        backtest.to_dict(),
        [item.to_dict() for item in logs],
        version=strategy.version,
    )
    result = {
        "input": strategy_text,
        "strategy": strategy.to_dict(),
        "market": {
            "symbol": market["symbol"],
            "timeframe": market["timeframe"],
            "source": market["source"],
            "klines": klines_to_dict(klines),
        },
        "backtest": backtest.to_dict(),
        "risk": risk,
        "executionLogs": [item.to_dict() for item in logs],
        "proof": proof.to_dict(),
    }
    _write_run_artifacts(result)
    return result


def _write_run_artifacts(result: Dict[str, object]) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S_%f")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir()
    _write_json(run_dir / "strategy_v1.json", result["strategy"])
    _write_json(run_dir / "market_meta.json", {key: result["market"][key] for key in ("symbol", "timeframe", "source")})
    _write_json(run_dir / "backtest_v1.json", result["backtest"])
    _write_json(run_dir / "risk_report_v1.json", result["risk"])
    _write_json(run_dir / "simulated_orders.json", result["executionLogs"])
    _write_json(run_dir / "proof.json", result["proof"])
    (run_dir / "input.txt").write_text(str(result["input"]), encoding="utf-8")


def _write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
