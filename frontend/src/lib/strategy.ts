import type { ControllerConfig, Strategy } from "../types";

const DEFAULT_EXCHANGE = "binance";
const DEFAULT_LEVERAGE = 1;

const RISK_LEVELS: Record<string, string[]> = {
  low: ["低风险", "稳健", "保守", "low"],
  medium: ["中风险", "均衡", "medium"],
  high: ["高风险", "激进", "high"],
};

export function normalize(text: string): string {
  return text
    .trim()
    .replace(/％/g, "%")
    .replace(/，/g, ",")
    .replace(/。/g, ".")
    .replace(/：/g, ":")
    .replace(/／/g, "/");
}

export function extractSymbol(text: string): string | null {
  const upper = text.toUpperCase();
  if (upper.includes("ETH/USDT") || upper.includes("ETHUSDT")) return "ETH/USDT";
  if (upper.includes("BTC/USDT") || upper.includes("BTCUSDT")) return "BTC/USDT";
  return null;
}

export function extractTimeframe(text: string): string | null {
  const lowered = text.toLowerCase();
  const mappings: Record<string, string> = {
    "1min": "1m",
    "1m": "1m",
    "1分": "1m",
    "5min": "5m",
    "5m": "5m",
    "5分": "5m",
    "1h": "1h",
    "1小时": "1h",
    "4h": "4h",
    "4小时": "4h",
    "1d": "1d",
    "1天": "1d",
    日线: "1d",
  };
  for (const [token, tf] of Object.entries(mappings)) {
    if (lowered.includes(token)) return tf;
  }
  return null;
}

export function extractCapital(text: string): number | null {
  const patterns = [
    /(\d+(?:\.\d+)?)\s*USDT/i,
    /资金\s*(\d+(?:\.\d+)?)/,
    /capital\s*(\d+(?:\.\d+)?)/i,
  ];
  for (const p of patterns) {
    const m = text.match(p);
    if (m) return parseFloat(m[1]);
  }
  return null;
}

export function extractKeywordPercent(text: string, keywords: string[]): number | null {
  for (const keyword of keywords) {
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const patterns = [
      new RegExp(`${escaped}[^\\d,.;，。]{0,12}(\\d+(?:\\.\\d+)?)\\s*%`, "i"),
      new RegExp(`(\\d+(?:\\.\\d+)?)\\s*%[^\\n,.;，。]{0,12}${escaped}`, "i"),
    ];
    for (const p of patterns) {
      const m = text.match(p);
      if (m) return parseFloat(m[1]);
    }
  }
  return null;
}

export function extractRiskLevel(text: string): string {
  const lowered = text.toLowerCase();
  for (const [level, tokens] of Object.entries(RISK_LEVELS)) {
    if (tokens.some((t) => lowered.includes(t.toLowerCase()))) return level;
  }
  return "medium";
}

function defaultPositionSize(text: string): number {
  const risk = extractRiskLevel(text);
  if (risk === "low") return 20;
  if (risk === "high") return 50;
  return 30;
}

export function parseStrategy(text: string, defaultSymbol = "BTC/USDT"): Strategy {
  const normalized = normalize(text);
  const symbol = extractSymbol(normalized) || defaultSymbol;
  const timeframe = extractTimeframe(normalized) || "1h";
  const capital = extractCapital(normalized) || 1000;
  const dropPercent =
    extractKeywordPercent(normalized, ["跌", "下跌", "回调", "drop"]) || 5;
  const takeProfit =
    extractKeywordPercent(normalized, ["止盈", "涨", "上涨", "take profit", "profit"]) ||
    10;
  const stopLoss =
    extractKeywordPercent(normalized, ["止损", "亏损", "最大亏损", "stop loss", "loss"]) ||
    3;
  const maxDrawdown =
    extractKeywordPercent(normalized, ["最大回撤", "回撤", "drawdown"]) || 5;
  const positionSize =
    extractKeywordPercent(normalized, ["仓位", "position"]) ||
    defaultPositionSize(normalized);
  const riskLevel = extractRiskLevel(normalized);
  return {
    symbol,
    timeframe,
    capital,
    entry: { type: "price_drop", drop_percent: dropPercent },
    exit: { take_profit_percent: takeProfit, stop_loss_percent: stopLoss },
    risk: {
      max_drawdown_percent: maxDrawdown,
      position_size_percent: positionSize,
      risk_level: riskLevel,
    },
    template: "dip_buy_take_profit_stop_loss",
    version: "v1",
  };
}

export function ruleMapper(
  text: string,
  defaultSymbol = "BTC/USDT",
): { controller: ControllerConfig; warnings: string[] } {
  const normalized = normalize(text);
  const lowered = normalized.toLowerCase();
  const symbol = extractSymbol(normalized) || defaultSymbol;
  const capital = extractCapital(normalized) || 1000;
  const warnings: string[] = [];

  const takeProfitPct =
    extractKeywordPercent(normalized, ["止盈", "涨", "上涨", "take profit", "profit"]) || 8;
  const stopLossPct =
    extractKeywordPercent(normalized, ["止损", "亏损", "最大亏损", "stop loss", "loss"]) || 3;
  const dropPct =
    extractKeywordPercent(normalized, ["跌", "下跌", "回调", "drop"]) || 5;

  const tradingPair = symbol.replace("/", "-");
  const takeProfitDec = takeProfitPct / 100;
  const stopLossDec = stopLossPct / 100;
  const dropDec = dropPct / 100;

  if (["做市", "spread", "market making", "pmm"].some((k) => lowered.includes(k))) {
    const buySpread =
      extractKeywordPercent(normalized, ["买价差", "buy spread", "bid spread"]) || 0.5;
    const sellSpread =
      extractKeywordPercent(normalized, ["卖价差", "sell spread", "ask spread"]) || 0.5;
    return {
      controller: {
        controllerType: "market_making",
        controllerName: "pmm_simple",
        config: {
          exchange: DEFAULT_EXCHANGE,
          trading_pair: tradingPair,
          buy_spread: buySpread / 100,
          sell_spread: sellSpread / 100,
          order_amount_usd: capital,
          leverage: DEFAULT_LEVERAGE,
          stop_loss: stopLossDec,
          take_profit: takeProfitDec,
          time_limit: 60 * 60 * 24,
          cooldown_time: 60 * 10,
        },
        generatedBy: "rules",
        warnings,
      },
      warnings,
    };
  }

  if (["网格", "grid"].some((k) => lowered.includes(k))) {
    const minPricePct =
      extractKeywordPercent(normalized, ["最低", "min price", "下限"]) || null;
    const maxPricePct =
      extractKeywordPercent(normalized, ["最高", "max price", "上限"]) || null;
    return {
      controller: {
        controllerType: "generic",
        controllerName: "grid_strike",
        config: {
          exchange: DEFAULT_EXCHANGE,
          trading_pair: tradingPair,
          min_price: minPricePct ? Number(minPricePct) : null,
          max_price: maxPricePct ? Number(maxPricePct) : null,
          grid_levels: 10,
          order_amount_usd: capital,
        },
        generatedBy: "rules",
        warnings,
      },
      warnings,
    };
  }

  if (!["跌", "回调", "drop", "趋势", "bollinger", "bb", "布林"].some((k) => lowered.includes(k))) {
    warnings.push("unsupported_scenario_default_bollinger");
  }

  return {
    controller: {
      controllerType: "directional_trading",
      controllerName: "bollinger_v1",
      config: {
        exchange: DEFAULT_EXCHANGE,
        trading_pair: tradingPair,
        leverage: DEFAULT_LEVERAGE,
        stop_loss: stopLossDec,
        take_profit: takeProfitDec,
        time_limit: 60 * 60 * 24,
        trailing_stop_activation_price_delta: dropDec,
        trailing_stop_trailing_delta: 0.01,
        order_amount_usd: capital,
        cooldown_time: 60 * 10,
        candles_exchange: DEFAULT_EXCHANGE,
        candles_interval: "1h",
        bb_length: 20,
        bb_std: 2.0,
        bb_long_threshold: 0.0,
        bb_short_threshold: 1.0,
      },
      generatedBy: "rules",
      warnings,
    },
    warnings,
  };
}

export function explainStrategy(strategy: Strategy): string {
  return (
    `${strategy.symbol} ${strategy.timeframe} strategy: buy after a ` +
    `${strategy.entry.drop_percent.toFixed(2)}% pullback, take profit at ` +
    `${strategy.exit.take_profit_percent.toFixed(2)}%, stop loss at ` +
    `${strategy.exit.stop_loss_percent.toFixed(2)}%, using ` +
    `${strategy.risk.position_size_percent.toFixed(2)}% position size.`
  );
}
