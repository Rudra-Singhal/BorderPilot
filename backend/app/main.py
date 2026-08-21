from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import behavior, counterparties, entities, netting, obligations, packet, scoring, smes

app = FastAPI(title="BorderPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(smes.router)
app.include_router(counterparties.router)
app.include_router(obligations.router)
app.include_router(behavior.router)
app.include_router(scoring.router)
app.include_router(netting.router)
app.include_router(packet.router)
app.include_router(entities.router)


@app.get("/health")
def health():
    return {"status": "ok"}
