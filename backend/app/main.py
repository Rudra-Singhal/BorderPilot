from fastapi import FastAPI

from app.api import behavior, counterparties, netting, obligations, packet, scoring, smes

app = FastAPI(title="BorderPilot API")

app.include_router(smes.router)
app.include_router(counterparties.router)
app.include_router(obligations.router)
app.include_router(behavior.router)
app.include_router(scoring.router)
app.include_router(netting.router)
app.include_router(packet.router)


@app.get("/health")
def health():
    return {"status": "ok"}
