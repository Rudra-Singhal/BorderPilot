"""Seeds SME / Counterparty / Obligation / PaymentEvent data with deliberate
cross-SME counterparty overlap, so Phase 2's pooled behavior aggregation has
something real to prove. Idempotent: safe to re-run, keyed by natural names.

Run with: python -m app.seed.seed
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.db.session import Base, SessionLocal, engine
from app.models import SME, Counterparty, Obligation, PaymentEvent
from app.models.obligation import ObligationDirection, ObligationStatus
from app.services.scoring import recompute_all_counterparty_scores

ANCHOR = date(2026, 8, 21)  # fixed reference date so re-runs are deterministic

SMES = [
    {"name": "Acme Textiles", "country": "IN", "base_currency": "INR"},
    {"name": "Nordic Gears", "country": "SE", "base_currency": "EUR"},
    {"name": "Pacific Foods", "country": "SG", "base_currency": "USD"},
    {"name": "Andes Coffee Co", "country": "CO", "base_currency": "USD"},
    {"name": "Baltic Steel", "country": "LT", "base_currency": "EUR"},
    {"name": "Kestrel Electronics", "country": "GB", "base_currency": "GBP"},
]

COUNTERPARTIES = [
    {"name": "Global Retail Corp", "country": "US"},
    {"name": "EuroMart GmbH", "country": "DE"},
    {"name": "Northwind Traders", "country": "GB"},
    {"name": "Sunrise Distribution", "country": "IN"},
    {"name": "Harbor Logistics", "country": "SG"},
    {"name": "Andina Exports", "country": "CO"},
    {"name": "Steel Works Ltd", "country": "LT"},
    {"name": "British Components", "country": "GB"},
    {"name": "Falcon Supply Co", "country": "US"},
    {"name": "Meridian Traders", "country": "SG"},
    {"name": "Coastal Foods Inc", "country": "US"},
    {"name": "Vega Materials", "country": "SE"},
]

# counterparty_name -> list of sme_names it transacts with (overlap is deliberate here)
COUNTERPARTY_SME_LINKS = {
    "Global Retail Corp": ["Acme Textiles", "Pacific Foods", "Andes Coffee Co"],
    "EuroMart GmbH": ["Nordic Gears", "Baltic Steel"],
    "Northwind Traders": ["Kestrel Electronics", "Nordic Gears"],
    "Falcon Supply Co": ["Acme Textiles", "Kestrel Electronics"],
    "Sunrise Distribution": ["Acme Textiles"],
    "Harbor Logistics": ["Pacific Foods"],
    "Andina Exports": ["Andes Coffee Co"],
    "Steel Works Ltd": ["Baltic Steel"],
    "British Components": ["Kestrel Electronics"],
    "Meridian Traders": ["Pacific Foods"],
    "Coastal Foods Inc": ["Andes Coffee Co"],
    "Vega Materials": ["Nordic Gears"],
}

SME_CURRENCY = {sme["name"]: sme["base_currency"] for sme in SMES}


def get_or_create_sme(db: Session, data: dict) -> SME:
    sme = db.query(SME).filter_by(name=data["name"]).one_or_none()
    if sme is None:
        sme = SME(**data)
        db.add(sme)
        db.flush()
    return sme


def get_or_create_counterparty(db: Session, data: dict) -> Counterparty:
    cp = db.query(Counterparty).filter_by(name=data["name"]).one_or_none()
    if cp is None:
        cp = Counterparty(**data)
        db.add(cp)
        db.flush()
    return cp


def seed_obligations_and_events(
    db: Session, sme: SME, counterparty: Counterparty, seq: int
) -> None:
    """Creates one open obligation + 2-3 historical payment events per (sme, counterparty) pair."""
    currency = SME_CURRENCY[sme.name]

    existing = (
        db.query(Obligation)
        .filter_by(sme_id=sme.id, counterparty_id=counterparty.id)
        .count()
    )
    if existing == 0:
        direction = ObligationDirection.RECEIVABLE if seq % 2 == 0 else ObligationDirection.PAYABLE
        amount = 5000 + (seq * 733) % 20000
        db.add(
            Obligation(
                sme_id=sme.id,
                counterparty_id=counterparty.id,
                direction=direction,
                amount=amount,
                currency=currency,
                expected_settlement_date=ANCHOR + timedelta(days=10 + (seq * 7) % 60),
                status=ObligationStatus.OPEN,
            )
        )

    existing_events = (
        db.query(PaymentEvent)
        .filter_by(sme_id=sme.id, counterparty_id=counterparty.id)
        .count()
    )
    if existing_events == 0:
        for i in range(3):
            due = ANCHOR - timedelta(days=30 + i * 40)
            # deliberately vary on-time-ness: mostly on-time with some slippage
            delay_days = (seq + i) % 5  # 0-4 days late, 0 = on time
            paid = due + timedelta(days=delay_days)
            amount = 4000 + ((seq + i) * 611) % 15000
            db.add(
                PaymentEvent(
                    counterparty_id=counterparty.id,
                    sme_id=sme.id,
                    obligation_id=None,
                    due_date=due,
                    paid_date=paid,
                    amount=amount,
                    currency=currency,
                )
            )


def _add_obligation_if_new(db: Session, sme: SME, counterparty: Counterparty, direction, amount, currency, settlement_date):
    """Adds an extra obligation beyond the one-per-pair from the main loop, keyed on the
    settlement date so a distinct demo-scenario date makes this idempotent on re-run."""
    existing = (
        db.query(Obligation)
        .filter_by(sme_id=sme.id, counterparty_id=counterparty.id, expected_settlement_date=settlement_date)
        .count()
    )
    if existing == 0:
        db.add(
            Obligation(
                sme_id=sme.id,
                counterparty_id=counterparty.id,
                direction=direction,
                amount=amount,
                currency=currency,
                expected_settlement_date=settlement_date,
                status=ObligationStatus.OPEN,
            )
        )


def _add_payment_event_if_new(db: Session, sme: SME, counterparty: Counterparty, due_date, paid_date, amount, currency):
    existing = (
        db.query(PaymentEvent)
        .filter_by(sme_id=sme.id, counterparty_id=counterparty.id, due_date=due_date)
        .count()
    )
    if existing == 0:
        db.add(
            PaymentEvent(
                counterparty_id=counterparty.id,
                sme_id=sme.id,
                obligation_id=None,
                due_date=due_date,
                paid_date=paid_date,
                amount=amount,
                currency=currency,
            )
        )


def seed_guaranteed_demo_scenarios(db: Session, smes_by_name: dict, counterparties_by_name: dict) -> None:
    """Bakes the two proof points already hand-verified during Phases 3-4-5 directly into
    the base dataset, so every demo replay -- not just a manually-poked one -- shows: (a) a
    multilateral match (one payable split across two different SMEs' receivables through a
    shared counterparty), and (b) a naturally tier-B counterparty producing an auto-eligible
    match. Without this, a fresh reset only ever reproduces the single thin cross-currency
    match from the base loop.
    """
    kestrel = smes_by_name["Kestrel Electronics"]
    nordic = smes_by_name["Nordic Gears"]
    baltic = smes_by_name["Baltic Steel"]
    acme = smes_by_name["Acme Textiles"]
    pacific = smes_by_name["Pacific Foods"]
    northwind = counterparties_by_name["Northwind Traders"]
    harbor = counterparties_by_name["Harbor Logistics"]

    # Multilateral: one payable, two receivables, one shared counterparty -- same bucket.
    multilateral_date = date(2026, 11, 2)
    _add_obligation_if_new(db, kestrel, northwind, ObligationDirection.PAYABLE, 1000, "GBP", multilateral_date)
    _add_obligation_if_new(db, nordic, northwind, ObligationDirection.RECEIVABLE, 600, "GBP", multilateral_date)
    _add_obligation_if_new(db, baltic, northwind, ObligationDirection.RECEIVABLE, 400, "GBP", multilateral_date)

    # Tier-B counterparty: a run of on-time payments plus a small matchable pair.
    for i in range(10):
        due = date(2026, 1, 1) + timedelta(days=i * 20)
        _add_payment_event_if_new(db, pacific, harbor, due, due, 3000, "USD")

    auto_eligible_date = date(2026, 12, 1)
    _add_obligation_if_new(db, acme, harbor, ObligationDirection.PAYABLE, 300, "INR", auto_eligible_date)
    _add_obligation_if_new(db, pacific, harbor, ObligationDirection.RECEIVABLE, 2, "USD", auto_eligible_date)


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        smes_by_name = {}
        for data in SMES:
            smes_by_name[data["name"]] = get_or_create_sme(db, data)
        db.flush()

        counterparties_by_name = {}
        for data in COUNTERPARTIES:
            counterparties_by_name[data["name"]] = get_or_create_counterparty(db, data)
        db.flush()

        seq = 0
        for cp_name, sme_names in COUNTERPARTY_SME_LINKS.items():
            counterparty = counterparties_by_name[cp_name]
            for sme_name in sme_names:
                sme = smes_by_name[sme_name]
                seed_obligations_and_events(db, sme, counterparty, seq)
                seq += 1

        seed_guaranteed_demo_scenarios(db, smes_by_name, counterparties_by_name)

        db.commit()

        # Score every counterparty up front -- otherwise only ones that happen to land in a
        # netting match ever get scored, leaving the rest "not scored" until someone calls
        # the bulk recompute endpoint (which showed up as a wall of expected-but-noisy 404s
        # on the Receivables page for a freshly seeded/reset environment).
        scored = recompute_all_counterparty_scores(db)

        print(
            f"Seed complete: {len(smes_by_name)} SMEs, {len(counterparties_by_name)} counterparties, "
            f"{seq} (sme, counterparty) obligation/payment-event pairs, plus guaranteed demo scenarios. "
            f"{len(scored)} counterparties scored."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
