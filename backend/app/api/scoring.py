import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import ReliabilityScoreOut
from app.db.session import get_db
from app.models import ReliabilityScore
from app.services.scoring import (
    compute_counterparty_score,
    compute_obligation_score,
    recompute_all_counterparty_scores,
)

router = APIRouter(prefix="/reliability-scores", tags=["reliability-scores"])


def _latest(db: Session, counterparty_id: uuid.UUID, obligation_id: uuid.UUID | None) -> ReliabilityScore | None:
    return db.execute(
        select(ReliabilityScore)
        .where(
            ReliabilityScore.counterparty_id == counterparty_id,
            ReliabilityScore.obligation_id == obligation_id,
        )
        .order_by(ReliabilityScore.version.desc())
        .limit(1)
    ).scalar_one_or_none()


@router.post("/counterparty/recompute-all")
def recompute_all(db: Session = Depends(get_db)):
    rows = recompute_all_counterparty_scores(db)
    return {"recomputed": len(rows)}


@router.get("/counterparty/{counterparty_id}", response_model=ReliabilityScoreOut)
def get_counterparty_score(counterparty_id: uuid.UUID, db: Session = Depends(get_db)):
    score = _latest(db, counterparty_id, None)
    if score is None:
        raise HTTPException(status_code=404, detail="No reliability score computed for this counterparty yet")
    return score


@router.get("/counterparty/{counterparty_id}/history", response_model=list[ReliabilityScoreOut])
def get_counterparty_score_history(counterparty_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.execute(
        select(ReliabilityScore)
        .where(ReliabilityScore.counterparty_id == counterparty_id, ReliabilityScore.obligation_id.is_(None))
        .order_by(ReliabilityScore.version.desc())
    ).scalars().all()


@router.post("/counterparty/{counterparty_id}/recompute", response_model=ReliabilityScoreOut)
def recompute_counterparty_score(counterparty_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        row = compute_counterparty_score(db, counterparty_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    db.commit()
    db.refresh(row)
    return row


@router.get("/obligation/{obligation_id}", response_model=ReliabilityScoreOut)
def get_obligation_score(obligation_id: uuid.UUID, db: Session = Depends(get_db)):
    row = db.execute(
        select(ReliabilityScore)
        .where(ReliabilityScore.obligation_id == obligation_id)
        .order_by(ReliabilityScore.version.desc())
        .limit(1)
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="No reliability score computed for this obligation yet")
    return row


@router.post("/obligation/{obligation_id}/recompute", response_model=ReliabilityScoreOut)
def recompute_obligation_score(obligation_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        row = compute_obligation_score(db, obligation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    db.commit()
    db.refresh(row)
    return row
