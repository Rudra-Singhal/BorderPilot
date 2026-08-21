"""Seeds the BorderPilot demo dataset -- hand-crafted to the reference spec's §24 so the
pooling, underwriting, and netting stories all demo well on real (if synthetic) data.

Design:
- 8 Indian export SMEs, 15 foreign buyers across 6 countries (DE/US/GB/AE/VN/NL), 4 currencies.
- Buyers follow 3 archetypes (reliable / moderate / unreliable) plus 2 thin-data buyers, so the
  reliability score visibly differentiates. Schmidt Industrial GmbH is the hero buyer: ~94 pooled
  payment events across 6 SMEs -- the "no single lender sees this much history" moment.
- Deliberate shared buyers across SMEs (that overlap is what makes pooling + netting demonstrable),
  one high-concentration SME (Indus Leatherworks), and one risky corridor (Vietnam -> India).
- Hand-crafted open obligations that produce 4+ clean netting matches, including the hero:
  Raj Exports' EUR 50,000 receivable from Schmidt, due in 45 days.

Deterministic: fixed anchor date + seeded RNG, so every reset reproduces identical data. Idempotent:
safe to re-run, keyed by natural keys.

Run with: python -m app.seed.seed
"""

import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.db.session import Base, SessionLocal, engine
from app.models import (
    SME,
    BankNBFCPartner,
    Counterparty,
    Invoice,
    Obligation,
    PaymentEvent,
)
from app.models.bank_nbfc_partner import PartnerType
from app.models.invoice import InvoiceSource
from app.models.obligation import ObligationDirection, ObligationStatus
from app.services.scoring import recompute_all_counterparty_scores

ANCHOR = date(2026, 8, 22)
RNG_SEED = 42

# --- 8 Indian export SMEs (varied sectors, all INR base) ---
SMES = [
    {"name": "Raj Exports", "country": "IN", "base_currency": "INR"},  # hero SME (auto parts, Pune)
    {"name": "Acme Textiles", "country": "IN", "base_currency": "INR"},
    {"name": "Deccan Pharma", "country": "IN", "base_currency": "INR"},
    {"name": "Kestrel Electronics", "country": "IN", "base_currency": "INR"},
    {"name": "Coromandel Components", "country": "IN", "base_currency": "INR"},
    {"name": "Sahyadri Organics", "country": "IN", "base_currency": "INR"},
    {"name": "Indus Leatherworks", "country": "IN", "base_currency": "INR"},  # high-concentration SME
    {"name": "Ganges Steel", "country": "IN", "base_currency": "INR"},
]

# --- 15 foreign buyers. currency = the currency this buyer invoices in ---
COUNTERPARTIES = [
    {"name": "Schmidt Industrial GmbH", "country": "DE", "currency": "EUR", "archetype": "reliable"},
    {"name": "EuroMart GmbH", "country": "DE", "currency": "EUR", "archetype": "moderate"},
    {"name": "Hamburg Metals GmbH", "country": "DE", "currency": "EUR", "archetype": "moderate"},
    {"name": "Global Retail Corp", "country": "US", "currency": "USD", "archetype": "reliable"},
    {"name": "Coastal Foods Inc", "country": "US", "currency": "USD", "archetype": "moderate"},
    {"name": "Falcon Supply Co", "country": "US", "currency": "USD", "archetype": "moderate"},
    {"name": "Northwind Traders", "country": "GB", "currency": "GBP", "archetype": "unreliable"},
    {"name": "British Components Ltd", "country": "GB", "currency": "GBP", "archetype": "reliable"},
    {"name": "Gulf Trading LLC", "country": "AE", "currency": "USD", "archetype": "moderate"},
    {"name": "Emirates Auto Parts", "country": "AE", "currency": "USD", "archetype": "thin"},
    {"name": "Mekong Manufacturing", "country": "VN", "currency": "USD", "archetype": "unreliable"},
    {"name": "Saigon Textiles Co", "country": "VN", "currency": "USD", "archetype": "moderate"},
    {"name": "Rotterdam Logistics BV", "country": "NL", "currency": "EUR", "archetype": "reliable"},
    {"name": "Amsterdam Foods BV", "country": "NL", "currency": "EUR", "archetype": "moderate"},
    {"name": "Delta Materials NV", "country": "NL", "currency": "EUR", "archetype": "thin"},
]

# archetype -> fraction of payments that land on-time (delay <= 0) when generating history
ARCHETYPE_ON_TIME = {"reliable": 0.92, "moderate": 0.78, "unreliable": 0.46, "thin": 0.80}

# counterparty_name -> (list of SME names it transacts with, total historical events)
# The overlap here IS the pooling; Schmidt is deliberately spread across 6 SMEs.
HISTORY_PLAN = {
    "Schmidt Industrial GmbH": (
        ["Raj Exports", "Acme Textiles", "Kestrel Electronics", "Coromandel Components", "Ganges Steel", "Deccan Pharma"],
        94,
    ),
    "Global Retail Corp": (["Acme Textiles", "Sahyadri Organics", "Coromandel Components", "Raj Exports"], 40),
    "British Components Ltd": (["Kestrel Electronics", "Ganges Steel"], 18),
    "Rotterdam Logistics BV": (["Sahyadri Organics", "Deccan Pharma"], 16),
    "EuroMart GmbH": (["Acme Textiles", "Ganges Steel"], 14),
    "Hamburg Metals GmbH": (["Coromandel Components", "Ganges Steel"], 12),
    "Coastal Foods Inc": (["Sahyadri Organics"], 10),
    "Falcon Supply Co": (["Raj Exports", "Kestrel Electronics"], 12),
    "Gulf Trading LLC": (["Indus Leatherworks", "Acme Textiles"], 12),
    "Saigon Textiles Co": (["Acme Textiles", "Indus Leatherworks"], 10),
    "Amsterdam Foods BV": (["Sahyadri Organics", "Deccan Pharma"], 12),
    "Northwind Traders": (["Kestrel Electronics", "Ganges Steel"], 10),
    "Mekong Manufacturing": (["Coromandel Components", "Raj Exports"], 8),
    "Emirates Auto Parts": (["Indus Leatherworks"], 3),  # thin
    "Delta Materials NV": (["Deccan Pharma"], 2),  # thin
}

# Hand-crafted OPEN obligations. Same 14-day settlement bucket + same counterparty = nettable.
# (sme, counterparty, direction, amount, settlement_date) -- currency taken from the counterparty.
# Grouped by design intent; every entry becomes an Invoice + Obligation.
# NOTE: the netting engine buckets by 14-day windows anchored at 2026-01-01, so every
# obligation in a scenario must fall inside the *same* window to be matchable. Dates below
# are chosen mid-bucket to leave margin. Bucket 19 = 09-24..10-07, 20 = 10-08..10-21,
# 21 = 10-22..11-04, 22 = 11-05..11-18, 23 = 11-19..12-02.
OPEN_OBLIGATIONS = [
    # -- Scenario A: hero corridor, Schmidt, bucket 19 --
    ("Raj Exports", "Schmidt Industrial GmbH", "receivable", 50000, date(2026, 10, 5)),  # HERO
    ("Kestrel Electronics", "Schmidt Industrial GmbH", "payable", 30000, date(2026, 10, 6)),
    ("Coromandel Components", "Schmidt Industrial GmbH", "receivable", 22000, date(2026, 10, 7)),
    # -- Scenario B: Global Retail, bucket 20 --
    ("Acme Textiles", "Global Retail Corp", "receivable", 22000, date(2026, 10, 12)),
    ("Sahyadri Organics", "Global Retail Corp", "payable", 18000, date(2026, 10, 13)),
    # -- Scenario C: British Components, bucket 22 --
    ("Kestrel Electronics", "British Components Ltd", "payable", 15000, date(2026, 11, 9)),
    ("Ganges Steel", "British Components Ltd", "receivable", 12000, date(2026, 11, 10)),
    # -- Scenario D: Rotterdam, bucket 21 --
    ("Sahyadri Organics", "Rotterdam Logistics BV", "receivable", 14000, date(2026, 10, 26)),
    ("Deccan Pharma", "Rotterdam Logistics BV", "payable", 9000, date(2026, 10, 27)),
    # -- Scenario E: multilateral on EuroMart, bucket 23 --
    ("Ganges Steel", "EuroMart GmbH", "payable", 20000, date(2026, 11, 23)),
    ("Acme Textiles", "EuroMart GmbH", "receivable", 12000, date(2026, 11, 24)),
    ("Coromandel Components", "EuroMart GmbH", "receivable", 8000, date(2026, 11, 25)),
    # -- Unmatched open obligations for realism (the residual story) --
    ("Indus Leatherworks", "Gulf Trading LLC", "receivable", 16500, date(2026, 9, 30)),
    ("Indus Leatherworks", "Saigon Textiles Co", "receivable", 9800, date(2026, 10, 15)),
    ("Indus Leatherworks", "Emirates Auto Parts", "receivable", 7200, date(2026, 11, 2)),
    ("Deccan Pharma", "Amsterdam Foods BV", "receivable", 13400, date(2026, 10, 29)),
    ("Coromandel Components", "Mekong Manufacturing", "receivable", 11200, date(2026, 11, 27)),
    ("Kestrel Electronics", "Northwind Traders", "receivable", 10600, date(2026, 10, 1)),
    ("Raj Exports", "Falcon Supply Co", "payable", 8400, date(2026, 9, 18)),
    ("Sahyadri Organics", "Coastal Foods Inc", "receivable", 15200, date(2026, 10, 9)),
    ("Ganges Steel", "Hamburg Metals GmbH", "payable", 17800, date(2026, 11, 12)),
]

BANK_PARTNERS = [
    {"name": "Meridian Trade Finance NBFC", "partner_type": PartnerType.NBFC, "country": "IN", "min_auto_tier": "B", "typical_latency_ms": 1400},
    {"name": "Coromandel Supply-Chain Finance", "partner_type": PartnerType.BANK, "country": "IN", "min_auto_tier": "B", "typical_latency_ms": 2100},
]


def get_or_create(db: Session, model, defaults: dict, **key):
    row = db.query(model).filter_by(**key).one_or_none()
    if row is None:
        row = model(**key, **defaults)
        db.add(row)
        db.flush()
    return row


def _generate_history(db: Session, rng: random.Random, smes_by_name: dict, cps_by_name: dict) -> int:
    """Generates historical PaymentEvents per the HISTORY_PLAN, distributing each counterparty's
    total across its linked SMEs and hitting its archetype's on-time fraction."""
    created = 0
    for cp_name, (sme_names, total) in HISTORY_PLAN.items():
        cp = cps_by_name[cp_name]
        meta = next(c for c in COUNTERPARTIES if c["name"] == cp_name)
        currency = meta["currency"]
        on_time_target = int(round(total * ARCHETYPE_ON_TIME[meta["archetype"]]))

        # decide on-time vs late for each of the `total` events, then spread across SMEs
        flags = [True] * on_time_target + [False] * (total - on_time_target)
        rng.shuffle(flags)

        for i, on_time in enumerate(flags):
            sme = smes_by_name[sme_names[i % len(sme_names)]]
            # skip if this exact (cp, sme, due_date) already seeded (idempotency)
            due = ANCHOR - timedelta(days=30 + i * 11 + (7 if cp_name == "Schmidt Industrial GmbH" else 0))
            if on_time:
                delay = rng.choice([-3, -2, -1, 0, 0])
            else:
                # split late into moderate (1-14) and significant (15-35)
                delay = rng.randint(1, 14) if rng.random() < 0.7 else rng.randint(15, 35)
            paid = due + timedelta(days=delay)
            amount = 4000 + rng.randint(0, 18) * 850

            exists = (
                db.query(PaymentEvent)
                .filter_by(counterparty_id=cp.id, sme_id=sme.id, due_date=due)
                .count()
            )
            if exists == 0:
                db.add(
                    PaymentEvent(
                        counterparty_id=cp.id,
                        sme_id=sme.id,
                        obligation_id=None,
                        due_date=due,
                        paid_date=paid,
                        amount=amount,
                        currency=currency,
                    )
                )
                created += 1
    return created


def _create_open_obligations(db: Session, smes_by_name: dict, cps_by_name: dict) -> int:
    created = 0
    for seq, (sme_name, cp_name, direction, amount, settle_date) in enumerate(OPEN_OBLIGATIONS):
        sme = smes_by_name[sme_name]
        cp = cps_by_name[cp_name]
        currency = next(c for c in COUNTERPARTIES if c["name"] == cp_name)["currency"]
        invoice_number = f"INV-{seq + 1:04d}"

        if db.query(Invoice).filter_by(invoice_number=invoice_number).count() > 0:
            continue

        dir_enum = ObligationDirection(direction)
        invoice = Invoice(
            sme_id=sme.id,
            counterparty_id=cp.id,
            invoice_number=invoice_number,
            direction=dir_enum,
            amount=amount,
            currency=currency,
            invoice_date=settle_date - timedelta(days=45),
            due_date=settle_date,
            po_reference=f"PO-{2600 + seq}",
            source=InvoiceSource.SEEDED,
        )
        db.add(invoice)
        db.flush()

        db.add(
            Obligation(
                sme_id=sme.id,
                counterparty_id=cp.id,
                invoice_id=invoice.id,
                direction=dir_enum,
                amount=amount,
                currency=currency,
                expected_settlement_date=settle_date,
                status=ObligationStatus.OPEN,
            )
        )
        created += 1
    return created


def run():
    Base.metadata.create_all(bind=engine)
    rng = random.Random(RNG_SEED)
    db = SessionLocal()
    try:
        smes_by_name = {
            s["name"]: get_or_create(db, SME, {"country": s["country"], "base_currency": s["base_currency"]}, name=s["name"])
            for s in SMES
        }
        cps_by_name = {
            c["name"]: get_or_create(db, Counterparty, {"country": c["country"]}, name=c["name"])
            for c in COUNTERPARTIES
        }
        for p in BANK_PARTNERS:
            get_or_create(
                db,
                BankNBFCPartner,
                {"partner_type": p["partner_type"], "country": p["country"], "min_auto_tier": p["min_auto_tier"], "typical_latency_ms": p["typical_latency_ms"]},
                name=p["name"],
            )
        db.flush()

        events = _generate_history(db, rng, smes_by_name, cps_by_name)
        obligations = _create_open_obligations(db, smes_by_name, cps_by_name)
        db.commit()

        scored = recompute_all_counterparty_scores(db)

        print(
            f"Seed complete: {len(smes_by_name)} SMEs, {len(cps_by_name)} counterparties, "
            f"{len(BANK_PARTNERS)} lender partners, {events} payment events seeded, "
            f"{obligations} open obligations (+invoices), {len(scored)} counterparties scored."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
