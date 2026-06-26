import type { ProofRecord } from "../types";

export function canonicalJson(value: unknown): string {
  return JSON.stringify(sortKeys(value));
}

function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === "object") {
    const sorted: Record<string, unknown> = {};
    for (const key of Object.keys(value as Record<string, unknown>).sort()) {
      sorted[key] = sortKeys((value as Record<string, unknown>)[key]);
    }
    return sorted;
  }
  return value;
}

export async function sha256Hex(value: unknown): Promise<string> {
  const text = canonicalJson(value);
  const buffer = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export async function generateProof(
  strategy: unknown,
  backtest: unknown,
  executionLogs: unknown,
  version = "v1",
): Promise<ProofRecord> {
  const [strategyHash, backtestHash, executionHash] = await Promise.all([
    sha256Hex(strategy),
    sha256Hex(backtest),
    sha256Hex(executionLogs),
  ]);
  const combinedHash = await sha256Hex({
    strategyHash,
    backtestHash,
    executionLogHash: executionHash,
    version,
  });
  return {
    version,
    timestamp: new Date().toISOString(),
    strategyHash,
    backtestHash,
    executionLogHash: executionHash,
    combinedHash,
  };
}
