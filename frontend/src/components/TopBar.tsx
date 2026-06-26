import { useState } from "react";
import type { HbAuthSettings, LlmSettings } from "../types";
import type { HbHealthState } from "../hooks/useHbHealth";
import { statusClassName, type Tone } from "../lib/format";

interface Props {
  hbHealth: HbHealthState;
  llmSettings: LlmSettings | null;
  hbAuth: HbAuthSettings;
  onLlmSave: (s: LlmSettings) => void;
  onHbAuthSave: (s: HbAuthSettings) => void;
}

export function TopBar({ hbHealth, llmSettings, hbAuth, onLlmSave, onHbAuthSave }: Props) {
  const [showSettings, setShowSettings] = useState(false);

  const hbTone: Tone = hbHealth.reachable ? "ok" : hbHealth.checking ? "warn" : "danger";
  const hbText = hbHealth.reachable
    ? "hummingbot"
    : hbHealth.checking
      ? "checking"
      : "offline";

  return (
    <section className="topbar">
      <div>
        <p className="eyebrow">HTX-Ai-Trader</p>
        <h1>ProfitPrince Strategy Console</h1>
      </div>
      <div className="connection-panel">
        <span className="pill-label">Hummingbot API (localhost:8000)</span>
        <span className={statusClassName(hbTone)}>{hbText}</span>
        <button
          className="icon-button"
          type="button"
          title="Refresh HB health"
          aria-label="Refresh HB health"
          onClick={() => hbHealth.refresh()}
        >
          ↻
        </button>
        <button
          className="icon-button"
          type="button"
          title="Settings"
          aria-label="Settings"
          onClick={() => setShowSettings((v) => !v)}
        >
          ⚙
        </button>
      </div>
      {showSettings && (
        <SettingsPopover
          llmSettings={llmSettings}
          hbAuth={hbAuth}
          onLlmSave={onLlmSave}
          onHbAuthSave={onHbAuthSave}
          onClose={() => setShowSettings(false)}
        />
      )}
    </section>
  );
}

function SettingsPopover({
  llmSettings,
  hbAuth,
  onLlmSave,
  onHbAuthSave,
  onClose,
}: {
  llmSettings: LlmSettings | null;
  hbAuth: HbAuthSettings;
  onLlmSave: (s: LlmSettings) => void;
  onHbAuthSave: (s: HbAuthSettings) => void;
  onClose: () => void;
}) {
  const [baseUrl, setBaseUrl] = useState(llmSettings?.baseUrl ?? "");
  const [apiKey, setApiKey] = useState(llmSettings?.apiKey ?? "");
  const [model, setModel] = useState(llmSettings?.model ?? "gpt-4o-mini");
  const [user, setUser] = useState(hbAuth.user);
  const [password, setPassword] = useState(hbAuth.password);

  return (
    <div className="settings-popover">
      <div className="panel-head tight">
        <h2>Settings</h2>
        <button className="icon-button" type="button" onClick={onClose}>✕</button>
      </div>
      <fieldset>
        <legend>Hummingbot Auth (Basic)</legend>
        <label className="field compact">
          <span>User</span>
          <input value={user} onChange={(e) => setUser(e.target.value)} />
        </label>
        <label className="field compact">
          <span>Password</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button
          className="primary-button compact"
          type="button"
          onClick={() => onHbAuthSave({ user, password })}
        >
          Save HB Auth
        </button>
      </fieldset>
      <fieldset>
        <legend>LLM (optional, OpenAI-compatible)</legend>
        <label className="field compact">
          <span>Base URL</span>
          <input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} placeholder="https://api.openai.com/v1" />
        </label>
        <label className="field compact">
          <span>API Key</span>
          <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} />
        </label>
        <label className="field compact">
          <span>Model</span>
          <input value={model} onChange={(e) => setModel(e.target.value)} />
        </label>
        <button
          className="primary-button compact"
          type="button"
          onClick={() => onLlmSave({ baseUrl, apiKey, model })}
        >
          Save LLM
        </button>
      </fieldset>
    </div>
  );
}
