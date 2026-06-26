import { useCallback, useEffect, useState } from "react";
import { checkHbHealth } from "../api/hb";

export interface HbHealthState {
  reachable: boolean;
  engine: string;
  checking: boolean;
  error: string | null;
  refresh: () => void;
}

export function useHbHealth(): HbHealthState {
  const [reachable, setReachable] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const probe = useCallback(async () => {
    setChecking(true);
    setError(null);
    try {
      await checkHbHealth();
      setReachable(true);
    } catch (err) {
      setReachable(false);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setChecking(false);
    }
  }, []);

  useEffect(() => {
    void probe();
    const handle = window.setInterval(() => void probe(), 30000);
    return () => window.clearInterval(handle);
  }, [probe]);

  return {
    reachable,
    engine: reachable ? "hummingbot" : "local",
    checking,
    error,
    refresh: () => void probe(),
  };
}
