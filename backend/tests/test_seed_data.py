"""Phase 1 checks: run against the seeded dev database (docker-compose db)."""

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models import SME, Counterparty, Obligation, PaymentEvent


def test_smes_and_counterparties_seeded():
    db = SessionLocal()
    try:
        assert db.execute(select(func.count()).select_from(SME)).scalar() >= 5
        assert db.execute(select(func.count()).select_from(Counterparty)).scalar() >= 10
    finally:
        db.close()


def test_no_negative_or_zero_obligation_amounts():
    db = SessionLocal()
    try:
        bad = db.execute(select(func.count()).select_from(Obligation).where(Obligation.amount <= 0)).scalar()
        assert bad == 0
    finally:
        db.close()


def test_at_least_three_counterparties_have_cross_sme_overlap():
    db = SessionLocal()
    try:
        rows = db.execute(
            select(
                Obligation.counterparty_id,
                func.count(func.distinct(Obligation.sme_id)).label("distinct_smes"),
            ).group_by(Obligation.counterparty_id)
        ).all()
        overlapping = [r for r in rows if r.distinct_smes > 1]
        assert len(overlapping) >= 3
    finally:
        db.close()


def test_payment_events_exist_for_shared_counterparties():
    db = SessionLocal()
    try:
        overlapping_ids = [
            r.counterparty_id
            for r in db.execute(
                select(
                    Obligation.counterparty_id,
                    func.count(func.distinct(Obligation.sme_id)).label("distinct_smes"),
                ).group_by(Obligation.counterparty_id)
            ).all()
            if r.distinct_smes > 1
        ]
        for cp_id in overlapping_ids:
            count = db.execute(
                select(func.count()).select_from(PaymentEvent).where(PaymentEvent.counterparty_id == cp_id)
            ).scalar()
            assert count > 0, f"counterparty {cp_id} has cross-SME obligations but no payment events"
    finally:
        db.close()
