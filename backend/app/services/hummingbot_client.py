"""Sync Hummingbot REST client (httpx + HTTP Basic Auth).

Endpoint paths are best-effort against Hummingbot's REST API; they may need
tuning against a live instance.
"""
from typing import Any, Dict, List, Optional

import httpx

from app.services import config


class HummingbotError(RuntimeError):
    pass


class HummingbotClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 4.0,
    ) -> None:
        self._base_url = (base_url or config.hummingbot_api_url()).rstrip("/")
        self._user = user or config.hummingbot_api_user()
        self._password = password or config.hummingbot_api_password()
        self._timeout = timeout
        self._client = httpx.Client(
            base_url=self._base_url,
            auth=(self._user, self._password),
            timeout=self._timeout,
        )

    def is_reachable(self) -> bool:
        try:
            resp = self._client.get("/connectors", timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    def _request(self, method: str, path: str, **kwargs) -> Any:
        try:
            resp = self._client.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise HummingbotError(f"hummingbot request failed: {exc}") from exc
        if resp.status_code >= 400:
            raise HummingbotError(f"hummingbot {method} {path} -> {resp.status_code}: {resp.text[:200]}")
        try:
            return resp.json()
        except ValueError as exc:
            raise HummingbotError(f"hummingbot returned non-json: {exc}") from exc

    def list_connectors(self) -> List[Dict[str, Any]]:
        data = self._request("GET", "/connectors")
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("connectors"), list):
            return data["connectors"]
        return []

    def get_candles(self, symbol: str, interval: str, max_records: int = 120) -> Dict[str, Any]:
        trading_pair = symbol.replace("/", "-")
        # Path shape per Hummingbot market-data docs; fall back to query params.
        try:
            return self._request(
                "GET",
                f"/market-data/candles/binance/{trading_pair}/{interval}",
                params={"max_records": max_records},
            )
        except HummingbotError:
            return self._request(
                "GET",
                "/market-data/candles",
                params={
                    "connector": "binance",
                    "trading_pair": trading_pair,
                    "interval": interval,
                    "max_records": max_records,
                },
            )

    def run_backtest(self, controller_config: Dict[str, Any], **extra) -> Dict[str, Any]:
        payload = {"controller_config": controller_config, **extra}
        # If /backtesting/start 404s, raise to trigger facade fallback.
        return self._request("POST", "/backtesting/start", json=payload)

    def deploy_bot(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/bot-orchestration/deploy-v2", json=payload)

    def get_bot_status(self, bot_name: str) -> Dict[str, Any]:
        return self._request("GET", f"/bot-orchestration/{bot_name}/status")

    def get_active_bots(self) -> List[Dict[str, Any]]:
        data = self._request("GET", "/bot-orchestration/active")
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("bots"), list):
            return data["bots"]
        return []

    def stop_and_archive_bot(self, bot_name: str) -> Dict[str, Any]:
        return self._request("POST", f"/bot-orchestration/{bot_name}/stop")

    def get_portfolio_state(self) -> Dict[str, Any]:
        return self._request("GET", "/portfolio")


_singleton: Optional[HummingbotClient] = None


def get_client() -> HummingbotClient:
    global _singleton
    if _singleton is None:
        _singleton = HummingbotClient()
    return _singleton


def reset_client() -> None:
    global _singleton
    _singleton = None
