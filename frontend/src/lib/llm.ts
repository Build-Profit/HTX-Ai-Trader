import type { ControllerConfig, LlmSettings } from "../types";

const LLM_SYSTEM_PROMPT = `You map a natural-language trading prompt to a Hummingbot controller config.

Output ONLY strict JSON matching this shape:
{
  "controllerType": "market_making"|"generic"|"directional_trading",
  "controllerName": "pmm_simple"|"grid_strike"|"bollinger_v1",
  "config": { ...controller params... },
  "warnings": ["..."]
}

Supported controllers and their config schemas:
1) market_making.pmm_simple (keywords: 做市/spread/market making/pmm)
   config: exchange(str, default binance), trading_pair(str "BTC-USDT"),
   buy_spread(decimal, 0.005=0.5%), sell_spread(decimal), order_amount_usd(number),
   leverage(int, 1), stop_loss(decimal, 0.03=3%), take_profit(decimal),
   time_limit(int seconds), cooldown_time(int seconds)
2) generic.grid_strike (keywords: 网格/grid)
   config: exchange, trading_pair, min_price(number|null), max_price(number|null),
   grid_levels(int), order_amount_usd
3) directional_trading.bollinger_v1 (default/keywords: 跌/回调/drop/趋势/bollinger/bb)
   config: exchange, trading_pair, leverage, stop_loss(decimal), take_profit(decimal),
   time_limit(int seconds), trailing_stop_activation_price_delta(decimal),
   trailing_stop_trailing_delta(decimal), order_amount_usd, cooldown_time(int seconds),
   candles_exchange, candles_interval(str "1h"), bb_length(int 20), bb_std(number 2.0),
   bb_long_threshold(decimal 0.0), bb_short_threshold(decimal 1.0)

Rules:
- Percent values in user prompt (e.g. 3%) MUST be converted to decimals (0.03).
- trading_pair uses dash format (BTC-USDT), never slash.
- exchange default "binance", leverage default 1.
- If no clear keyword matches, choose directional_trading.bollinger_v1 and add
  warning "unsupported_scenario_default_bollinger".
- Do not output any text outside the JSON object.`;

export function loadLlmSettings(): LlmSettings | null {
  const baseUrl = localStorage.getItem("profitprince.llm.baseUrl");
  const apiKey = localStorage.getItem("profitprince.llm.apiKey");
  const model = localStorage.getItem("profitprince.llm.model") || "gpt-4o-mini";
  if (!apiKey) return null;
  return { baseUrl: baseUrl || "", apiKey, model };
}

export function saveLlmSettings(settings: LlmSettings): void {
  localStorage.setItem("profitprince.llm.baseUrl", settings.baseUrl);
  localStorage.setItem("profitprince.llm.apiKey", settings.apiKey);
  localStorage.setItem("profitprince.llm.model", settings.model);
}

export async function tryLlm(
  text: string,
  settings: LlmSettings,
): Promise<ControllerConfig | null> {
  try {
    const endpoint = settings.baseUrl
      ? settings.baseUrl.replace(/\/+$/, "") + "/chat/completions"
      : "https://api.openai.com/v1/chat/completions";
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${settings.apiKey}`,
      },
      body: JSON.stringify({
        model: settings.model,
        messages: [
          { role: "system", content: LLM_SYSTEM_PROMPT },
          { role: "user", content: text },
        ],
        temperature: 0.2,
      }),
      signal: AbortSignal.timeout(15000),
    });
    if (!response.ok) return null;
    const data = await response.json();
    const content: string = data?.choices?.[0]?.message?.content ?? "";
    const parsed = parseLlmJson(content);
    if (!parsed || typeof parsed !== "object") return null;
    if (
      !("controllerType" in parsed) ||
      !("controllerName" in parsed) ||
      !("config" in parsed)
    ) {
      return null;
    }
    if (typeof parsed.config !== "object" || parsed.config === null) return null;
    if (!Array.isArray(parsed.warnings)) parsed.warnings = [];
    return parsed as unknown as ControllerConfig;
  } catch {
    return null;
  }
}

function parseLlmJson(content: string): Record<string, unknown> | null {
  let text = content.trim();
  if (text.startsWith("```")) {
    if (text.startsWith("```json")) text = text.slice("```json".length).trim();
    else text = text.slice(3).trim();
    if (text.endsWith("```")) text = text.slice(0, -3).trim();
  }
  try {
    const data = JSON.parse(text);
    return typeof data === "object" && data !== null ? data : null;
  } catch {
    return null;
  }
}
