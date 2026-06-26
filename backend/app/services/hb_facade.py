"""Unified facade: Hummingbot when reachable, local engine fallback.

Bot orchestration endpoints do NOT fall back — caller must handle HTTPException(503).
"""
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.models.backtest import BacktestResult, EquityPoint, Trade
from app.models.market import Kline
from app.models.strategy import EntryRule, ExitRule, RiskRule, Strategy
from app.services import config
from app.services.backtest_engine import run_backtest as local_run_backtest
from app.services.htx_market import get_klines as local_get_klines
from app.services.htx_market import get_klines_with_fine, make_fine_fetch_callback
from app.services.hummingbot_client import HummingbotClient, HummingbotError, get_client


# --- Helpers ---------------------------------------------------------------

def _client() -> HummingbotClient:
    return get_client()


def _hb_enabled() -> bool:
    return config.hummingbot_enabled()


def _controller_to_strategy(controller_cfg: Dict[str, Any], default_symbol: str = "BTC/USDT") -> Strategy:
    """Map Hummingbot controller params back to local Strategy DSL so the
    existing backtest_engine can run on fallback."""
    inner = controller_cfg.get("config", {}) if isinstance(controller_cfg.get("config"), dict) else {}
    trading_pair = str(inner.get("trading_pair", default_symbol.replace("/", "-")))
    symbol = trading_pair.replace("-", "/")
    if symbol not in {"BTC/USDT", "ETH/USDT"}:
        symbol = default_symbol
    capital = float(inner.get("order_amount_usd", 1000.0))
    stop_loss_dec = float(inner.get("stop_loss", 0.03))
    take_profit_dec = float(inner.get("take_profit", 0.08))
    drop_dec = float(inner.get("trailing_stop_activation_price_delta", 0.05))
    position_size = 30.0
    max_drawdown = max(5.0, stop_loss_dec * 100)
    strategy = Strategy(
        symbol=symbol,
        timeframe=str(inner.get("candles_interval", "1h")),
        capital=capital,
        entry=EntryRule(type="price_drop", drop_percent=drop_dec * 100),
        exit=ExitRule(
            take_profit_percent=take_profit_dec * 100,
            stop_loss_percent=stop_loss_dec * 100,
        ),
        risk=RiskRule(
            max_drawdown_percent=max_drawdown,
            position_size_percent=position_size,
            risk_level="medium",
        ),
    )
    strategy.validate()
    return strategy


def _hb_candles_to_klines(data: Any) -> List[Kline]:
    rows: List[Any] = []
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        for key in ("candles", "data", "klines", "rows"):
            if isinstance(data.get(key), list):
                rows = data[key]
                break
    klines: List[Kline] = []
    for row in rows:
        if isinstance(row, dict):
            try:
                klines.append(
                    Kline(
                        timestamp=str(row.get("timestamp", row.get("time", ""))),
                        open=float(row.get("open", row.get("o", 0))),
                        high=float(row.get("high", row.get("h", 0))),
                        low=float(row.get("low", row.get("l", 0))),
                        close=float(row.get("close", row.get("c", 0))),
                        volume=float(row.get("volume", row.get("v", 0))),
                    )
                )
            except (TypeError, ValueError):
                continue
        elif isinstance(row, (list, tuple)) and len(row) >= 5:
            try:
                klines.append(
                    Kline(
                        timestamp=str(row[0]),
                        open=float(row[1]),
                        high=float(row[2]),
                        low=float(row[3]),
                        close=float(row[4]),
                        volume=float(row[5]) if len(row) > 5 else 0.0,
                    )
                )
            except (TypeError, ValueError):
                continue
    return klines


# --- Public API ------------------------------------------------------------

def health() -> Dict[str, Any]:
    if not _hb_enabled():
        return {"reachable": False, "engine": "local"}
    try:
        reachable = _client().is_reachable()
    except Exception:
        reachable = False
    return {"reachable": bool(reachable), "engine": "hummingbot" if reachable else "local"}


def get_klines(symbol: str, timeframe: str = "1h", limit: int = 120) -> Dict[str, Any]:
    if _hb_enabled():
        try:
            client = _client()
            if client.is_reachable():
                raw = client.get_candles(symbol, timeframe, max_records=limit)
                klines = _hb_candles_to_klines(raw)
                if klines:
                    return {
                        "source": "hummingbot",
                        "metadata": {"endpoint": "hummingbot", "raw": raw if isinstance(raw, dict) else {}},
                        "klines": klines,
                        "engine": "hummingbot",
                    }
        except (HummingbotError, Exception):
            pass

    market = local_get_klines(symbol, timeframe, limit)
    return {
        "source": market["source"],
        "metadata": market.get("metadata", {}),
        "klines": market["klines"],
        "engine": "local",
    }


def run_backtest(
    controller_cfg: Dict[str, Any],
    klines: Optional[List[Kline]] = None,
    limit: int = 120,
    fee_rate: float = 0.001,
) -> Dict[str, Any]:
    if _hb_enabled():
        try:
            client = _client()
            if client.is_reachable():
                raw = client.run_backtest(controller_cfg)
                mapped = _map_hb_backtest(raw, controller_cfg, fee_rate)
                if mapped is not None:
                    mapped["engine"] = "hummingbot"
                    return mapped
        except (HummingbotError, Exception):
            pass

    # Local fallback with fine-grained sub-candle resolution.
    cfg = controller_cfg.get("config") if isinstance(controller_cfg, dict) else None
    if not isinstance(cfg, dict):
        cfg = {}
    strategy = _controller_to_strategy(controller_cfg)
    if klines is None:
        market = get_klines_with_fine(strategy.symbol, strategy.timeframe, limit)
        klines = market["klines"]
        data_source = str(market["source"])
        fine_klines_map = market.get("fineKlines")
        fetch_fine_cb = make_fine_fetch_callback(strategy.symbol) if data_source == "htx_live" else None
    else:
        data_source = "request_payload"
        fine_klines_map = None
        fetch_fine_cb = None
    result = local_run_backtest(
        strategy, klines,
        data_source=data_source,
        fee_rate=fee_rate,
        fine_klines_map=fine_klines_map,
        fetch_fine_callback=fetch_fine_cb,
    )
    out = result.to_dict()
    out["engine"] = "local"
    return out


def _map_hb_backtest(raw: Any, controller_cfg: Dict[str, Any], fee_rate: float) -> Optional[Dict[str, Any]]:
    try:
        data = raw if isinstance(raw, dict) else {}
        inner = controller_cfg.get("config", {}) if isinstance(controller_cfg.get("config"), dict) else {}
        symbol = str(inner.get("trading_pair", "BTC-USDT")).replace("-", "/")
        timeframe = str(inner.get("candles_interval", "1h"))

        equity_curve = _extract_equity_curve(data)
        trades = _extract_trades(data)
        final_equity = float(data.get("final_equity", data.get("finalEquity", equity_curve[-1]["equity"] if equity_curve else 0)))
        initial = float(data.get("initial_capital", data.get("initialCapital", inner.get("order_amount_usd", 1000.0))))
        total_return = float(data.get("total_return_percent", data.get("totalReturnPercent",
            ((final_equity / initial) - 1) * 100 if initial else 0.0)))
        win_rate = float(data.get("win_rate_percent", data.get("winRatePercent", 0.0)))
        max_dd = float(data.get("max_drawdown_percent", data.get("maxDrawdownPercent", 0.0)))
        trade_count = int(data.get("trade_count", data.get("tradeCount", len(trades))))
        buy_hold = float(data.get("buy_hold_return_percent", data.get("buyHoldReturnPercent", 0.0)))
        pl_ratio = float(data.get("profit_loss_ratio", data.get("profitLossRatio", 0.0)))

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "dataSource": "hummingbot",
            "initialCapital": initial,
            "finalEquity": final_equity,
            "totalReturnPercent": total_return,
            "buyHoldReturnPercent": buy_hold,
            "winRatePercent": win_rate,
            "maxDrawdownPercent": max_dd,
            "tradeCount": trade_count,
            "profitLossRatio": pl_ratio,
            "feeRate": fee_rate,
            "trades": trades,
            "equityCurve": equity_curve,
        }
    except (TypeError, ValueError, KeyError):
        return None


def _extract_equity_curve(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("equity_curve", "equityCurve", "equity"):
        value = data.get(key)
        if isinstance(value, list):
            out = []
            for point in value:
                if isinstance(point, dict):
                    ts = point.get("timestamp", point.get("time", ""))
                    eq = point.get("equity", point.get("value", 0))
                    try:
                        out.append({"timestamp": str(ts), "equity": float(eq)})
                    except (TypeError, ValueError):
                        continue
            if out:
                return out
    return []


def _extract_trades(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("trades", "executions"):
        value = data.get(key)
        if isinstance(value, list):
            out = []
            for trade in value:
                if not isinstance(trade, dict):
                    continue
                try:
                    out.append({
                        "entryTime": str(trade.get("entry_time", trade.get("entryTime", ""))),
                        "exitTime": str(trade.get("exit_time", trade.get("exitTime", ""))),
                        "entryPrice": float(trade.get("entry_price", trade.get("entryPrice", 0))),
                        "exitPrice": float(trade.get("exit_price", trade.get("exitPrice", 0))),
                        "quantity": float(trade.get("amount", trade.get("quantity", 0))),
                        "grossPnl": float(trade.get("gross_pnl", trade.get("grossPnl", 0))),
                        "netPnl": float(trade.get("net_pnl", trade.get("netPnl", 0))),
                        "returnPercent": float(trade.get("return_percent", trade.get("returnPercent", 0))),
                        "exitReason": str(trade.get("exit_reason", trade.get("exitReason", ""))),
                    })
                except (TypeError, ValueError):
                    continue
            return out
    return []


def deploy_paper_trade_bot(controller_cfg: Dict[str, Any], bot_name: str) -> Dict[str, Any]:
    if not _hb_enabled():
        raise HTTPException(status_code=503, detail="Hummingbot API unreachable: hummingbot disabled by config")
    try:
        client = _client()
        if not client.is_reachable():
            raise HTTPException(status_code=503, detail="Hummingbot API unreachable: health probe failed")
        payload = {
            "bot_name": bot_name,
            "controller_config": controller_cfg,
            "paper_trade": True,
        }
        result = client.deploy_bot(payload)
        return {
            "botId": str(result.get("bot_id", result.get("botId", bot_name))),
            "status": str(result.get("status", "deployed")),
            "engine": "hummingbot",
            "raw": result,
        }
    except HTTPException:
        raise
    except HummingbotError as exc:
        raise HTTPException(status_code=503, detail=f"Hummingbot API unreachable: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Hummingbot API unreachable: {exc}") from exc


def get_bot_status(bot_name: str) -> Dict[str, Any]:
    if not _hb_enabled():
        raise HTTPException(status_code=503, detail="Hummingbot API unreachable: hummingbot disabled by config")
    try:
        client = _client()
        if not client.is_reachable():
            raise HTTPException(status_code=503, detail="Hummingbot API unreachable: health probe failed")
        result = client.get_bot_status(bot_name)
        return {
            "botId": bot_name,
            "status": str(result.get("status", "unknown")),
            "executors": result.get("executors", []),
            "positions": result.get("positions", []),
            "executionLogs": result.get("execution_logs", result.get("executionLogs", [])),
            "engine": "hummingbot",
        }
    except HTTPException:
        raise
    except HummingbotError as exc:
        raise HTTPException(status_code=503, detail=f"Hummingbot API unreachable: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Hummingbot API unreachable: {exc}") from exc


def stop_bot(bot_name: str) -> Dict[str, Any]:
    if not _hb_enabled():
        raise HTTPException(status_code=503, detail="Hummingbot API unreachable: hummingbot disabled by config")
    try:
        client = _client()
        if not client.is_reachable():
            raise HTTPException(status_code=503, detail="Hummingbot API unreachable: health probe failed")
        result = client.stop_and_archive_bot(bot_name)
        return {
            "botId": bot_name,
            "status": str(result.get("status", "stopped")),
            "engine": "hummingbot",
        }
    except HTTPException:
        raise
    except HummingbotError as exc:
        raise HTTPException(status_code=503, detail=f"Hummingbot API unreachable: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Hummingbot API unreachable: {exc}") from exc


def get_portfolio() -> Dict[str, Any]:
    if not _hb_enabled():
        raise HTTPException(status_code=503, detail="Hummingbot API unreachable: hummingbot disabled by config")
    try:
        client = _client()
        if not client.is_reachable():
            raise HTTPException(status_code=503, detail="Hummingbot API unreachable: health probe failed")
        result = client.get_portfolio_state()
        if not isinstance(result, dict):
            result = {"raw": result}
        result["engine"] = "hummingbot"
        return result
    except HTTPException:
        raise
    except HummingbotError as exc:
        raise HTTPException(status_code=503, detail=f"Hummingbot API unreachable: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Hummingbot API unreachable: {exc}") from exc
