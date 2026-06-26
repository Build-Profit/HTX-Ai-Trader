import type { HbAuthSettings, HbBotStatus, HbDebugEntry, HbPosition, Kline } from "../types";

export class HbApiError extends Error {
  status: number | string;
  body: unknown;
  constructor(message: string, status: number | string, body: unknown) {
    super(message);
    this.name = "HbApiError";
    this.status = status;
    this.body = body;
  }
}

const PROXY_PREFIX = "/hbapi";
const MAX_DEBUG = 30;

let debugLog: HbDebugEntry[] = [];
let debugId = 0;
const debugListeners = new Set<(entries: HbDebugEntry[]) => void>();

export function subscribeDebug(fn: (entries: HbDebugEntry[]) => void): () => void {
  debugListeners.add(fn);
  fn(debugLog);
  return () => {
    debugListeners.delete(fn);
  };
}

export function getDebugLog(): HbDebugEntry[] {
  return debugLog;
}

function pushDebug(entry: Omit<HbDebugEntry, "id" | "timestamp">) {
  debugId += 1;
  const full: HbDebugEntry = { ...entry, id: debugId, timestamp: new Date().toISOString() };
  debugLog = [full, ...debugLog].slice(0, MAX_DEBUG);
  for (const fn of debugListeners) fn(debugLog);
}

export function clearDebug(): void {
  debugLog = [];
  for (const fn of debugListeners) fn(debugLog);
}

export function loadHbAuth(): HbAuthSettings {
  return {
    user: localStorage.getItem("profitprince.hb.user") || "admin",
    password: localStorage.getItem("profitprince.hb.password") || "admin",
  };
}

export function saveHbAuth(settings: HbAuthSettings): void {
  localStorage.setItem("profitprince.hb.user", settings.user);
  localStorage.setItem("profitprince.hb.password", settings.password);
}

async function fetchHb<T = unknown>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const auth = loadHbAuth();
  const cred = btoa(`${auth.user}:${auth.password}`);
  const url = `${PROXY_PREFIX}${path}`;
  const init: RequestInit = {
    method,
    headers: {
      Authorization: `Basic ${cred}`,
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  };

  let status: number | string = 0;
  let ok = false;
  let responseParsed: unknown = undefined;
  let errorMsg: string | undefined;

  try {
    const response = await fetch(url, init);
    status = response.status;
    ok = response.ok;
    const text = await response.text();
    try {
      responseParsed = text ? JSON.parse(text) : undefined;
    } catch {
      responseParsed = text;
    }
    if (!response.ok) {
      errorMsg = `HTTP ${response.status}`;
      throw new HbApiError(`HB ${method} ${path} -> ${response.status}`, response.status, responseParsed);
    }
    return responseParsed as T;
  } catch (err) {
    if (!errorMsg) {
      errorMsg = err instanceof Error ? err.message : String(err);
      status = status || "ERR";
    }
    if (err instanceof HbApiError) throw err;
    throw new HbApiError(errorMsg, status, responseParsed);
  } finally {
    pushDebug({
      method,
      path,
      status,
      ok,
      request: body,
      response: responseParsed,
      error: errorMsg,
    });
  }
}

export async function checkHbHealth(): Promise<{ reachable: boolean; raw: unknown }> {
  const raw = await fetchHb<unknown>("GET", "/bot-orchestration/status");
  return { reachable: true, raw };
}

export async function listConnectors(): Promise<string[]> {
  const data = await fetchHb<string[]>("GET", "/connectors/");
  return Array.isArray(data) ? data : [];
}

export async function listControllers(): Promise<Record<string, string[]>> {
  return fetchHb<Record<string, string[]>>("GET", "/controllers/");
}

export async function fetchCandles(
  connectorName: string,
  tradingPair: string,
  interval = "1h",
  maxRecords = 120,
): Promise<Kline[]> {
  const body = { connector_name: connectorName, trading_pair: tradingPair, interval, max_records: maxRecords };
  const data = await fetchHb<unknown>("POST", "/market-data/candles", body);
  return mapCandles(data);
}

function mapCandles(data: unknown): Kline[] {
  const rows: unknown[] = [];
  if (Array.isArray(data)) rows.push(...data);
  else if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>;
    for (const key of ["candles", "data", "klines", "rows"]) {
      if (Array.isArray(obj[key])) {
        rows.push(...(obj[key] as unknown[]));
        break;
      }
    }
  }
  const klines: Kline[] = [];
  for (const row of rows) {
    if (row && typeof row === "object") {
      const r = row as Record<string, unknown>;
      try {
        klines.push({
          timestamp: normalizeTimestamp(r.timestamp ?? r.time),
          open: Number(r.open ?? r.o ?? 0),
          high: Number(r.high ?? r.h ?? 0),
          low: Number(r.low ?? r.l ?? 0),
          close: Number(r.close ?? r.c ?? 0),
          volume: Number(r.volume ?? r.v ?? 0),
        });
      } catch {
        continue;
      }
    } else if (Array.isArray(row) && row.length >= 5) {
      try {
        klines.push({
          timestamp: normalizeTimestamp(row[0]),
          open: Number(row[1]),
          high: Number(row[2]),
          low: Number(row[3]),
          close: Number(row[4]),
          volume: row.length > 5 ? Number(row[5]) : 0,
        });
      } catch {
        continue;
      }
    }
  }
  return klines;
}

function normalizeTimestamp(value: unknown): string {
  if (typeof value === "number") {
    return new Date(value * 1000).toISOString();
  }
  const s = String(value ?? "");
  if (/^\d+(\.\d+)?$/.test(s)) {
    const n = parseFloat(s);
    if (!Number.isNaN(n)) return new Date(n * 1000).toISOString();
  }
  return s;
}

export async function runHbBacktest(controllerConfig: unknown): Promise<unknown> {
  return fetchHb<unknown>("POST", "/backtesting/run", { controller_config: controllerConfig });
}

export async function deployBot(
  controllerConfig: unknown,
  botName: string,
): Promise<{ botId: string; status: string; raw: unknown }> {
  const body = { controller_config: controllerConfig, bot_name: botName, paper_trade: true };
  const data = await fetchHb<Record<string, unknown>>("POST", "/bot-orchestration/deploy-v2-controllers", body);
  return {
    botId: String(data?.bot_name ?? data?.bot_id ?? botName),
    status: String(data?.status ?? "deployed"),
    raw: data,
  };
}

export async function getBotStatus(botName: string): Promise<HbBotStatus> {
  const data = await fetchHb<Record<string, unknown>>("GET", `/bot-orchestration/${encodeURIComponent(botName)}/status`);
  return mapBotStatus(botName, data);
}

function mapBotStatus(botName: string, data: Record<string, unknown> | undefined): HbBotStatus {
  const status = String(data?.status ?? "unknown");
  const executors = Array.isArray(data?.executors) ? (data!.executors as unknown[]) : [];
  const positions: HbPosition[] = Array.isArray(data?.positions)
    ? (data!.positions as HbPosition[])
    : [];
  const logs = Array.isArray(data?.execution_logs)
    ? (data!.execution_logs as Record<string, unknown>[])
    : Array.isArray(data?.executionLogs)
      ? (data!.executionLogs as Record<string, unknown>[])
      : [];
  return {
    botId: botName,
    status,
    executors,
    positions,
    executionLogs: logs.map((l) => ({
      timestamp: String(l.timestamp ?? ""),
      event: String(l.event ?? ""),
      status: String(l.status ?? ""),
      message: l.message ? String(l.message) : undefined,
    })),
    engine: "hummingbot",
  };
}

export async function stopBot(botName: string): Promise<{ botId: string; status: string; raw: unknown }> {
  const data = await fetchHb<Record<string, unknown>>("POST", `/bot-orchestration/stop-and-archive-bot/${encodeURIComponent(botName)}`);
  return {
    botId: botName,
    status: String(data?.status ?? "stopped"),
    raw: data,
  };
}

export async function getPortfolio(): Promise<unknown> {
  return fetchHb<unknown>("POST", "/portfolio/state");
}
