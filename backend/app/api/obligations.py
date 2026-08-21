import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import ObligationOut
from app.db.session import get_db
from app.models import Obligation

router = APIRouter(prefix="/obligations", tags=["obligations"])


@router.get("", response_model=list[ObligationOut])
def list_obligations(db: Session = Depends(get_db)):
    return db.execute(select(Obligation)).scalars().all()


@router.get("/{obligation_id}", response_model=ObligationOut)
def get_obligation(obligation_id: uuid.UUID, db: Session = Depends(get_db)):
    obligation = db.get(Obligation, obligation_id)
    if obligation is None:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return obligation
