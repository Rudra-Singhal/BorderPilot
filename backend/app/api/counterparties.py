import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api.schemas import CounterpartyOut, ObligationOut
from app.db.session import get_db
from app.models import Counterparty, Obligation

router = APIRouter(prefix="/counterparties", tags=["counterparties"])


@router.get("", response_model=list[CounterpartyOut])
def list_counterparties(db: Session = Depends(get_db)):
    return db.execute(select(Counterparty)).scalars().all()


@router.get("/pooled-overlap")
def get_pooled_overlap(db: Session = Depends(get_db)):
    """Debug/manual-test helper: counterparties linked to more than one distinct SME."""
    rows = db.execute(
        select(
            Obligation.counterparty_id,
            func.count(func.distinct(Obligation.sme_id)).label("distinct_sme_count"),
        ).group_by(Obligation.counterparty_id)
    ).all()
    return [
        {"counterparty_id": row.counterparty_id, "distinct_sme_count": row.distinct_sme_count}
        for row in rows
        if row.distinct_sme_count > 1
    ]


@router.get("/{counterparty_id}", response_model=CounterpartyOut)
def get_counterparty(counterparty_id: uuid.UUID, db: Session = Depends(get_db)):
    counterparty = db.get(Counterparty, counterparty_id)
    if counterparty is None:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    return counterparty


@router.get("/{counterparty_id}/obligations", response_model=list[ObligationOut])
def get_counterparty_obligations(counterparty_id: uuid.UUID, db: Session = Depends(get_db)):
    return (
        db.execute(select(Obligation).where(Obligation.counterparty_id == counterparty_id))
        .scalars()
        .all()
    )
