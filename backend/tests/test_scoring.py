"""Phase 3 checks: deterministic reliability scoring (M4, narrowed).

Uses flush-only + rollback per test, same as test_behavior.py, so nothing
lands in the shared seeded dev database.
"""

import uuid
from datetime import date

import pytest

from app.db.session import SessionLocal
from app.models import SME, Counterparty, Obligation, PaymentEvent
from app.models.obligation import ObligationDirection, ObligationStatus
from app.services.scoring import (
    NEUTRAL_SCORE,
    compute_counterparty_score,
    compute_obligation_score,
    tier_from_score,
)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def _make_sme(db, country="US", currency="USD") -> SME:
    sme = SME(id=uuid.uuid4(), name=f"Test SME {uuid.uuid4()}", country=country, base_currency=currency)
    db.add(sme)
    db.flush()
    return sme


def _make_counterparty(db, country="US") -> Counterparty:
    cp = Counterparty(id=uuid.uuid4(), name=f"Test Counterparty {uuid.uuid4()}", country=country)
    db.add(cp)
    db.flush()
    return cp


def _add_events(db, cp, sme, count, delay_days):
    for i in range(count):
        due = date(2026, 1, 1)
        db.add(
            PaymentEvent(
                counterparty_id=cp.id,
                sme_id=sme.id,
                due_date=due,
                paid_date=date(2026, 1, 1 + delay_days) if delay_days else due,
                amount=1000,
                currency="USD",
            )
        )
    db.flush()


def test_tier_boundaries():
    assert tier_from_score(90) == "A"
    assert tier_from_score(85) == "A"
    assert tier_from_score(84.9) == "B"
    assert tier_from_score(70) == "B"
    assert tier_from_score(55) == "C"
    assert tier_from_score(40) == "D"
    assert tier_from_score(0) == "E"


def test_counterparty_score_neutral_with_no_history(db):
    cp = _make_counterparty(db, country="ZZ")  # unknown country -> default corridor
    row = compute_counterparty_score(db, cp.id)
    assert row.factors["behavior"]["reason"] == "no_payment_history"
    # 0.7 * NEUTRAL + 0.3 * default_corridor(55) == NEUTRAL when default corridor == neutral
    assert row.score == pytest.approx(0.7 * NEUTRAL_SCORE + 0.3 * 55.0, abs=0.01)


def test_counterparty_score_deterministic(db):
    cp = _make_counterparty(db)
    sme = _make_sme(db)
    _add_events(db, cp, sme, count=5, delay_days=2)

    r1 = compute_counterparty_score(db, cp.id)
    r2 = compute_counterparty_score(db, cp.id)
    assert r1.score == r2.score
    assert r2.version == r1.version + 1  # versioned history, values unchanged


def test_more_on_time_history_improves_score(db):
    cp = _make_counterparty(db, country="US")
    sme = _make_sme(db, country="US")
    _add_events(db, cp, sme, count=3, delay_days=10)  # late
    score_before = compute_counterparty_score(db, cp.id).score

    _add_events(db, cp, sme, count=10, delay_days=0)  # then a run of on-time payments
    score_after = compute_counterparty_score(db, cp.id).score

    assert score_after > score_before


def test_obligation_score_handles_no_comparable_obligations(db):
    cp = _make_counterparty(db)
    sme = _make_sme(db)
    _add_events(db, cp, sme, count=3, delay_days=0)
    obligation = Obligation(
        sme_id=sme.id,
        counterparty_id=cp.id,
        direction=ObligationDirection.RECEIVABLE,
        amount=1000,
        currency="USD",
        expected_settlement_date=date(2026, 3, 1),
        status=ObligationStatus.OPEN,
    )
    db.add(obligation)
    db.flush()

    row = compute_obligation_score(db, obligation.id)
    assert row.factors["obligation_signal"]["reason"] == "no_comparable_obligations"
    assert row.tier in {"A", "B", "C", "D", "E"}
