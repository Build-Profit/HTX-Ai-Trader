import { useState } from "react";
import { runHbBacktest } from "../api/hb";
import { statusClassName, type Tone } from "../lib/format";
import type { ControllerConfig } from "../types";

interface Props {
  controller: ControllerConfig | null;
  hbReachable: boolean;
}

interface HbBacktestState {
  loading: boolean;
  result: unknown;
  error: string | null;
}

export function HbControllerPanel({ controller, hbReachable }: Props) {
  const by = controller?.generatedBy ?? "--";
  const byTone: Tone = by === "llm" ? "ok" : by === "rules" ? "warn" : "neutral";
  const configEntries = controller?.config ? Object.entries(controller.config) : [];

  const [bt, setBt] = useState<HbBacktestState>({ loading: false, result: null, error: null });
  const [showResult, setShowResult] = useState(false);

  const runDisabled = !hbReachable || !controller || bt.loading;

  const onRunHbBacktest = async () => {
    if (!controller) return;
    setBt({ loading: true, result: null, error: null });
    setShowResult(true);
    try {
      const result = await runHbBacktest({
        controller_type: controller.controllerType,
        controller_name: controller.controllerName,
        config: controller.config,
      });
      setBt({ loading: false, result, error: null });
    } catch (err) {
      setBt({
        loading: false,
        result: null,
        error: err instanceof Error ? err.message : String(err),
      });
    }
  };

  return (
    <section className="info-panel controller-panel">
      <div className="panel-head tight">
        <h2>Hummingbot Controller</h2>
        <span className={`${statusClassName(byTone)} ${by === "llm" ? "badge-llm" : by === "rules" ? "badge-rules" : ""}`}>
          {by}
        </span>
      </div>
      <dl className="param-list">
        <div>
          <dt>Controller</dt>
          <dd>{controller?.controllerName ?? "--"}</dd>
        </div>
        <div>
          <dt>Type</dt>
          <dd>{controller?.controllerType ?? "--"}</dd>
        </div>
      </dl>
      <h3 className="config-title">Config</h3>
      <dl className="param-list config-list">
        {configEntries.length === 0 ? (
          <div><dt>—</dt><dd>No config</dd></div>
        ) : (
          configEntries.map(([key, value]) => (
            <div key={key}>
              <dt>{key}</dt>
              <dd>{formatConfigValue(value)}</dd>
            </div>
          ))
        )}
      </dl>
      <div className="hb-backtest-row">
        <button
          className="primary-button compact"
          type="button"
          disabled={runDisabled}
          onClick={onRunHbBacktest}
        >
          {bt.loading ? "Running…" : "Run HB Backtest"}
        </button>
        {bt.result !== null && (
          <button
            className="icon-button"
            type="button"
            title={showResult ? "Hide" : "Show"}
            onClick={() => setShowResult((v) => !v)}
          >
            {showResult ? "▾" : "▸"}
          </button>
        )}
      </div>
      {showResult && (bt.loading || bt.result !== null || bt.error) && (
        <div className="hb-backtest-result">
          {bt.error ? (
            <div className="error-box">{bt.error}</div>
          ) : bt.loading ? (
            <p className="subline">Waiting for Hummingbot backtest…</p>
          ) : (
            <pre>{typeof bt.result === "string" ? bt.result : JSON.stringify(bt.result, null, 2)}</pre>
          )}
        </div>
      )}
      {controller?.warnings && controller.warnings.length > 0 && (
        <div className="warnings">
          {controller.warnings.map((w, i) => (
            <p key={i} className="warning-line">{w}</p>
          ))}
        </div>
      )}
    </section>
  );
}

function formatConfigValue(value: unknown): string {
  if (value === null || value === undefined) return "--";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
