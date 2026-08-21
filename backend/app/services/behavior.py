"""M3: pooled payment behavior aggregation — one profile per Counterparty,
built from PaymentEvents across *all* SMEs linked to that counterparty.
"""

import uuid
from statistics import median, pvariance

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PaymentBehaviorProfile, PaymentEvent


def _compute_stats(events: list[PaymentEvent]) -> dict:
    delays = [(e.paid_date - e.due_date).days for e in events]
    on_time_count = sum(1 for d in delays if d <= 0)
    return {
        "on_time_ratio": on_time_count / len(delays),
        "median_delay_days": float(median(delays)),
        "delay_variance": float(pvariance(delays)) if len(delays) > 1 else 0.0,
        "transaction_count": len(events),
        "most_recent_payment_date": max(e.paid_date for e in events),
    }


def recompute_profile(db: Session, counterparty_id: uuid.UUID) -> PaymentBehaviorProfile | None:
    """Recomputes and upserts the behavior profile for one counterparty. Returns None if it
    has no PaymentEvents yet (nothing to aggregate)."""
    events = db.execute(
        select(PaymentEvent).where(PaymentEvent.counterparty_id == counterparty_id)
    ).scalars().all()
    if not events:
        return None

    stats = _compute_stats(events)

    profile = db.execute(
        select(PaymentBehaviorProfile).where(PaymentBehaviorProfile.counterparty_id == counterparty_id)
    ).scalar_one_or_none()
    if profile is None:
        profile = PaymentBehaviorProfile(counterparty_id=counterparty_id, **stats)
        db.add(profile)
    else:
        for key, value in stats.items():
            setattr(profile, key, value)

    db.flush()
    return profile


def recompute_all_profiles(db: Session) -> list[PaymentBehaviorProfile]:
    counterparty_ids = db.execute(select(PaymentEvent.counterparty_id).distinct()).scalars().all()
    profiles = []
    for counterparty_id in counterparty_ids:
        profile = recompute_profile(db, counterparty_id)
        if profile is not None:
            profiles.append(profile)
    db.commit()
    return profiles
