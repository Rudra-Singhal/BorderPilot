"""Phase 2 checks: pooled payment behavior aggregation (M3).

Uses flush-only + rollback per test so nothing lands in the shared seeded
dev database — commit would pollute the counts other phases' manual tests
rely on.
"""

import uuid
from datetime import date

import pytest

from app.db.session import SessionLocal
from app.models import SME, Counterparty, PaymentEvent
from app.services.behavior import recompute_profile


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def _make_sme(db, name="Test SME") -> SME:
    sme = SME(id=uuid.uuid4(), name=f"{name} {uuid.uuid4()}", country="US", base_currency="USD")
    db.add(sme)
    db.flush()
    return sme


def _make_counterparty(db, name="Test Counterparty") -> Counterparty:
    cp = Counterparty(id=uuid.uuid4(), name=f"{name} {uuid.uuid4()}", country="US")
    db.add(cp)
    db.flush()
    return cp


def test_recompute_returns_none_with_no_events(db):
    cp = _make_counterparty(db)
    profile = recompute_profile(db, cp.id)
    assert profile is None


def test_recompute_reflects_new_cross_sme_event(db):
    cp = _make_counterparty(db)
    sme_a = _make_sme(db, "SME A")
    sme_b = _make_sme(db, "SME B")
    db.add_all(
        [
            PaymentEvent(
                counterparty_id=cp.id,
                sme_id=sme_a.id,
                due_date=date(2026, 1, 1),
                paid_date=date(2026, 1, 1),
                amount=100,
                currency="USD",
            ),
            PaymentEvent(
                counterparty_id=cp.id,
                sme_id=sme_a.id,
                due_date=date(2026, 1, 1),
                paid_date=date(2026, 1, 1),
                amount=100,
                currency="USD",
            ),
        ]
    )
    db.flush()

    profile_before = recompute_profile(db, cp.id)
    assert profile_before.transaction_count == 2
    assert profile_before.on_time_ratio == 1.0
    on_time_ratio_before = profile_before.on_time_ratio  # capture scalar: recompute mutates the same row in place

    # a new SME transacts late with the same counterparty
    db.add(
        PaymentEvent(
            counterparty_id=cp.id,
            sme_id=sme_b.id,
            due_date=date(2026, 2, 1),
            paid_date=date(2026, 2, 15),
            amount=500,
            currency="USD",
        )
    )
    db.flush()

    profile_after = recompute_profile(db, cp.id)
    assert profile_after.transaction_count == 3
    assert profile_after.on_time_ratio < on_time_ratio_before


def test_single_sme_counterparty_does_not_crash(db):
    cp = _make_counterparty(db)
    sme = _make_sme(db)
    db.add(
        PaymentEvent(
            counterparty_id=cp.id,
            sme_id=sme.id,
            due_date=date(2026, 1, 1),
            paid_date=date(2026, 1, 3),
            amount=100,
            currency="USD",
        )
    )
    db.flush()

    profile = recompute_profile(db, cp.id)
    assert profile.transaction_count == 1
    assert profile.delay_variance == 0.0  # single data point, no crash on pvariance


def test_recompute_is_deterministic(db):
    cp = _make_counterparty(db)
    sme = _make_sme(db)
    db.add_all(
        [
            PaymentEvent(
                counterparty_id=cp.id,
                sme_id=sme.id,
                due_date=date(2026, 1, 1),
                paid_date=date(2026, 1, 4),
                amount=100,
                currency="USD",
            ),
            PaymentEvent(
                counterparty_id=cp.id,
                sme_id=sme.id,
                due_date=date(2026, 2, 1),
                paid_date=date(2026, 1, 30),
                amount=200,
                currency="USD",
            ),
        ]
    )
    db.flush()

    p1 = recompute_profile(db, cp.id)
    first = (p1.on_time_ratio, p1.median_delay_days, p1.delay_variance, p1.transaction_count)

    p2 = recompute_profile(db, cp.id)
    second = (p2.on_time_ratio, p2.median_delay_days, p2.delay_variance, p2.transaction_count)

    assert first == second
