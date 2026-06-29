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

  const [engine, setEngine] = useState<string>("local");
  const probe = useCallback(async () => {
    setChecking(true);
    setError(null);
    try {
      const info = await checkHbHealth();
      setReachable(info.reachable);
      setEngine(info.engine);
    } catch (err) {
      setReachable(false);
      setEngine("local");
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
    engine,
    checking,
    error,
    refresh: () => void probe(),
  };
}
