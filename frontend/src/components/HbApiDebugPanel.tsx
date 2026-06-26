import { useEffect, useState } from "react";
import { clearDebug, subscribeDebug } from "../api/hb";
import type { HbDebugEntry } from "../types";

export function HbApiDebugPanel() {
  const [entries, setEntries] = useState<HbDebugEntry[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => subscribeDebug(setEntries), []);

  return (
    <section className="info-panel debug-panel">
      <div className="panel-head tight">
        <h2>HB API Debug</h2>
        <button className="icon-button" type="button" title="Clear" onClick={() => clearDebug()}>
          ⌫
        </button>
      </div>
      {entries.length === 0 ? (
        <p className="subline">No HB API calls yet. Click ↻ or Run Demo.</p>
      ) : (
        <div className="debug-list">
          {entries.map((e) => (
            <div key={e.id} className={`debug-row ${e.ok ? "ok" : "err"}`}>
              <button
                className="debug-row-head"
                type="button"
                onClick={() => setExpanded(expanded === e.id ? null : e.id)}
              >
                <span className={`debug-status ${e.ok ? "ok" : "err"}`}>{e.status}</span>
                <span className="debug-method">{e.method}</span>
                <span className="debug-path">{e.path}</span>
                <span className="debug-time">{e.timestamp.slice(11, 19)}</span>
              </button>
              {expanded === e.id && (
                <div className="debug-detail">
                  {e.request !== undefined && (
                    <div>
                      <p className="debug-label">Request</p>
                      <pre>{JSON.stringify(e.request, null, 2)}</pre>
                    </div>
                  )}
                  <div>
                    <p className="debug-label">Response{e.error ? ` (error: ${e.error})` : ""}</p>
                    <pre>{typeof e.response === "string" ? e.response : JSON.stringify(e.response, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
