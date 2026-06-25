import { checkHealth, runDemo } from "./api.js";
import { checkHbHealth } from "./hb-api.js";
import { initHbPanel } from "./hb-panel.js";
import { drawEquityChart } from "./charts.js";
import { presets } from "./demo.js";
import { sampleResult } from "./sample-result.js";
import { formatNumber, formatPercent, setStatus, shortHash } from "./ui-state.js";

const elements = {
  apiBase: document.querySelector("#apiBase"),
  healthButton: document.querySelector("#healthButton"),
  healthStatus: document.querySelector("#healthStatus"),
  hbHealthStatus: document.querySelector("#hbHealthStatus"),
  strategyText: document.querySelector("#strategyText"),
  runButton: document.querySelector("#runButton"),
  runState: document.querySelector("#runState"),
  errorBox: document.querySelector("#errorBox"),
  strategyJson: document.querySelector("#strategyJson"),
  strategyVersion: document.querySelector("#strategyVersion"),
  totalReturn: document.querySelector("#totalReturn"),
  buyHold: document.querySelector("#buyHold"),
  winRate: document.querySelector("#winRate"),
  maxDrawdown: document.querySelector("#maxDrawdown"),
  tradeCount: document.querySelector("#tradeCount"),
  marketMeta: document.querySelector("#marketMeta"),
  dataSource: document.querySelector("#dataSource"),
  engineStatus: document.querySelector("#engineStatus"),
  equityChart: document.querySelector("#equityChart"),
  riskLevel: document.querySelector("#riskLevel"),
  riskSummary: document.querySelector("#riskSummary"),
  riskScore: document.querySelector("#riskScore"),
  executionRecommendation: document.querySelector("#executionRecommendation"),
  keyRisk: document.querySelector("#keyRisk"),
  riskSuggestion: document.querySelector("#riskSuggestion"),
  proofVersion: document.querySelector("#proofVersion"),
  strategyHash: document.querySelector("#strategyHash"),
  backtestHash: document.querySelector("#backtestHash"),
  executionHash: document.querySelector("#executionHash"),
  combinedHash: document.querySelector("#combinedHash"),
  ordersBody: document.querySelector("#ordersBody"),
  orderCount: document.querySelector("#orderCount"),
  hbControllerName: document.querySelector("#hbControllerName"),
  hbControllerType: document.querySelector("#hbControllerType"),
  hbGeneratedBy: document.querySelector("#hbGeneratedBy"),
  hbConfigBody: document.querySelector("#hbConfigBody"),
  hbBotDeployBtn: document.querySelector("#hbBotDeployBtn"),
  hbBotStopBtn: document.querySelector("#hbBotStopBtn"),
  hbBotId: document.querySelector("#hbBotId"),
  hbBotStatus: document.querySelector("#hbBotStatus"),
  hbBotExecutors: document.querySelector("#hbBotExecutors"),
  hbBotPositions: document.querySelector("#hbBotPositions"),
  hbBotLogsBody: document.querySelector("#hbBotLogsBody"),
  hbBotLogCount: document.querySelector("#hbBotLogCount"),
};

const hbPanel = initHbPanel({
  apiBaseGetter: () => elements.apiBase.value,
  elements: {
    hbBotDeployBtn: elements.hbBotDeployBtn,
    hbBotStopBtn: elements.hbBotStopBtn,
    hbBotId: elements.hbBotId,
    hbBotStatus: elements.hbBotStatus,
    hbBotExecutors: elements.hbBotExecutors,
    hbBotPositions: elements.hbBotPositions,
    hbBotLogsBody: elements.hbBotLogsBody,
    hbBotLogCount: elements.hbBotLogCount,
  },
  onBotChanged: () => {},
});

let latestResult = null;

bindEvents();
renderResult(sampleResult);
setStatus(elements.runState, "sample", "warn");
setStatus(elements.dataSource, "local_sample_preview", "warn");
queueInitialRefresh();

function bindEvents() {
  elements.healthButton.addEventListener("click", handleHealthCheck);
  elements.runButton.addEventListener("click", handleRunDemo);
  elements.apiBase.addEventListener("change", () => {
    localStorage.setItem("profitprince.apiBase", elements.apiBase.value);
    refreshHbHealth().catch(() => {});
  });

  document.querySelectorAll(".preset").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".preset").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      elements.strategyText.value = presets[button.dataset.preset] || presets.balanced;
    });
  });

  const savedBase = localStorage.getItem("profitprince.apiBase");
  if (savedBase) {
    elements.apiBase.value = savedBase;
  }

  window.addEventListener("resize", () => {
    drawEquityChart(elements.equityChart, latestResult?.backtest?.equityCurve || []);
  });
}

async function handleHealthCheck() {
  setStatus(elements.healthStatus, "checking", "warn");
  setStatus(elements.hbHealthStatus, "checking", "warn");
  try {
    await checkHealth(elements.apiBase.value);
    setStatus(elements.healthStatus, "online", "ok");
  } catch (error) {
    setStatus(elements.healthStatus, "offline", "danger");
    showError(error.message);
  }
  await refreshHbHealth();
}

async function refreshHbHealth() {
  try {
    const hb = await checkHbHealth(elements.apiBase.value);
    updateHbHealth(hb);
  } catch {
    setStatus(elements.hbHealthStatus, "offline", "danger");
    hbPanel.setHbReachable(false);
  }
}

function updateHbHealth(hb) {
  const reachable = !!hb?.reachable;
  const engine = hb?.engine || "local";
  if (!reachable) {
    setStatus(elements.hbHealthStatus, "offline", "danger");
    hbPanel.setHbReachable(false);
    return;
  }
  if (engine === "hummingbot") {
    setStatus(elements.hbHealthStatus, "hummingbot", "ok");
  } else {
    setStatus(elements.hbHealthStatus, "local", "warn");
  }
  hbPanel.setHbReachable(true);
}

async function handleRunDemo() {
  hideError();
  elements.runButton.disabled = true;
  setStatus(elements.runState, "running", "warn");

  try {
    const result = await runDemo(elements.apiBase.value, elements.strategyText.value);
    latestResult = result;
    renderResult(result);
    setStatus(elements.runState, "complete", "ok");
    setStatus(elements.healthStatus, "online", "ok");
  } catch (error) {
    setStatus(elements.runState, "failed", "danger");
    showError(error.message);
  } finally {
    elements.runButton.disabled = false;
  }
}

function queueInitialRefresh() {
  window.setTimeout(async () => {
    refreshHbHealth().catch(() => {});
    try {
      await handleRunDemo();
    } catch {
      setStatus(elements.healthStatus, "offline", "danger");
    }
  }, 250);
}

function renderResult(result) {
  const { strategy, backtest, risk, proof, executionLogs = [], market } = result;
  elements.strategyJson.textContent = JSON.stringify(strategy, null, 2);
  elements.strategyVersion.textContent = strategy.version || "v1";

  elements.totalReturn.textContent = formatPercent(backtest.totalReturnPercent);
  elements.buyHold.textContent = formatPercent(backtest.buyHoldReturnPercent);
  elements.winRate.textContent = formatPercent(backtest.winRatePercent);
  elements.maxDrawdown.textContent = formatPercent(backtest.maxDrawdownPercent);
  elements.tradeCount.textContent = String(backtest.tradeCount ?? "--");

  elements.marketMeta.textContent = marketMetaText(backtest, market);
  setStatus(elements.dataSource, market?.source || backtest.dataSource || "unknown", sourceTone(market?.source || backtest.dataSource));
  drawEquityChart(elements.equityChart, backtest.equityCurve);

  renderEngine(result.engine, result.paperTradeDeployable);
  renderHbController(result.hummingbot);
  hbPanel.setController(result.hummingbot);

  setStatus(elements.riskLevel, risk.riskLevel || "--", riskTone(risk.riskLevel));
  elements.riskSummary.textContent = risk.summary || "--";
  elements.riskScore.textContent = String(risk.riskScore ?? "--");
  elements.executionRecommendation.textContent = risk.executionRecommendation || "--";
  elements.keyRisk.textContent = firstOf(risk.keyRisks);
  elements.riskSuggestion.textContent = firstOf(risk.suggestions);

  elements.proofVersion.textContent = proof.version || "v1";
  elements.strategyHash.textContent = shortHash(proof.strategyHash);
  elements.backtestHash.textContent = shortHash(proof.backtestHash);
  elements.executionHash.textContent = shortHash(proof.executionLogHash);
  elements.combinedHash.textContent = shortHash(proof.combinedHash);

  renderOrders(executionLogs);
}

function renderHbController(hb) {
  if (!hb) {
    elements.hbControllerName.textContent = "--";
    elements.hbControllerType.textContent = "--";
    setStatus(elements.hbGeneratedBy, "--", "neutral");
    elements.hbGeneratedBy.classList.remove("badge-llm", "badge-rules");
    elements.hbConfigBody.innerHTML = '<div><dt>—</dt><dd>No config</dd></div>';
    return;
  }
  elements.hbControllerName.textContent = hb.controllerName || "--";
  elements.hbControllerType.textContent = hb.controllerType || "--";
  const by = hb.generatedBy || "rules";
  setStatus(elements.hbGeneratedBy, by, by === "llm" ? "ok" : "warn");
  elements.hbGeneratedBy.classList.remove("badge-llm", "badge-rules");
  elements.hbGeneratedBy.classList.add(by === "llm" ? "badge-llm" : "badge-rules");
  renderHbConfig(hb.config || {});
}

function renderHbConfig(config) {
  const entries = Object.entries(config || {});
  if (!entries.length) {
    elements.hbConfigBody.innerHTML = '<div><dt>—</dt><dd>No config</dd></div>';
    return;
  }
  elements.hbConfigBody.innerHTML = entries
    .map(
      ([key, value]) => `<div>
      <dt>${escapeHtml(key)}</dt>
      <dd>${escapeHtml(formatConfigValue(value))}</dd>
    </div>`,
    )
    .join("");
}

function formatConfigValue(value) {
  if (value === null || value === undefined) {
    return "--";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function renderEngine(engine, paperTradeDeployable) {
  if (!engine) {
    setStatus(elements.engineStatus, "engine: --", "neutral");
    return;
  }
  const bt = engine.backtest || "local";
  const text = paperTradeDeployable ? `engine: ${bt} · paper: ready` : `engine: ${bt}`;
  setStatus(elements.engineStatus, text, bt === "hummingbot" ? "ok" : "warn");
}

function renderOrders(logs) {
  elements.orderCount.textContent = `${logs.length} logs`;
  if (!logs.length) {
    elements.ordersBody.innerHTML = '<tr><td colspan="5" class="empty-cell">No simulated order logs</td></tr>';
    return;
  }

  elements.ordersBody.innerHTML = logs
    .map(
      (log) => `<tr>
        <td>${escapeHtml(log.timestamp)}</td>
        <td>${escapeHtml(log.event)}</td>
        <td>${escapeHtml(log.status)}</td>
        <td>${formatNumber(log.price, 2)}</td>
        <td>${formatNumber(log.quantity, 8)}</td>
      </tr>`,
    )
    .join("");
}

function showError(message) {
  elements.errorBox.hidden = false;
  elements.errorBox.textContent = message;
}

function hideError() {
  elements.errorBox.hidden = true;
  elements.errorBox.textContent = "";
}

function firstOf(value) {
  if (Array.isArray(value) && value.length) {
    return value[0];
  }
  return "--";
}

function riskTone(level) {
  if (level === "low") {
    return "ok";
  }
  if (level === "high") {
    return "danger";
  }
  return "warn";
}

function sourceTone(source) {
  if (source === "htx_live") {
    return "ok";
  }
  if (source === "htx_cached" || source === "local_sample" || source === "local_sample_preview") {
    return "warn";
  }
  return "neutral";
}

function marketMetaText(backtest, market) {
  const parts = [`${backtest.symbol} ${backtest.timeframe}`, `final equity ${formatNumber(backtest.finalEquity)} USDT`];
  if (market?.source === "htx_cached" && market?.metadata?.fetchedAt) {
    parts.push(`Last HTX snapshot: ${formatSnapshotTime(market.metadata.fetchedAt)}`);
  }
  return parts.join(" · ");
}

function formatSnapshotTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  const year = date.getUTCFullYear();
  const month = pad2(date.getUTCMonth() + 1);
  const day = pad2(date.getUTCDate());
  const hours = pad2(date.getUTCHours());
  const minutes = pad2(date.getUTCMinutes());
  return `${year}-${month}-${day} ${hours}:${minutes} UTC`;
}

function pad2(value) {
  return String(value).padStart(2, "0");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
