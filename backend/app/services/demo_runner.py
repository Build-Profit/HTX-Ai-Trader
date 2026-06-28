import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from app.models.strategy import Strategy
from app.services.ai_strategy_agent import generate_controller
from app.services.backtest_engine import run_backtest as local_run_backtest
from app.services.hb_facade import health as hb_health
from app.services.hb_facade import run_backtest as hb_run_backtest
from app.services.htx_market import get_klines_with_fine, klines_to_dict, make_fine_fetch_callback
from app.services.proof_hasher import generate_proof
from app.services.risk_explainer import explain_risk
from app.services.simulator import simulate_trade
from app.services.strategy_parser import parse_strategy_text


ROOT_DIR = Path(__file__).resolve().parents[3]
RUNS_DIR = ROOT_DIR / "runs"


def run_demo(strategy_text: str) -> Dict[str, object]:
    strategy = parse_strategy_text(strategy_text)
    market = get_klines_with_fine(strategy.symbol, strategy.timeframe, limit=120)
    klines = market["klines"]
    data_source = str(market["source"])
    fine_klines_map = market.get("fineKlines")
    fetch_fine_cb = make_fine_fetch_callback(strategy.symbol) if data_source == "htx_live" else None
    controller = generate_controller(strategy_text, default_symbol=strategy.symbol)

    hb_health_state = hb_health()
    hb_reachable = bool(hb_health_state.get("reachable"))

    if hb_reachable:
        backtest_result = hb_run_backtest(
            controller,
            klines=klines,
            limit=120,
            fee_rate=0.001,
        )
        backtest = _backtest_dict_to_result(backtest_result, strategy)
        backtest_engine_label = "hummingbot"
    else:
        backtest = local_run_backtest(
            strategy, klines,
            data_source=data_source,
            fine_klines_map=fine_klines_map,
            fetch_fine_callback=fetch_fine_cb,
        )
        backtest_engine_label = "local"
        backtest_result = backtest.to_dict()

    risk = explain_risk(strategy, backtest)

    if hb_reachable:
        logs = []
        paper_trade = {
            "deployable": True,
            "controller": controller,
            "engine": "hummingbot",
        }
        exec_engine_label = "hummingbot"
    else:
        logs = simulate_trade(strategy, klines[:30], fine_klines_map=fine_klines_map)
        paper_trade = None
        exec_engine_label = "local"

    proof = generate_proof(
        strategy.to_dict(),
        backtest.to_dict(),
        [item.to_dict() for item in logs],
        version=strategy.version,
    )

    result = {
        "input": strategy_text,
        "strategy": strategy.to_dict(),
        "hummingbot": controller,
        "market": {
            "symbol": market["symbol"],
            "timeframe": market["timeframe"],
            "source": market["source"],
            "metadata": market.get("metadata", {}),
            "klines": klines_to_dict(klines),
        },
        "backtest": backtest.to_dict(),
        "risk": risk,
        "executionLogs": [item.to_dict() for item in logs],
        "paperTrade": paper_trade,
        "proof": proof.to_dict(),
        "engine": {
            "health": hb_health_state,
            "backtest": backtest_engine_label,
            "execution": exec_engine_label,
        },
    }
    _write_run_artifacts(result)
    return result


def _backtest_dict_to_result(data: Dict[str, object], strategy: Strategy):
    from app.models.backtest import BacktestResult, EquityPoint, Trade

    trades = [
        Trade(
            entry_time=str(item.get("entryTime", "")),
            exit_time=str(item.get("exitTime", "")),
            entry_price=float(item.get("entryPrice", 0)),
            exit_price=float(item.get("exitPrice", 0)),
            quantity=float(item.get("quantity", 0)),
            gross_pnl=float(item.get("grossPnl", 0)),
            net_pnl=float(item.get("netPnl", 0)),
            return_percent=float(item.get("returnPercent", 0)),
            exit_reason=str(item.get("exitReason", "")),
        )
        for item in data.get("trades", [])
    ]
    equity = [
        EquityPoint(timestamp=str(item.get("timestamp", "")), equity=float(item.get("equity", 0)))
        for item in data.get("equityCurve", [])
    ]
    return BacktestResult(
        symbol=str(data.get("symbol", strategy.symbol)),
        timeframe=str(data.get("timeframe", strategy.timeframe)),
        data_source=str(data.get("dataSource", "hummingbot")),
        initial_capital=float(data.get("initialCapital", strategy.capital)),
        final_equity=float(data.get("finalEquity", 0)),
        total_return_percent=float(data.get("totalReturnPercent", 0)),
        buy_hold_return_percent=float(data.get("buyHoldReturnPercent", 0)),
        win_rate_percent=float(data.get("winRatePercent", 0)),
        max_drawdown_percent=float(data.get("maxDrawdownPercent", 0)),
        trade_count=int(data.get("tradeCount", len(trades))),
        profit_loss_ratio=float(data.get("profitLossRatio", 0)),
        fee_rate=float(data.get("feeRate", 0.001)),
        trades=trades,
        equity_curve=equity,
    )


def _write_run_artifacts(result: Dict[str, object]) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S_%f")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir()
    _write_json(run_dir / "strategy_v1.json", result["strategy"])
    _write_json(run_dir / "market_meta.json", {key: result["market"][key] for key in ("symbol", "timeframe", "source", "metadata")})
    _write_json(run_dir / "backtest_v1.json", result["backtest"])
    _write_json(run_dir / "risk_report_v1.json", result["risk"])
    _write_json(run_dir / "simulated_orders.json", result["executionLogs"])
    _write_json(run_dir / "proof.json", result["proof"])
    (run_dir / "input.txt").write_text(str(result["input"]), encoding="utf-8")


def _write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
