import { shortHash } from "../lib/format";
import type { ProofRecord } from "../types";

interface Props {
  proof: ProofRecord | null;
}

export function ProofPanel({ proof }: Props) {
  return (
    <article className="info-panel">
      <div className="panel-head tight">
        <h2>Proof</h2>
        <span className="mono-chip">{proof?.version ?? "v1"}</span>
      </div>
      <dl className="hash-list">
        <div>
          <dt>Strategy</dt>
          <dd>{proof ? shortHash(proof.strategyHash) : "--"}</dd>
        </div>
        <div>
          <dt>Backtest</dt>
          <dd>{proof ? shortHash(proof.backtestHash) : "--"}</dd>
        </div>
        <div>
          <dt>Execution</dt>
          <dd>{proof ? shortHash(proof.executionLogHash) : "--"}</dd>
        </div>
        <div>
          <dt>Combined</dt>
          <dd>{proof ? shortHash(proof.combinedHash) : "--"}</dd>
        </div>
      </dl>
    </article>
  );
}
