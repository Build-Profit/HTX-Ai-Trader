import { statusClassName, type Tone } from "../lib/format";
import type { ControllerConfig } from "../types";

interface Props {
  controller: ControllerConfig | null;
}

export function HbControllerPanel({ controller }: Props) {
  const by = controller?.generatedBy ?? "--";
  const byTone: Tone = by === "llm" ? "ok" : by === "rules" ? "warn" : "neutral";
  const configEntries = controller?.config ? Object.entries(controller.config) : [];

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
