export interface EntryRule {
  type: string;
  drop_percent: number;
}

export interface ExitRule {
  take_profit_percent: number;
  stop_loss_percent: number;
}

export interface RiskRule {
  max_drawdown_percent: number;
  position_size_percent: number;
  risk_level: string;
}

export interface Strategy {
  symbol: string;
  timeframe: string;
  capital: number;
  entry: EntryRule;
  exit: ExitRule;
  risk: RiskRule;
  template?: string;
  version?: string;
}

export interface Trade {
  entryTime: string;
  exitTime: string;
  entryPrice: number;
  exitPrice: number;
  quantity: number;
  grossPnl: number;
  netPnl: number;
  returnPercent: number;
  exitReason: string;
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
}

export interface BacktestResult {
  symbol: string;
  timeframe: string;
  dataSource: string;
  initialCapital: number;
  finalEquity: number;
  totalReturnPercent: number;
  buyHoldReturnPercent: number;
  winRatePercent: number;
  maxDrawdownPercent: number;
  tradeCount: number;
  profitLossRatio: number;
  feeRate: number;
  trades: Trade[];
  equityCurve: EquityPoint[];
}

export interface Kline {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ControllerConfig {
  controllerType: string;
  controllerName: string;
  config: Record<string, unknown>;
  generatedBy: string;
  warnings: string[];
}

export interface RiskReport {
  riskScore: number;
  riskLevel: string;
  summary: string;
  suitableMarket: string;
  unsuitableMarket: string;
  keyRisks: string[];
  suggestions: string[];
  executionRecommendation: string;
}

export interface ProofRecord {
  version: string;
  timestamp: string;
  strategyHash: string;
  backtestHash: string;
  executionLogHash: string;
  combinedHash: string;
}

export interface ExecutionLog {
  timestamp: string;
  event: string;
  status: string;
  symbol?: string;
  price?: number;
  quantity?: number;
  message?: string;
}

export interface DemoResult {
  input: string;
  strategy: Strategy;
  market?: { symbol: string; timeframe: string; source: string };
  backtest: BacktestResult;
  risk: RiskReport;
  executionLogs: ExecutionLog[];
  proof: ProofRecord;
  hummingbot?: ControllerConfig;
  engine?: Record<string, string>;
  paperTradeDeployable?: boolean;
}

export interface HbStatus {
  reachable: boolean;
  engine: string;
  raw?: unknown;
}

export interface HbBotStatus {
  botId: string;
  status: string;
  executors: unknown[];
  positions: HbPosition[];
  executionLogs: ExecutionLog[];
  engine?: string;
}

export interface HbPosition {
  symbol?: string;
  trading_pair?: string;
  amount?: number;
  size?: number;
  side?: string;
  side_code?: string;
}

export interface HbDebugEntry {
  id: number;
  method: string;
  path: string;
  status: number | string;
  ok: boolean;
  request?: unknown;
  response?: unknown;
  error?: string;
  timestamp: string;
}

export interface LlmSettings {
  baseUrl: string;
  apiKey: string;
  model: string;
}

export interface HbAuthSettings {
  user: string;
  password: string;
}
