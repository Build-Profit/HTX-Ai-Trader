export type Tone = "neutral" | "ok" | "warn" | "danger";

export function statusClassName(tone: Tone): string {
  return `status-pill ${tone}`;
}

export function formatPercent(value: number | undefined | null): string {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return "--";
  }
  const number = Number(value);
  const sign = number > 0 ? "+" : "";
  return `${sign}${number.toFixed(2)}%`;
}

export function formatNumber(value: number | undefined | null, digits = 2): string {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return "--";
  }
  return Number(value).toFixed(digits);
}

export function shortHash(value: string | undefined | null): string {
  if (!value) {
    return "--";
  }
  const text = String(value);
  return `${text.slice(0, 12)}...${text.slice(-10)}`;
}

export function riskTone(level: string | undefined): Tone {
  if (level === "low") return "ok";
  if (level === "high") return "danger";
  return "warn";
}

export function sourceTone(source: string | undefined): Tone {
  if (source === "htx_live" || source === "hummingbot") return "ok";
  if (source === "htx_cached" || source === "local_sample" || source === "local_sample_preview") return "warn";
  return "neutral";
}

export function botStatusTone(status: string | undefined): Tone {
  const s = status || "";
  if (["running", "started", "online", "success"].includes(s)) return "ok";
  if (["starting", "deploying", "stopping"].includes(s)) return "warn";
  if (["stopped", "archived", "ended"].includes(s)) return "neutral";
  if (["failed", "error"].includes(s)) return "danger";
  return "neutral";
}
