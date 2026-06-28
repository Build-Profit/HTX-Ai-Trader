from typing import Callable, Dict, List, Optional, Tuple

from app.models.backtest import BacktestResult, EquityPoint, Trade
from app.models.market import Kline
from app.models.strategy import Strategy


def run_backtest(
    strategy: Strategy,
    klines: List[Kline],
    data_source: str = "local_sample",
    fee_rate: float = 0.001,
    fine_klines_map: Optional[Dict[str, List[Kline]]] = None,
    fetch_fine_callback: Optional[Callable[[str, str], List[Kline]]] = None,
) -> BacktestResult:
    if len(klines) < 2:
        raise ValueError("at least two klines are required")
    strategy.validate()

    cash = strategy.capital
    quantity = 0.0
    entry_price = 0.0
    entry_time = ""
    position_cost = 0.0
    last_peak = klines[0].close
    trades: List[Trade] = []
    equity_curve: List[EquityPoint] = []

    for kline in klines:
        if quantity <= 0:
            last_peak = max(last_peak, kline.close)
            trigger_price = last_peak * (1 - strategy.entry.drop_percent / 100)
            fine_klines = _get_fine_for_candle(
                kline, strategy.timeframe, fine_klines_map, fetch_fine_callback,
            )
            if fine_klines:
                for sub in fine_klines:
                    if sub.close <= trigger_price:
                        position_cost = cash * strategy.risk.position_size_percent / 100
                        entry_fee = position_cost * fee_rate
                        entry_price = sub.close
                        quantity = (position_cost - entry_fee) / entry_price
                        cash -= position_cost
                        entry_time = sub.timestamp
                        break
            else:
                if kline.close <= trigger_price:
                    position_cost = cash * strategy.risk.position_size_percent / 100
                    entry_fee = position_cost * fee_rate
                    entry_price = kline.close
                    quantity = (position_cost - entry_fee) / entry_price
                    cash -= position_cost
                    entry_time = kline.timestamp
        else:
            stop_price = entry_price * (1 - strategy.exit.stop_loss_percent / 100)
            take_price = entry_price * (1 + strategy.exit.take_profit_percent / 100)
            fine_klines = _get_fine_for_candle(
                kline, strategy.timeframe, fine_klines_map, fetch_fine_callback,
            )
            exit_price, reason = _resolve_exit(kline, stop_price, take_price, fine_klines)
            if exit_price is not None and reason is not None:
                gross_value = quantity * exit_price
                exit_fee = gross_value * fee_rate
                net_value = gross_value - exit_fee
                gross_pnl = gross_value - position_cost
                net_pnl = net_value - position_cost
                cash += net_value
                trades.append(
                    Trade(
                        entry_time=entry_time,
                        exit_time=kline.timestamp,
                        entry_price=round(entry_price, 8),
                        exit_price=round(exit_price, 8),
                        quantity=round(quantity, 8),
                        gross_pnl=round(gross_pnl, 6),
                        net_pnl=round(net_pnl, 6),
                        return_percent=round((net_pnl / position_cost) * 100, 6),
                        exit_reason=reason,
                    )
                )
                quantity = 0.0
                entry_price = 0.0
                position_cost = 0.0
                last_peak = kline.close

        equity_curve.append(EquityPoint(timestamp=kline.timestamp, equity=round(_mark_equity(cash, quantity, kline.close, fee_rate), 6)))

    final_equity = _mark_equity(cash, quantity, klines[-1].close, fee_rate)
    total_return = (final_equity / strategy.capital - 1) * 100
    wins = [trade.net_pnl for trade in trades if trade.net_pnl > 0]
    losses = [trade.net_pnl for trade in trades if trade.net_pnl < 0]
    win_rate = (len(wins) / len(trades) * 100) if trades else 0.0
    profit_loss_ratio = _profit_loss_ratio(wins, losses)
    buy_hold_return = (klines[-1].close / klines[0].close - 1) * 100

    return BacktestResult(
        symbol=strategy.symbol,
        timeframe=strategy.timeframe,
        data_source=data_source,
        initial_capital=round(strategy.capital, 6),
        final_equity=round(final_equity, 6),
        total_return_percent=round(total_return, 6),
        buy_hold_return_percent=round(buy_hold_return, 6),
        win_rate_percent=round(win_rate, 6),
        max_drawdown_percent=round(_max_drawdown(equity_curve), 6),
        trade_count=len(trades),
        profit_loss_ratio=round(profit_loss_ratio, 6),
        fee_rate=fee_rate,
        trades=trades,
        equity_curve=equity_curve,
    )


def _get_fine_for_candle(
    kline: Kline,
    timeframe: str,
    fine_map: Optional[Dict[str, List[Kline]]],
    fetch_cb: Optional[Callable[[str, str], List[Kline]]],
) -> Optional[List[Kline]]:
    fine = (fine_map or {}).get(kline.timestamp)
    if fine is not None:
        return fine
    if fetch_cb is not None:
        fetched = fetch_cb(kline.timestamp, timeframe)
        if fetched:
            if fine_map is not None:
                fine_map[kline.timestamp] = fetched
            return fetched
    return None


def _resolve_exit(
    kline: Kline,
    stop_price: float,
    take_price: float,
    fine_klines: Optional[List[Kline]] = None,
) -> Tuple[Optional[float], Optional[str]]:
    if fine_klines:
        for sub in fine_klines:
            if sub.low <= stop_price:
                return stop_price, "stop_loss"
            if sub.high >= take_price:
                return take_price, "take_profit"
        return None, None
    if kline.low <= stop_price:
        return stop_price, "stop_loss"
    if kline.high >= take_price:
        return take_price, "take_profit"
    return None, None


def _mark_equity(cash: float, quantity: float, close: float, fee_rate: float) -> float:
    if quantity <= 0:
        return cash
    gross_value = quantity * close
    return cash + gross_value * (1 - fee_rate)


def _max_drawdown(points: List[EquityPoint]) -> float:
    peak = points[0].equity
    max_dd = 0.0
    for point in points:
        peak = max(peak, point.equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - point.equity) / peak * 100)
    return max_dd


def _profit_loss_ratio(wins: List[float], losses: List[float]) -> float:
    if not wins:
        return 0.0
    if not losses:
        return 999.0
    avg_win = sum(wins) / len(wins)
    avg_loss = abs(sum(losses) / len(losses))
    if avg_loss == 0:
        return 999.0
    return avg_win / avg_loss
