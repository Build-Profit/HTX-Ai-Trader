from typing import List

from app.models.market import Kline
from app.models.strategy import Strategy
from app.models.trade import ExecutionLog


def simulate_trade(strategy: Strategy, klines: List[Kline]) -> List[ExecutionLog]:
    if not klines:
        raise ValueError("klines are required")

    logs: List[ExecutionLog] = []
    first = klines[0]
    last = klines[-1]
    quantity = (strategy.capital * strategy.risk.position_size_percent / 100) / first.close

    logs.append(
        ExecutionLog(
            timestamp=first.timestamp,
            event="order_created",
            status="created",
            symbol=strategy.symbol,
            price=round(first.close, 8),
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
            price=round(first.close, 8),
            quantity=round(quantity, 8),
            message="Simulated order filled at sample market close price.",
        )
    )

    stop_price = first.close * (1 - strategy.exit.stop_loss_percent / 100)
    take_price = first.close * (1 + strategy.exit.take_profit_percent / 100)
    for kline in klines[1:]:
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
