export function setStatus(element, text, tone = "neutral") {
  element.textContent = text;
  element.className = `status-pill ${tone}`;
}

export function formatPercent(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return "--";
  }
  const number = Number(value);
  const sign = number > 0 ? "+" : "";
  return `${sign}${number.toFixed(2)}%`;
}

export function formatNumber(value, digits = 2) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return "--";
  }
  return Number(value).toFixed(digits);
}

export function shortHash(value) {
  if (!value) {
    return "--";
  }
  const text = String(value);
  return `${text.slice(0, 12)}...${text.slice(-10)}`;
}
