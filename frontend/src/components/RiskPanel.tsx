import { riskTone, statusClassName } from "../lib/format";
import type { RiskReport } from "../types";

interface Props {
  risk: RiskReport | null;
}

export function RiskPanel({ risk }: Props) {
  if (!risk) {
    return (
      <article className="info-panel">
        <div className="panel-head tight">
          <h2>AI Risk</h2>
          <span className="status-pill neutral">--</span>
        </div>
        <p className="risk-summary">--</p>
      </article>
    );
  }
  const first = <T,>(arr: T[]) => (arr.length ? arr[0] : "--");
  return (
    <article className="info-panel">
      <div className="panel-head tight">
        <h2>AI Risk</h2>
        <span className={statusClassName(riskTone(risk.riskLevel))}>{risk.riskLevel}</span>
      </div>
      <p className="risk-summary">{risk.summary}</p>
      <dl className="risk-list">
        <div>
          <dt>Score</dt>
          <dd>{risk.riskScore}</dd>
        </div>
        <div>
          <dt>Recommendation</dt>
          <dd>{risk.executionRecommendation}</dd>
        </div>
        <div>
          <dt>Key Risk</dt>
          <dd>{first(risk.keyRisks)}</dd>
        </div>
        <div>
          <dt>Next Parameter</dt>
          <dd>{first(risk.suggestions)}</dd>
        </div>
      </dl>
    </article>
  );
}
