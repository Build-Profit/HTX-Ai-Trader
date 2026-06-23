from fastapi import APIRouter, HTTPException

from app.services.proof_hasher import generate_proof


router = APIRouter(prefix="/api/proof", tags=["proof"])


@router.post("/hash")
def hash_proof(payload: dict):
    try:
        proof = generate_proof(
            payload["strategy"],
            payload["backtest"],
            payload.get("executionLogs", []),
            version=str(payload.get("version", "v1")),
        )
        return proof.to_dict()
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
