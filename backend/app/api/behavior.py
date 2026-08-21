import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import PaymentBehaviorProfileOut
from app.db.session import get_db
from app.models import PaymentBehaviorProfile
from app.services.behavior import recompute_all_profiles, recompute_profile

router = APIRouter(prefix="/behavior-profiles", tags=["behavior"])


@router.post("/recompute")
def recompute(db: Session = Depends(get_db)):
    profiles = recompute_all_profiles(db)
    return {"recomputed": len(profiles)}


@router.post("/recompute/{counterparty_id}", response_model=PaymentBehaviorProfileOut)
def recompute_one(counterparty_id: uuid.UUID, db: Session = Depends(get_db)):
    profile = recompute_profile(db, counterparty_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="No PaymentEvents for this counterparty")
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{counterparty_id}", response_model=PaymentBehaviorProfileOut)
def get_profile(counterparty_id: uuid.UUID, db: Session = Depends(get_db)):
    profile = db.execute(
        select(PaymentBehaviorProfile).where(PaymentBehaviorProfile.counterparty_id == counterparty_id)
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="No behavior profile for this counterparty")
    return profile
