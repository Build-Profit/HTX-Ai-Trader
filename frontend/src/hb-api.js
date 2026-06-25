export async function checkHbHealth(apiBase) {
  const response = await fetch(`${trimApiBase(apiBase)}/api/hb/health`);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `HB health check failed: ${response.status}`);
  }
  return payload;
}

export async function deployBot(apiBase, { controller, botName, paperTrade = true }) {
  const response = await fetch(`${trimApiBase(apiBase)}/api/hb/bot/deploy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ controller, botName, paperTrade }),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `Bot deploy failed: ${response.status}`);
  }
  return payload;
}

export async function getBotStatus(apiBase, botId) {
  const response = await fetch(`${trimApiBase(apiBase)}/api/hb/bot/${encodeURIComponent(botId)}/status`);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `Bot status failed: ${response.status}`);
  }
  return payload;
}

export async function stopBot(apiBase, botId) {
  const response = await fetch(`${trimApiBase(apiBase)}/api/hb/bot/${encodeURIComponent(botId)}/stop`, {
    method: "POST",
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `Bot stop failed: ${response.status}`);
  }
  return payload;
}

export async function getPortfolio(apiBase) {
  const response = await fetch(`${trimApiBase(apiBase)}/api/hb/portfolio`);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `Portfolio fetch failed: ${response.status}`);
  }
  return payload;
}

export async function runHbBacktest(apiBase, { controller, limit, feeRate } = {}) {
  const response = await fetch(`${trimApiBase(apiBase)}/api/hb/backtest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ controller, limit, feeRate }),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `HB backtest failed: ${response.status}`);
  }
  return payload;
}

function trimApiBase(value) {
  return String(value || "http://127.0.0.1:8000").replace(/\/+$/, "");
}
