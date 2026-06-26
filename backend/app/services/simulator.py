from typing import Dict, List, Optional

from app.models.market import Kline
from app.models.strategy import Strategy
from app.models.trade import ExecutionLog


def simulate_trade(
    strategy: Strategy,
    klines: List[Kline],
    fine_klines_map: Optional[Dict[str, List[Kline]]] = None,
) -> List[ExecutionLog]:
    if not klines:
        raise ValueError("klines are required")

    logs: List[ExecutionLog] = []
    first = klines[0]
    last = klines[-1]
    entry_price = first.close
    fine_entry = (fine_klines_map or {}).get(first.timestamp)
    if fine_entry:
        for sub in fine_entry:
            if sub.close is not None:
                entry_price = sub.close
                break
    quantity = (strategy.capital * strategy.risk.position_size_percent / 100) / entry_price

    logs.append(
        ExecutionLog(
            timestamp=first.timestamp,
            event="order_created",
            status="created",
            symbol=strategy.symbol,
            price=round(entry_price, 8),
            quantity=round(quantity, 8),
            message="Simulated entry order created. No real exchange order was sent.",
        )
    )
    logs.append(
        ExecutionLog(
            timestamp=first.timestamp,
            event="order_filled",
            status="filled",
            symbol=strategy.symbol,
            price=round(entry_price, 8),
            quantity=round(quantity, 8),
            message="Simulated order filled at sample market close price.",
        )
    )

    stop_price = entry_price * (1 - strategy.exit.stop_loss_percent / 100)
    take_price = entry_price * (1 + strategy.exit.take_profit_percent / 100)
    for kline in klines[1:]:
        fine_klines = (fine_klines_map or {}).get(kline.timestamp)
        if fine_klines:
            for sub in fine_klines:
                if sub.low <= stop_price:
                    logs.append(
                        ExecutionLog(
                            timestamp=sub.timestamp,
                            event="stop_loss_triggered",
                            status="closed",
                            symbol=strategy.symbol,
                            price=round(stop_price, 8),
                            quantity=round(quantity, 8),
                            message="Simulated stop loss triggered via sub-candle resolution.",
                        )
                    )
                    return logs
                if sub.high >= take_price:
                    logs.append(
                        ExecutionLog(
                            timestamp=sub.timestamp,
                            event="take_profit_triggered",
                            status="closed",
                            symbol=strategy.symbol,
                            price=round(take_price, 8),
                            quantity=round(quantity, 8),
                            message="Simulated take profit triggered via sub-candle resolution.",
                        )
                    )
                    return logs
        else:
            if kline.low <= stop_price:
                logs.append(
                    ExecutionLog(
                        timestamp=kline.timestamp,
                        event="stop_loss_triggered",
                        status="closed",
                        symbol=strategy.symbol,
                        price=round(stop_price, 8),
                        quantity=round(quantity, 8),
                        message="Simulated stop loss triggered.",
                    )
                )
                return logs
            if kline.high >= take_price:
                logs.append(
                    ExecutionLog(
                        timestamp=kline.timestamp,
                        event="take_profit_triggered",
                        status="closed",
                        symbol=strategy.symbol,
                        price=round(take_price, 8),
                        quantity=round(quantity, 8),
                        message="Simulated take profit triggered.",
                    )
                )
                return logs

    logs.append(
        ExecutionLog(
            timestamp=last.timestamp,
            event="manual_stop",
            status="closed",
            symbol=strategy.symbol,
            price=round(last.close, 8),
            quantity=round(quantity, 8),
            message="Simulation ended at last available candle.",
        )
    )
    return logs
