"""Central config: read env vars at call time so tests can monkeypatch."""
import os


def _str(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "y"}


def hummingbot_enabled() -> bool:
    return _bool("HUMMINGBOT_ENABLED", True)


def hummingbot_api_url() -> str:
    return _str("HUMMINGBOT_API_URL", "http://localhost:8000").rstrip("/")


def hummingbot_api_user() -> str:
    return _str("HUMMINGBOT_API_USER", "admin")


def hummingbot_api_password() -> str:
    return _str("HUMMINGBOT_API_PASSWORD", "admin")


def llm_enabled() -> bool:
    return _bool("LLM_ENABLED", True)


def openai_api_key() -> str:
    return _str("OPENAI_API_KEY", "")


def openai_base_url() -> str:
    return _str("OPENAI_BASE_URL", "")


def openai_model() -> str:
    return _str("OPENAI_MODEL", "gpt-4o-mini")
