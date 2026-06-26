import type { BacktestResult, EquityPoint, Kline, Strategy, Trade } from "../types";

export function runBacktest(
  strategy: Strategy,
  klines: Kline[],
  dataSource = "local_sample",
  feeRate = 0.001,
): BacktestResult {
  if (klines.length < 2) {
    throw new Error("at least two klines are required");
  }

  let cash = strategy.capital;
  let quantity = 0;
  let entryPrice = 0;
  let entryTime = "";
  let positionCost = 0;
  let lastPeak = klines[0].close;
  const trades: Trade[] = [];
  const equityCurve: EquityPoint[] = [];

  for (const kline of klines) {
    if (quantity <= 0) {
      lastPeak = Math.max(lastPeak, kline.close);
      const triggerPrice = lastPeak * (1 - strategy.entry.drop_percent / 100);
      if (kline.close <= triggerPrice) {
        positionCost = (cash * strategy.risk.position_size_percent) / 100;
        const entryFee = positionCost * feeRate;
        entryPrice = kline.close;
        quantity = (positionCost - entryFee) / entryPrice;
        cash -= positionCost;
        entryTime = kline.timestamp;
      }
    } else {
      const stopPrice = entryPrice * (1 - strategy.exit.stop_loss_percent / 100);
      const takePrice = entryPrice * (1 + strategy.exit.take_profit_percent / 100);
      const [exitPrice, reason] = resolveExit(kline, stopPrice, takePrice);
      if (exitPrice !== null && reason !== null) {
        const grossValue = quantity * exitPrice;
        const exitFee = grossValue * feeRate;
        const netValue = grossValue - exitFee;
        const grossPnl = grossValue - positionCost;
        const netPnl = netValue - positionCost;
        cash += netValue;
        trades.push({
          entryTime,
          exitTime: kline.timestamp,
          entryPrice: round(entryPrice, 8),
          exitPrice: round(exitPrice, 8),
          quantity: round(quantity, 8),
          grossPnl: round(grossPnl, 6),
          netPnl: round(netPnl, 6),
          returnPercent: round((netPnl / positionCost) * 100, 6),
          exitReason: reason,
        });
        quantity = 0;
        entryPrice = 0;
        positionCost = 0;
        lastPeak = kline.close;
      }
    }
    equityCurve.push({
      timestamp: kline.timestamp,
      equity: round(markEquity(cash, quantity, kline.close, feeRate), 6),
    });
  }

  const finalEquity = markEquity(cash, quantity, klines[klines.length - 1].close, feeRate);
  const totalReturn = (finalEquity / strategy.capital - 1) * 100;
  const wins = trades.filter((t) => t.netPnl > 0).map((t) => t.netPnl);
  const losses = trades.filter((t) => t.netPnl < 0).map((t) => t.netPnl);
  const winRate = trades.length ? (wins.length / trades.length) * 100 : 0;
  const profitLossRatio = computePlRatio(wins, losses);
  const buyHoldReturn = (klines[klines.length - 1].close / klines[0].close - 1) * 100;

  return {
    symbol: strategy.symbol,
    timeframe: strategy.timeframe,
    dataSource,
    initialCapital: round(strategy.capital, 6),
    finalEquity: round(finalEquity, 6),
    totalReturnPercent: round(totalReturn, 6),
    buyHoldReturnPercent: round(buyHoldReturn, 6),
    winRatePercent: round(winRate, 6),
    maxDrawdownPercent: round(maxDrawdown(equityCurve), 6),
    tradeCount: trades.length,
    profitLossRatio: round(profitLossRatio, 6),
    feeRate,
    trades,
    equityCurve,
  };
}

function resolveExit(
  kline: Kline,
  stopPrice: number,
  takePrice: number,
): [number | null, string | null] {
  if (kline.low <= stopPrice) return [stopPrice, "stop_loss"];
  if (kline.high >= takePrice) return [takePrice, "take_profit"];
  return [null, null];
}

function markEquity(cash: number, quantity: number, close: number, feeRate: number): number {
  if (quantity <= 0) return cash;
  const grossValue = quantity * close;
  return cash + grossValue * (1 - feeRate);
}

function maxDrawdown(points: EquityPoint[]): number {
  let peak = points[0].equity;
  let maxDd = 0;
  for (const point of points) {
    peak = Math.max(peak, point.equity);
    if (peak > 0) {
      maxDd = Math.max(maxDd, ((peak - point.equity) / peak) * 100);
    }
  }
  return maxDd;
}

function computePlRatio(wins: number[], losses: number[]): number {
  if (!wins.length) return 0;
  if (!losses.length) return 999;
  const avgWin = wins.reduce((a, b) => a + b, 0) / wins.length;
  const avgLoss = Math.abs(losses.reduce((a, b) => a + b, 0) / losses.length);
  if (avgLoss === 0) return 999;
  return avgWin / avgLoss;
}

function round(value: number, digits: number): number {
  const f = Math.pow(10, digits);
  return Math.round(value * f) / f;
}
