import { useCallback, useEffect, useRef, useState } from "react";
import { deployBot, getBotStatus, stopBot } from "../api/hb";
import type { ControllerConfig, HbBotStatus } from "../types";

const TERMINAL_STATUSES = ["stopped", "archived", "failed", "error", "ended"];
const POLL_INTERVAL_MS = 3000;

export interface BotState {
  botId: string | null;
  status: string;
  executors: unknown[];
  positions: HbBotStatus["positions"];
  logs: HbBotStatus["executionLogs"];
  deploying: boolean;
  stopping: boolean;
  error: string | null;
  deploy: (controller: ControllerConfig, botName: string) => Promise<void>;
  stop: () => Promise<void>;
}

export function useBotPolling(): BotState {
  const [botId, setBotId] = useState<string | null>(null);
  const [status, setStatus] = useState("idle");
  const [executors, setExecutors] = useState<unknown[]>([]);
  const [positions, setPositions] = useState<HbBotStatus["positions"]>([]);
  const [logs, setLogs] = useState<HbBotStatus["executionLogs"]>([]);
  const [deploying, setDeploying] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollHandle = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (pollHandle.current !== null) {
      window.clearInterval(pollHandle.current);
      pollHandle.current = null;
    }
  }, []);

  const pollOnce = useCallback(
    async (name: string) => {
      try {
        const result = await getBotStatus(name);
        setBotId(result.botId);
        setStatus(result.status);
        setExecutors(result.executors);
        setPositions(result.positions);
        setLogs(result.executionLogs);
        if (TERMINAL_STATUSES.includes(result.status)) {
          stopPolling();
        }
      } catch {
        // transient: keep polling
      }
    },
    [stopPolling],
  );

  const startPolling = useCallback(
    (name: string) => {
      stopPolling();
      pollHandle.current = window.setInterval(() => void pollOnce(name), POLL_INTERVAL_MS);
      void pollOnce(name);
    },
    [pollOnce, stopPolling],
  );

  useEffect(() => () => stopPolling(), [stopPolling]);

  const deploy = useCallback(
    async (controller: ControllerConfig, botName: string) => {
      setDeploying(true);
      setError(null);
      setStatus("deploying");
      try {
        const result = await deployBot(controller, botName);
        setBotId(result.botId);
        setStatus(result.status);
        startPolling(result.botId || botName);
      } catch (err) {
        setStatus("failed");
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setDeploying(false);
      }
    },
    [startPolling],
  );

  const stop = useCallback(async () => {
    if (!botId) return;
    setStopping(true);
    setError(null);
    setStatus("stopping");
    try {
      const result = await stopBot(botId);
      setStatus(result.status);
      stopPolling();
    } catch (err) {
      setStatus("stop_failed");
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setStopping(false);
    }
  }, [botId, stopPolling]);

  return {
    botId,
    status,
    executors,
    positions,
    logs,
    deploying,
    stopping,
    error,
    deploy,
    stop,
  };
}
