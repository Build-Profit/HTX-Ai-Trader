from fastapi import APIRouter, HTTPException

from app.services.ai_strategy_agent import generate_controller
from app.services.strategy_parser import parse_strategy_payload


router = APIRouter(prefix="/api/strategy", tags=["strategy"])


@router.post("/parse")
def parse_strategy(payload: dict):
    try:
        result = parse_strategy_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    text = str(result.get("input") or payload.get("text") or "")
    default_symbol = str(payload.get("symbol") or "BTC/USDT")
    try:
        result["hummingbot"] = generate_controller(text, default_symbol=default_symbol)
    except Exception as exc:  # Defensive: never break /parse on AI agent error.
        result["hummingbot"] = {
            "controllerType": None,
            "controllerName": None,
            "config": {},
            "generatedBy": "rules",
            "warnings": [f"ai_agent_error: {exc}"],
        }
    return result
