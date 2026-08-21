import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import SMEOut
from app.db.session import get_db
from app.models import SME

router = APIRouter(prefix="/smes", tags=["smes"])


@router.get("", response_model=list[SMEOut])
def list_smes(db: Session = Depends(get_db)):
    return db.execute(select(SME)).scalars().all()


@router.get("/{sme_id}", response_model=SMEOut)
def get_sme(sme_id: uuid.UUID, db: Session = Depends(get_db)):
    sme = db.get(SME, sme_id)
    if sme is None:
        raise HTTPException(status_code=404, detail="SME not found")
    return sme
