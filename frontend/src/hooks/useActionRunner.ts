import { useState } from "react";

import { ApiRequestError } from "../api/client";

export interface ActionRunner {
  busy: boolean;
  lastError: string | null;
  actionLog: string[];
  setLastError: (value: string | null) => void;
  pushLog: (message: string) => void;
  runAction: (label: string, callback: () => Promise<void>) => Promise<void>;
}

export function useActionRunner(): ActionRunner {
  const [busy, setBusy] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);
  const [actionLog, setActionLog] = useState<string[]>([]);

  function pushLog(message: string): void {
    setActionLog((previous) => [new Date().toISOString() + " | " + message, ...previous].slice(0, 40));
  }

  async function runAction(label: string, callback: () => Promise<void>): Promise<void> {
    setBusy(true);
    setLastError(null);
    try {
      await callback();
      pushLog(`${label}: success`);
    } catch (error) {
      const message = formatError(error);
      setLastError(message);
      pushLog(`${label}: ${message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    busy,
    lastError,
    actionLog,
    setLastError,
    pushLog,
    runAction,
  };
}

function formatError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    return `[${error.status}] ${error.message}`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Unexpected error";
}

