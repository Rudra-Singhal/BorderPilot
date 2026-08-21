"""Phase 2 (v2) checks: the expanded §24-scale demo dataset. Runs against the seeded
dev database, same style as test_seed_data.py."""

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models import (
    SME,
    BankNBFCPartner,
    Counterparty,
    Invoice,
    Obligation,
    PaymentEvent,
)


def test_dataset_scale():
    db = SessionLocal()
    try:
        assert db.execute(select(func.count()).select_from(SME)).scalar() == 8
        assert db.execute(select(func.count()).select_from(Counterparty)).scalar() == 15
        assert db.execute(select(func.count()).select_from(BankNBFCPartner)).scalar() >= 1
        # hero buyer needs enough history to make the pooling story real
        assert db.execute(select(func.count()).select_from(PaymentEvent)).scalar() >= 120
    finally:
        db.close()


def test_schmidt_is_pooled_across_six_smes():
    db = SessionLocal()
    try:
        schmidt = db.execute(
            select(Counterparty).where(Counterparty.name == "Schmidt Industrial GmbH")
        ).scalar_one()
        distinct_smes = db.execute(
            select(func.count(func.distinct(PaymentEvent.sme_id))).where(
                PaymentEvent.counterparty_id == schmidt.id
            )
        ).scalar()
        total_events = db.execute(
            select(func.count()).select_from(PaymentEvent).where(
                PaymentEvent.counterparty_id == schmidt.id
            )
        ).scalar()
        assert distinct_smes == 6  # the "no single lender sees this" moment
        assert total_events >= 90
    finally:
        db.close()


def test_thin_data_buyers_exist():
    db = SessionLocal()
    try:
        rows = db.execute(
            select(PaymentEvent.counterparty_id, func.count().label("n"))
            .group_by(PaymentEvent.counterparty_id)
        ).all()
        thin = [r for r in rows if r.n < 5]
        assert len(thin) >= 1  # for the confidence-multiplier / conservative-pricing story
    finally:
        db.close()


def test_hero_invoice_and_obligation_link():
    db = SessionLocal()
    try:
        hero = db.execute(
            select(Invoice).where(Invoice.invoice_number == "INV-0001")
        ).scalar_one()
        assert hero.amount == 50000
        assert hero.currency == "EUR"
        # every open obligation should be backed by an invoice
        unlinked = db.execute(
            select(func.count()).select_from(Obligation).where(Obligation.invoice_id.is_(None))
        ).scalar()
        assert unlinked == 0
    finally:
        db.close()
