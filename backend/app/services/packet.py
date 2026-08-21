"""M6: assembles the bank-facing output packet for one NettingRun -- gross
obligations in, proposed matches (with tier + justification), net settlement
figures, an FX/friction savings estimate, and flagged manual-review items.
This is the artifact a bank would actually receive; no bank API call is made.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import SME, BankPacket, Counterparty, NettingRun, Obligation, OffsetMatch
from app.services.explain import ELIGIBILITY_NEEDS_REVIEW
from app.services.netting import compute_residuals

# Assumed cross-border transfer/FX spread avoided per USD-equivalent matched instead of
# settled gross. A placeholder estimate, not a real treasury cost model.
FRICTION_RATE = 0.005


def _match_entry(db: Session, match: OffsetMatch) -> dict:
    counterparty = db.get(Counterparty, match.counterparty_id)
    payable_ob = db.get(Obligation, match.payable_obligation_id)
    receivable_ob = db.get(Obligation, match.receivable_obligation_id)
    payable_sme = db.get(SME, payable_ob.sme_id)
    receivable_sme = db.get(SME, receivable_ob.sme_id)

    return {
        "match_id": str(match.id),
        "counterparty_name": counterparty.name,
        "payable_sme_name": payable_sme.name,
        "payable_obligation_currency": payable_ob.currency,
        "payable_obligation_amount": float(payable_ob.amount),
        "receivable_sme_name": receivable_sme.name,
        "receivable_obligation_currency": receivable_ob.currency,
        "receivable_obligation_amount": float(receivable_ob.amount),
        "matched_amount_usd": float(match.matched_amount_usd),
        "confidence_tier": match.confidence_tier,
        "eligibility_flag": match.eligibility_flag,
        "justification_text": match.justification_text,
        "ai_generated": match.ai_generated,
        "settlement_window": [
            match.settlement_bucket_start.isoformat(),
            match.settlement_bucket_end.isoformat(),
        ],
    }


def _residual_entry(db: Session, residual: dict) -> dict:
    obligation = db.get(Obligation, residual["obligation_id"])
    sme = db.get(SME, residual["sme_id"])
    counterparty = db.get(Counterparty, residual["counterparty_id"])
    return {
        "obligation_id": str(residual["obligation_id"]),
        "sme_name": sme.name,
        "counterparty_name": counterparty.name,
        "direction": residual["direction"],
        "currency": obligation.currency,
        "amount": float(obligation.amount),
        "total_usd": residual["total_usd"],
        "matched_usd": residual["matched_usd"],
        "residual_usd": residual["residual_usd"],
        "reason": "unmatched" if residual["matched_usd"] == 0 else "partially_matched",
    }


def build_packet(db: Session, netting_run_id: uuid.UUID) -> BankPacket:
    run = db.get(NettingRun, netting_run_id)
    if run is None:
        raise ValueError(f"NettingRun {netting_run_id} not found")

    matches = db.execute(
        select(OffsetMatch).where(OffsetMatch.netting_run_id == netting_run_id)
    ).scalars().all()
    residuals = compute_residuals(db, netting_run_id)

    match_entries = [_match_entry(db, m) for m in matches]
    flagged_matches = [e for e in match_entries if e["eligibility_flag"] == ELIGIBILITY_NEEDS_REVIEW]

    residual_entries = [_residual_entry(db, r) for r in residuals if r["residual_usd"] > 0]

    gross_obligations_usd = round(sum(r["total_usd"] for r in residuals), 2)
    total_matched_usd = round(sum(float(m.matched_amount_usd) for m in matches), 2)
    net_settlement_usd = round(sum(r["residual_usd"] for r in residuals), 2)
    fx_friction_savings_usd = round(total_matched_usd * FRICTION_RATE, 2)
    auto_eligible_count = sum(1 for e in match_entries if e["eligibility_flag"] != ELIGIBILITY_NEEDS_REVIEW)
    needs_review_count = len(flagged_matches)

    body = {
        "netting_run_id": str(run.id),
        "executed_at": run.executed_at.isoformat(),
        "summary": {
            "gross_obligations_usd": gross_obligations_usd,
            "total_matched_usd": total_matched_usd,
            "net_settlement_usd": net_settlement_usd,
            "fx_friction_savings_usd": fx_friction_savings_usd,
            "matches_count": len(match_entries),
            "auto_eligible_count": auto_eligible_count,
            "needs_review_count": needs_review_count,
            "flagged_residual_count": len(residual_entries),
        },
        "matches": match_entries,
        "flagged_for_review": {
            "needs_review_matches": flagged_matches,
            "residual_obligations": residual_entries,
        },
    }

    # Atomic upsert: two near-simultaneous requests for the same run's packet (e.g. React's
    # dev-mode double effect invocation) must not race a SELECT-then-INSERT against the
    # netting_run_id unique constraint. ON CONFLICT DO UPDATE resolves this at the DB level.
    values = {
        "netting_run_id": netting_run_id,
        "gross_obligations_usd": gross_obligations_usd,
        "total_matched_usd": total_matched_usd,
        "net_settlement_usd": net_settlement_usd,
        "fx_friction_savings_usd": fx_friction_savings_usd,
        "matches_count": len(match_entries),
        "auto_eligible_count": auto_eligible_count,
        "needs_review_count": needs_review_count,
        "body": body,
    }
    stmt = pg_insert(BankPacket).values(**values)
    stmt = stmt.on_conflict_do_update(
        index_elements=[BankPacket.netting_run_id],
        set_={k: v for k, v in values.items() if k != "netting_run_id"},
    )
    db.execute(stmt)
    db.flush()

    return db.execute(
        select(BankPacket).where(BankPacket.netting_run_id == netting_run_id)
    ).scalar_one()
