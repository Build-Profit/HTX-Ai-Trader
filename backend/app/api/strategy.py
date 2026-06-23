from fastapi import APIRouter, HTTPException

from app.services.strategy_parser import parse_strategy_payload


router = APIRouter(prefix="/api/strategy", tags=["strategy"])


@router.post("/parse")
def parse_strategy(payload: dict):
    try:
        return parse_strategy_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
