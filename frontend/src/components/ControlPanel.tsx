import { presets } from "../lib/presets";
import { statusClassName, type Tone } from "../lib/format";
import type { Strategy } from "../types";

interface Props {
  strategyText: string;
  onStrategyTextChange: (v: string) => void;
  activePreset: string;
  onPresetChange: (key: string) => void;
  onRun: () => void;
  running: boolean;
  error: string | null;
  strategy: Strategy | null;
  runTone: Tone;
  runText: string;
}

export function ControlPanel({
  strategyText,
  onStrategyTextChange,
  activePreset,
  onPresetChange,
  onRun,
  running,
  error,
  strategy,
  runTone,
  runText,
}: Props) {
  return (
    <aside className="control-panel">
      <div className="panel-head">
        <h2>Strategy</h2>
        <span className={statusClassName(runTone)}>{runText}</span>
      </div>
      <label className="field">
        <span>Prompt</span>
        <textarea
          rows={8}
          value={strategyText}
          onChange={(e) => onStrategyTextChange(e.target.value)}
        />
      </label>
      <div className="preset-row" role="group" aria-label="Prompt presets">
        {Object.keys(presets).map((key) => (
          <button
            key={key}
            className={`preset ${activePreset === key ? "active" : ""}`}
            type="button"
            onClick={() => onPresetChange(key)}
          >
            {key.charAt(0).toUpperCase() + key.slice(1)}
          </button>
        ))}
      </div>
      <button className="primary-button" type="button" onClick={onRun} disabled={running}>
        {running ? "Running…" : "Run Demo"}
      </button>
      {error && <div className="error-box">{error}</div>}
      <div className="json-panel">
        <div className="panel-head tight">
          <h2>Strategy JSON</h2>
          <span className="mono-chip">{strategy?.version ?? "v1"}</span>
        </div>
        <pre>{strategy ? JSON.stringify(strategy, null, 2) : "{}"}</pre>
      </div>
    </aside>
  );
}
