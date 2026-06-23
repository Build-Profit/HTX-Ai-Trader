from fastapi import APIRouter, HTTPException

from app.services.demo_runner import run_demo


router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/run")
def run(payload: dict):
    try:
        text = str(payload.get("text") or "Use 1000 USDT on BTC/USDT. Buy when BTC drops 5%, take profit at 10%, stop loss at 3%, and keep max drawdown under 5%.")
        return run_demo(text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
