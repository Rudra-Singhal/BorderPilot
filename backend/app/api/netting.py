import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import NettingRunDetailOut, NettingRunOut, OffsetMatchOut, ResidualOut
from app.db.session import get_db
from app.models import NettingRun, OffsetMatch
from app.services.netting import compute_residuals, run_netting

router = APIRouter(prefix="/netting-runs", tags=["netting"])


def _to_detail(run: NettingRun, matches: list[OffsetMatch]) -> NettingRunDetailOut:
    return NettingRunDetailOut(
        id=run.id,
        executed_at=run.executed_at,
        window_days=run.window_days,
        obligations_considered=run.obligations_considered,
        matches_created=run.matches_created,
        fx_snapshot=run.fx_snapshot,
        matches=[OffsetMatchOut.model_validate(m) for m in matches],
    )


@router.post("", response_model=NettingRunDetailOut)
def create_netting_run(db: Session = Depends(get_db)):
    run = run_netting(db)
    db.commit()
    db.refresh(run)
    matches = db.execute(select(OffsetMatch).where(OffsetMatch.netting_run_id == run.id)).scalars().all()
    return _to_detail(run, matches)


@router.get("", response_model=list[NettingRunOut])
def list_netting_runs(db: Session = Depends(get_db)):
    return db.execute(select(NettingRun).order_by(NettingRun.executed_at.desc())).scalars().all()


@router.get("/{netting_run_id}", response_model=NettingRunDetailOut)
def get_netting_run(netting_run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = db.get(NettingRun, netting_run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="NettingRun not found")
    matches = db.execute(select(OffsetMatch).where(OffsetMatch.netting_run_id == run.id)).scalars().all()
    return _to_detail(run, matches)


@router.get("/{netting_run_id}/residuals", response_model=list[ResidualOut])
def get_netting_run_residuals(netting_run_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return compute_residuals(db, netting_run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
