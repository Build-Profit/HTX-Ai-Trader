import { deployBot, getBotStatus, stopBot } from "./hb-api.js";
import { formatNumber, setStatus } from "./ui-state.js";

const TERMINAL_STATUSES = ["stopped", "archived", "failed", "error", "ended"];
const POLL_INTERVAL_MS = 3000;

export function initHbPanel({ apiBaseGetter, elements, onBotChanged } = {}) {
  let currentController = null;
  let botId = null;
  let pollHandle = null;
  let deploying = false;
  let hbReachable = false;

  function setController(controller) {
    currentController = controller || null;
    refreshDeployEnabled();
  }

  function setHbReachable(reachable) {
    hbReachable = !!reachable;
    refreshDeployEnabled();
    if (!hbReachable) {
      showOffline();
    } else if (!botId) {
      resetIdle();
    }
  }

  function refreshDeployEnabled() {
    elements.hbBotDeployBtn.disabled = !hbReachable || !currentController || deploying;
  }

  function showOffline() {
    setStatus(elements.hbBotStatus, "Hummingbot offline", "danger");
    elements.hbBotId.textContent = "--";
    elements.hbBotExecutors.textContent = "0";
    elements.hbBotPositions.innerHTML = '<tr><td colspan="3" class="empty-cell">Hummingbot offline</td></tr>';
    elements.hbBotLogsBody.innerHTML = '<tr><td colspan="3" class="empty-cell">No logs</td></tr>';
    elements.hbBotLogCount.textContent = "0 logs";
    elements.hbBotStopBtn.disabled = true;
  }

  function resetIdle() {
    setStatus(elements.hbBotStatus, "idle", "neutral");
    elements.hbBotId.textContent = "--";
    elements.hbBotExecutors.textContent = "0";
    elements.hbBotPositions.innerHTML = '<tr><td colspan="3" class="empty-cell">No positions</td></tr>';
    elements.hbBotLogsBody.innerHTML = '<tr><td colspan="3" class="empty-cell">No logs</td></tr>';
    elements.hbBotLogCount.textContent = "0 logs";
    elements.hbBotStopBtn.disabled = true;
  }

  async function handleDeploy() {
    if (!currentController || deploying || !hbReachable) return;
    deploying = true;
    refreshDeployEnabled();
    setStatus(elements.hbBotStatus, "deploying", "warn");

    const botName = `pp_${Date.now()}`;
    try {
      const result = await deployBot(apiBaseGetter(), {
        controller: currentController,
        botName,
        paperTrade: true,
      });
      botId = result.botId;
      elements.hbBotId.textContent = botId || "--";
      setStatus(elements.hbBotStatus, result.status || "starting", "warn");
      elements.hbBotStopBtn.disabled = false;
      if (typeof onBotChanged === "function") onBotChanged(botId, "deployed");
      startPolling();
    } catch (error) {
      setStatus(elements.hbBotStatus, "failed", "danger");
      elements.hbBotLogsBody.innerHTML = `<tr><td colspan="3" class="empty-cell">${escapeHtml(error.message)}</td></tr>`;
      elements.hbBotLogCount.textContent = "0 logs";
    } finally {
      deploying = false;
      refreshDeployEnabled();
    }
  }

  async function handleStop() {
    if (!botId) return;
    elements.hbBotStopBtn.disabled = true;
    setStatus(elements.hbBotStatus, "stopping", "warn");
    try {
      const result = await stopBot(apiBaseGetter(), botId);
      setStatus(elements.hbBotStatus, result.status || "stopped", "ok");
      if (typeof onBotChanged === "function") onBotChanged(botId, "stopped");
      stopPolling();
    } catch (error) {
      setStatus(elements.hbBotStatus, "stop_failed", "danger");
      elements.hbBotLogsBody.innerHTML = `<tr><td colspan="3" class="empty-cell">${escapeHtml(error.message)}</td></tr>`;
    } finally {
      elements.hbBotStopBtn.disabled = false;
    }
  }

  function startPolling() {
    stopPolling();
    pollHandle = window.setInterval(pollOnce, POLL_INTERVAL_MS);
    pollOnce();
  }

  function stopPolling() {
    if (pollHandle) {
      window.clearInterval(pollHandle);
      pollHandle = null;
    }
  }

  async function pollOnce() {
    if (!botId) return;
    try {
      const status = await getBotStatus(apiBaseGetter(), botId);
      renderStatus(status);
      if (typeof onBotChanged === "function") onBotChanged(botId, status.status);
      if (TERMINAL_STATUSES.includes(status.status)) {
        stopPolling();
      }
    } catch {
      // transient errors: keep polling so the panel recovers when HB comes back
    }
  }

  function renderStatus(status) {
    setStatus(elements.hbBotStatus, status.status || "running", statusTone(status.status));
    elements.hbBotId.textContent = status.botId || botId || "--";
    const executors = Array.isArray(status.executors) ? status.executors : [];
    elements.hbBotExecutors.textContent = String(executors.length);
    renderPositions(status.positions || []);
    renderLogs(status.executionLogs || []);
  }

  function renderPositions(positions) {
    if (!positions.length) {
      elements.hbBotPositions.innerHTML = '<tr><td colspan="3" class="empty-cell">No positions</td></tr>';
      return;
    }
    elements.hbBotPositions.innerHTML = positions
      .map(
        (p) => `<tr>
        <td>${escapeHtml(p.symbol || p.trading_pair || "--")}</td>
        <td>${formatNumber(p.amount ?? p.size, 6)}</td>
        <td>${escapeHtml(p.side || p.side_code || "--")}</td>
      </tr>`,
      )
      .join("");
  }

  function renderLogs(logs) {
    elements.hbBotLogCount.textContent = `${logs.length} logs`;
    if (!logs.length) {
      elements.hbBotLogsBody.innerHTML = '<tr><td colspan="3" class="empty-cell">No logs</td></tr>';
      return;
    }
    elements.hbBotLogsBody.innerHTML = logs
      .map(
        (l) => `<tr>
        <td>${escapeHtml(l.timestamp)}</td>
        <td>${escapeHtml(l.event)}</td>
        <td>${escapeHtml(l.message || l.status || "")}</td>
      </tr>`,
      )
      .join("");
  }

  elements.hbBotDeployBtn.addEventListener("click", handleDeploy);
  elements.hbBotStopBtn.addEventListener("click", handleStop);

  return {
    setController,
    setHbReachable,
    stop: stopPolling,
  };
}

function statusTone(status) {
  if (status === "running" || status === "started" || status === "online") {
    return "ok";
  }
  if (status === "starting" || status === "deploying" || status === "stopping") {
    return "warn";
  }
  if (status === "stopped" || status === "archived" || status === "ended") {
    return "neutral";
  }
  if (status === "failed" || status === "error") {
    return "danger";
  }
  return "neutral";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
