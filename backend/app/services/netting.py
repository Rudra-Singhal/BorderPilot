"""M5 core: builds a graph from open Obligations pooled across all SMEs, normalizes
currency, buckets by settlement date, and greedily nets payables (SME owes the
counterparty) against receivables (counterparty owes an SME) that share the same
pooled counterparty and settlement window. Unmatched obligations are left as-is --
never force-matched. A run never mutates Obligation rows, so it is a repeatable,
side-effect-free proposal, not a settlement action.
"""

import uuid
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import NettingRun, Obligation, OffsetMatch
from app.models.obligation import ObligationDirection, ObligationStatus

# Static FX table (rate to USD). No live FX API for this build pass -- snapshotted
# onto each NettingRun so historic runs stay self-describing if the table changes.
FX_TO_USD = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "INR": 0.012,
    "SEK": 0.095,
    "SGD": 0.74,
    "COP": 0.00025,
}

SETTLEMENT_BUCKET_DAYS = 14
BUCKET_EPOCH = date(2026, 1, 1)  # fixed reference so bucket indices are stable across runs
DUST_THRESHOLD_USD = 0.01  # ignore residuals below this when deciding a leg is exhausted


def to_usd(amount: float, currency: str) -> float:
    rate = FX_TO_USD.get(currency)
    if rate is None:
        raise ValueError(f"No FX rate configured for currency {currency}")
    return float(amount) * rate


def settlement_bucket_index(settlement_date: date) -> int:
    return (settlement_date - BUCKET_EPOCH).days // SETTLEMENT_BUCKET_DAYS


def bucket_bounds(bucket_index: int) -> tuple[date, date]:
    start = BUCKET_EPOCH + timedelta(days=bucket_index * SETTLEMENT_BUCKET_DAYS)
    end = start + timedelta(days=SETTLEMENT_BUCKET_DAYS - 1)
    return start, end


def is_eligible_for_netting(obligation: Obligation) -> bool:
    """Static compliance-eligibility gate: only OPEN obligations in a currency we
    can normalize are considered. Everything else never enters the graph."""
    return obligation.status == ObligationStatus.OPEN and obligation.currency in FX_TO_USD


def _build_groups(obligations: list[Obligation]) -> dict[tuple[int, uuid.UUID], dict[str, list]]:
    groups: dict[tuple[int, uuid.UUID], dict[str, list]] = defaultdict(lambda: {"payable": [], "receivable": []})
    for ob in obligations:
        bucket = settlement_bucket_index(ob.expected_settlement_date)
        key = (bucket, ob.counterparty_id)
        entry = {"obligation": ob, "remaining_usd": to_usd(ob.amount, ob.currency)}
        side = "payable" if ob.direction == ObligationDirection.PAYABLE else "receivable"
        groups[key][side].append(entry)
    return groups


def _match_group(payables: list[dict], receivables: list[dict], bucket: int, counterparty_id: uuid.UUID) -> list[dict]:
    # Deterministic order: largest remaining first, id as tie-break -- independent of DB/query ordering.
    payables = sorted(payables, key=lambda e: (-e["remaining_usd"], str(e["obligation"].id)))
    receivables = sorted(receivables, key=lambda e: (-e["remaining_usd"], str(e["obligation"].id)))

    matches = []
    i, j = 0, 0
    while i < len(payables) and j < len(receivables):
        payable, receivable = payables[i], receivables[j]
        matched = min(payable["remaining_usd"], receivable["remaining_usd"])
        if matched > DUST_THRESHOLD_USD:
            matches.append(
                {
                    "bucket": bucket,
                    "counterparty_id": counterparty_id,
                    "payable_obligation_id": payable["obligation"].id,
                    "receivable_obligation_id": receivable["obligation"].id,
                    "matched_amount_usd": round(matched, 2),
                }
            )
        payable["remaining_usd"] -= matched
        receivable["remaining_usd"] -= matched
        if payable["remaining_usd"] <= DUST_THRESHOLD_USD:
            i += 1
        if receivable["remaining_usd"] <= DUST_THRESHOLD_USD:
            j += 1

    return matches


def compute_matches(obligations: list[Obligation]) -> list[dict]:
    """Pure function (no DB writes) -- easy to unit test and to re-run for
    determinism checks without side effects."""
    groups = _build_groups(obligations)
    matches = []
    for (bucket, counterparty_id), sides in groups.items():
        matches.extend(_match_group(sides["payable"], sides["receivable"], bucket, counterparty_id))

    matches.sort(
        key=lambda m: (
            m["bucket"],
            str(m["counterparty_id"]),
            str(m["payable_obligation_id"]),
            str(m["receivable_obligation_id"]),
        )
    )
    return matches


def run_netting(db: Session) -> NettingRun:
    obligations = db.execute(select(Obligation).order_by(Obligation.id)).scalars().all()
    eligible = [ob for ob in obligations if is_eligible_for_netting(ob)]
    matches = compute_matches(eligible)

    run = NettingRun(
        window_days=SETTLEMENT_BUCKET_DAYS,
        obligations_considered=len(eligible),
        matches_created=len(matches),
        fx_snapshot=FX_TO_USD,
    )
    db.add(run)
    db.flush()

    for m in matches:
        start, end = bucket_bounds(m["bucket"])
        db.add(
            OffsetMatch(
                netting_run_id=run.id,
                counterparty_id=m["counterparty_id"],
                payable_obligation_id=m["payable_obligation_id"],
                receivable_obligation_id=m["receivable_obligation_id"],
                settlement_bucket_start=start,
                settlement_bucket_end=end,
                matched_amount_usd=m["matched_amount_usd"],
            )
        )

    db.flush()
    return run


def compute_residuals(db: Session, netting_run_id: uuid.UUID) -> list[dict]:
    """For every obligation considered in a run, how much of it (in USD) was
    matched vs left over. Used to surface 'no viable counterpart' obligations
    and will feed M6's flagged/unmatched section."""
    run = db.get(NettingRun, netting_run_id)
    if run is None:
        raise ValueError(f"NettingRun {netting_run_id} not found")

    obligations = db.execute(select(Obligation).order_by(Obligation.id)).scalars().all()
    eligible = {ob.id: ob for ob in obligations if is_eligible_for_netting(ob)}

    matched_usd: dict[uuid.UUID, float] = defaultdict(float)
    match_rows = db.execute(
        select(OffsetMatch).where(OffsetMatch.netting_run_id == netting_run_id)
    ).scalars().all()
    for match in match_rows:
        matched_usd[match.payable_obligation_id] += float(match.matched_amount_usd)
        matched_usd[match.receivable_obligation_id] += float(match.matched_amount_usd)

    residuals = []
    for ob in eligible.values():
        total_usd = to_usd(ob.amount, ob.currency)
        matched = matched_usd.get(ob.id, 0.0)
        residual = round(total_usd - matched, 2)
        residuals.append(
            {
                "obligation_id": ob.id,
                "sme_id": ob.sme_id,
                "counterparty_id": ob.counterparty_id,
                "direction": ob.direction,
                "total_usd": round(total_usd, 2),
                "matched_usd": round(matched, 2),
                "residual_usd": max(0.0, residual),
                "fully_matched": residual <= DUST_THRESHOLD_USD,
            }
        )
    return residuals
