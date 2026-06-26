import { formatNumber } from "../lib/format";
import type { ExecutionLog } from "../types";

interface Props {
  logs: ExecutionLog[];
}

export function OrdersTable({ logs }: Props) {
  return (
    <section className="table-section">
      <div className="panel-head">
        <h2>Simulated Orders</h2>
        <span className="mono-chip">{logs.length} logs</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Event</th>
              <th>Status</th>
              <th>Price</th>
              <th>Qty</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty-cell">No simulated order logs</td>
              </tr>
            ) : (
              logs.map((log, i) => (
                <tr key={i}>
                  <td>{log.timestamp}</td>
                  <td>{log.event}</td>
                  <td>{log.status}</td>
                  <td>{formatNumber(log.price, 2)}</td>
                  <td>{formatNumber(log.quantity, 8)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
