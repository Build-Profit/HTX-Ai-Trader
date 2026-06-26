import { botStatusTone, formatNumber, statusClassName } from "../lib/format";
import type { ControllerConfig } from "../types";
import type { BotState } from "../hooks/useBotPolling";

interface Props {
  bot: BotState;
  controller: ControllerConfig | null;
  hbReachable: boolean;
}

export function HbBotPanel({ bot, controller, hbReachable }: Props) {
  const deployDisabled = !hbReachable || !controller || bot.deploying || bot.stopping;
  const stopDisabled = !bot.botId || bot.stopping;

  return (
    <section className="table-section bot-panel">
      <div className="panel-head">
        <div>
          <h2>Paper Trade Bot</h2>
          <p className="subline">Deploy the current controller as a Hummingbot paper trade bot</p>
        </div>
        <div className="head-pills">
          <button
            className="primary-button compact"
            type="button"
            disabled={deployDisabled}
            onClick={() => controller && bot.deploy(controller, `pp_${Date.now()}`)}
          >
            Deploy
          </button>
          <button
            className="primary-button compact"
            type="button"
            disabled={stopDisabled}
            onClick={() => bot.stop()}
          >
            Stop
          </button>
        </div>
      </div>
      <dl className="param-list head-row">
        <div>
          <dt>Bot ID</dt>
          <dd>{bot.botId ?? "--"}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd><span className={statusClassName(botStatusTone(bot.status))}>{bot.status}</span></dd>
        </div>
        <div>
          <dt>Executors</dt>
          <dd>{bot.executors.length}</dd>
        </div>
      </dl>
      {bot.error && <div className="error-box">{bot.error}</div>}
      <div className="bot-grid">
        <div className="bot-block">
          <div className="panel-head tight sub">
            <h3>Positions</h3>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Amount</th>
                  <th>Side</th>
                </tr>
              </thead>
              <tbody>
                {bot.positions.length === 0 ? (
                  <tr><td colSpan={3} className="empty-cell">No positions</td></tr>
                ) : (
                  bot.positions.map((p, i) => (
                    <tr key={i}>
                      <td>{p.symbol ?? p.trading_pair ?? "--"}</td>
                      <td>{formatNumber(p.amount ?? p.size, 6)}</td>
                      <td>{p.side ?? p.side_code ?? "--"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
        <div className="bot-block">
          <div className="panel-head tight sub">
            <h3>Execution Logs</h3>
            <span className="mono-chip">{bot.logs.length} logs</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Event</th>
                  <th>Detail</th>
                </tr>
              </thead>
              <tbody>
                {bot.logs.length === 0 ? (
                  <tr><td colSpan={3} className="empty-cell">No logs</td></tr>
                ) : (
                  bot.logs.map((l, i) => (
                    <tr key={i}>
                      <td>{l.timestamp}</td>
                      <td>{l.event}</td>
                      <td>{l.status}{l.message ? ` — ${l.message}` : ""}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
