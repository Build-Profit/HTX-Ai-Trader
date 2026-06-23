from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import backtest, demo, market, proof, risk, strategy, trade


app = FastAPI(title="ProfitPrince HTX-Ai-Trader API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(strategy.router)
app.include_router(market.router)
app.include_router(backtest.router)
app.include_router(risk.router)
app.include_router(trade.router)
app.include_router(proof.router)
app.include_router(demo.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "htx-ai-trader"}
