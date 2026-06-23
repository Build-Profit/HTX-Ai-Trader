export async function checkHealth(apiBase) {
  const response = await fetch(`${trimApiBase(apiBase)}/api/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

export async function runDemo(apiBase, text) {
  const response = await fetch(`${trimApiBase(apiBase)}/api/demo/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail || `Demo run failed: ${response.status}`;
    throw new Error(detail);
  }
  return payload;
}

function trimApiBase(value) {
  return String(value || "http://127.0.0.1:8000").replace(/\/+$/, "");
}
