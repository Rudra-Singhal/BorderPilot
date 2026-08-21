"""Wipes all demo data and reseeds from scratch, so the demo environment can be
replayed cleanly between rehearsals (or right before the real thing) without any
leftover state from prior manual testing.

Run with: python -m app.seed.reset
"""

from sqlalchemy import text

from app.db.session import Base, SessionLocal, engine
from app.seed.seed import run as reseed

# Deletion order respects foreign keys (children before parents).
TABLES_IN_DELETE_ORDER = [
    "audit_events",
    "liquidity_events",
    "settlements",
    "compliance_requirements",
    "financing_agreements",
    "financing_offers",
    "underwriting_decisions",
    "bank_packets",
    "offset_matches",
    "netting_runs",
    "reliability_scores",
    "payment_behavior_profiles",
    "payment_events",
    "obligations",
    "invoices",
    "currency_exposures",
    "bank_nbfc_partners",
    "counterparties",
    "smes",
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for table in TABLES_IN_DELETE_ORDER:
            db.execute(text(f"DELETE FROM {table}"))
        db.commit()
        print(f"Cleared {len(TABLES_IN_DELETE_ORDER)} tables.")
    finally:
        db.close()

    reseed()


if __name__ == "__main__":
    run()
