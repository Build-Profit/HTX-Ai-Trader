import { useCallback, useEffect, useState } from "react";
import { parseStrategy, ruleMapper } from "./lib/strategy";
import { runBacktest } from "./lib/backtest";
import { explainRisk } from "./lib/risk";
import { generateProof } from "./lib/proof";
import { loadLlmSettings, saveLlmSettings, tryLlm } from "./lib/llm";
import { fetchCandles, loadHbAuth, saveHbAuth } from "./api/hb";
import { presets } from "./lib/presets";
import { sampleResult } from "./lib/sample";
import { sourceTone, type Tone } from "./lib/format";
import { useHbHealth } from "./hooks/useHbHealth";
import { useBotPolling } from "./hooks/useBotPolling";
import { TopBar } from "./components/TopBar";
import { ControlPanel } from "./components/ControlPanel";
import { MetricsGrid } from "./components/MetricsGrid";
import { EquityChart } from "./components/EquityChart";
import { RiskPanel } from "./components/RiskPanel";
import { ProofPanel } from "./components/ProofPanel";
import { OrdersTable } from "./components/OrdersTable";
import { HbControllerPanel } from "./components/HbControllerPanel";
import { HbBotPanel } from "./components/HbBotPanel";
import { HbApiDebugPanel } from "./components/HbApiDebugPanel";
import type {
  BacktestResult,
  ControllerConfig,
  DemoResult,
  ExecutionLog,
  HbAuthSettings,
  Kline,
  LlmSettings,
} from "./types";

export default function App() {
  const [strategyText, setStrategyText] = useState<string>(presets.balanced);
  const [activePreset, setActivePreset] = useState<string>("balanced");
  const [running, setRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DemoResult | null>(null);
  const [llmSettings, setLlmSettings] = useState<LlmSettings | null>(() => loadLlmSettings());
  const [hbAuth, setHbAuth] = useState<HbAuthSettings>(() => loadHbAuth());

  const hbHealth = useHbHealth();
  const bot = useBotPolling();

  const handleRunDemo = useCallback(async () => {
    setRunning(true);
    setError(null);
    try {
      const strategy = parseStrategy(strategyText);
      const { controller: ruleController, warnings } = ruleMapper(strategyText);
      let controller: ControllerConfig = ruleController;

      const settings = loadLlmSettings();
      if (settings) {
        const llmController = await tryLlm(strategyText, settings);
        if (llmController) {
          llmController.warnings = [...warnings, ...(llmController.warnings ?? [])];
          llmController.generatedBy = "llm";
          controller = llmController;
        } else {
          controller.warnings = [...warnings, "llm_unavailable: call_failed_or_invalid_response"];
        }
      }

      const cfg = controller.config as Record<string, unknown>;
      const exchange = String(cfg.exchange ?? cfg.candles_exchange ?? "binance");
      const tradingPair = String(cfg.trading_pair ?? strategy.symbol.replace("/", "-"));
      const interval = String(cfg.candles_interval ?? strategy.timeframe);

      let klines: Kline[] = [];
      let dataSource = "local_sample";
      try {
        const fetched = await fetchCandles(exchange, tradingPair, interval, 120);
        klines = fetched.klines;
        if (klines.length >= 2) dataSource = fetched.source;
        else klines = [];
      } catch {
        klines = [];
      }

      let backtest: BacktestResult;
      let executionLogs: ExecutionLog[];
      if (klines.length >= 2) {
        backtest = runBacktest(strategy, klines, dataSource);
        executionLogs = backtest.trades.map((t) => ({
          timestamp: t.exitTime,
          event: "trade_closed",
          status: t.exitReason,
          symbol: strategy.symbol,
          price: t.exitPrice,
          quantity: t.quantity,
          message: `net PnL ${t.netPnl}`,
        }));
      } else {
        backtest = { ...sampleResult.backtest, dataSource: "local_sample_preview" };
        executionLogs = sampleResult.executionLogs;
      }

      const riskReport = explainRisk(strategy, backtest);
      const proof = await generateProof(strategy, backtest, executionLogs);

      setResult({
        input: strategyText,
        strategy,
        market: { symbol: strategy.symbol, timeframe: strategy.timeframe, source: dataSource },
        backtest,
        risk: riskReport,
        executionLogs,
        proof,
        hummingbot: controller,
        engine: { name: hbHealth.reachable ? "hummingbot" : "local" },
        paperTradeDeployable: riskReport.executionRecommendation !== "do_not_execute_live",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setRunning(false);
    }
  }, [strategyText, hbHealth.reachable]);

  useEffect(() => {
    void handleRunDemo();
    // mount-only: preset switch should NOT auto-rerun; user clicks Run Demo explicitly
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onPresetChange = useCallback((key: string) => {
    setActivePreset(key);
    setStrategyText(presets[key] ?? presets.balanced);
  }, []);

  const onLlmSave = useCallback(
    (s: LlmSettings) => {
      saveLlmSettings(s);
      setLlmSettings(s);
    },
    [],
  );

  const onHbAuthSave = useCallback(
    (s: HbAuthSettings) => {
      saveHbAuth(s);
      setHbAuth(s);
      hbHealth.refresh();
    },
    [hbHealth],
  );

  const backtest = result?.backtest ?? null;
  const risk = result?.risk ?? null;
  const proof = result?.proof ?? null;
  const executionLogs = result?.executionLogs ?? [];
  const controller = result?.hummingbot ?? null;
  const dataSource = result?.backtest?.dataSource ?? "";
  const marketMeta = result ? `${result.strategy.symbol} · ${result.strategy.timeframe}` : "";
  const engineText = result?.engine?.name ?? (hbHealth.reachable ? "hummingbot" : "local");

  const runTone: Tone = running
    ? "warn"
    : error
      ? "danger"
      : result
        ? "ok"
        : "warn";
  const runText = running
    ? "running"
    : error
      ? "failed"
      : result
        ? "complete"
        : "sample";

  const engineTone: Tone = engineText === "hummingbot" ? "ok" : "warn";

  return (
    <main className="app-shell">
      <TopBar
        hbHealth={hbHealth}
        llmSettings={llmSettings}
        hbAuth={hbAuth}
        onLlmSave={onLlmSave}
        onHbAuthSave={onHbAuthSave}
      />
      <div className="workspace-grid">
        <ControlPanel
          strategyText={strategyText}
          onStrategyTextChange={setStrategyText}
          activePreset={activePreset}
          onPresetChange={onPresetChange}
          onRun={handleRunDemo}
          running={running}
          error={error}
          strategy={result?.strategy ?? null}
          runTone={runTone}
          runText={runText}
        />
        <div className="main-panel">
          <MetricsGrid backtest={backtest} />
          <EquityChart
            equityCurve={backtest?.equityCurve ?? []}
            marketMeta={marketMeta}
            engineText={engineText}
            engineTone={engineTone}
            dataSource={dataSource}
            dataSourceTone={sourceTone(dataSource)}
          />
          <div className="detail-grid">
            <RiskPanel risk={risk} />
            <ProofPanel proof={proof} />
          </div>
          <OrdersTable logs={executionLogs} />
          <HbControllerPanel controller={controller} hbReachable={hbHealth.reachable} />
          <HbBotPanel bot={bot} controller={controller} hbReachable={hbHealth.reachable} />
          <HbApiDebugPanel />
        </div>
      </div>
    </main>
  );
}
