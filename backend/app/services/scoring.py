"""M4 (narrowed): deterministic reliability scoring — counterparty + receivable
+ corridor + SME signal -> score (0-100) + tier (A-E). No advance-rate, pricing,
or approve/reject logic; the tier is a netting-confidence input for M5.

All weights/thresholds are named constants so a human can spot-check the math
by hand against the manual test checklist.
"""

import uuid
from statistics import median

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Counterparty, Obligation, PaymentBehaviorProfile, ReliabilityScore, SME
from app.services.behavior import recompute_profile

# Static corridor risk lookup (0-100, higher = lower perceived cross-border friction/risk).
# Deliberately coarse — this is a placeholder signal, not a real country-risk model.
COUNTRY_RISK = {
    "US": 90.0, "GB": 88.0, "DE": 88.0, "SE": 85.0, "SG": 85.0,
    "LT": 80.0, "IN": 70.0, "CO": 65.0,
}
DEFAULT_COUNTRY_RISK = 55.0

NEUTRAL_SCORE = 50.0  # used when there isn't enough data to say anything either way

# Counterparty-level score weights (no specific obligation involved)
CP_WEIGHT_BEHAVIOR = 0.7
CP_WEIGHT_CORRIDOR = 0.3

# Obligation-level score weights (adds receivable-quality + SME signal)
OB_WEIGHT_BEHAVIOR = 0.5
OB_WEIGHT_CORRIDOR = 0.2
OB_WEIGHT_OBLIGATION_SIGNAL = 0.15
OB_WEIGHT_SME_SIGNAL = 0.15

TIER_THRESHOLDS = [("A", 85.0), ("B", 70.0), ("C", 55.0), ("D", 40.0), ("E", 0.0)]


def tier_from_score(score: float) -> str:
    for tier, threshold in TIER_THRESHOLDS:
        if score >= threshold:
            return tier
    return "E"


def _behavior_score(profile: PaymentBehaviorProfile | None) -> tuple[float, dict]:
    """On-time ratio, penalized for delay variance, shrunk toward neutral when
    transaction history is thin (regression to the mean at low sample size)."""
    if profile is None:
        return NEUTRAL_SCORE, {"reason": "no_payment_history"}

    raw = profile.on_time_ratio * 100.0
    variance_penalty = min(25.0, (profile.delay_variance**0.5) * 3.0)
    raw = max(0.0, min(100.0, raw - variance_penalty))

    confidence = min(1.0, profile.transaction_count / 10.0)
    shrunk = confidence * raw + (1 - confidence) * NEUTRAL_SCORE

    return shrunk, {
        "on_time_ratio": profile.on_time_ratio,
        "variance_penalty": round(variance_penalty, 2),
        "raw_score": round(raw, 2),
        "confidence": round(confidence, 2),
        "transaction_count": profile.transaction_count,
    }


def _corridor_score_country(country: str) -> float:
    return COUNTRY_RISK.get(country, DEFAULT_COUNTRY_RISK)


def _corridor_score_pair(sme_country: str, counterparty_country: str) -> float:
    return (
        COUNTRY_RISK.get(sme_country, DEFAULT_COUNTRY_RISK)
        + COUNTRY_RISK.get(counterparty_country, DEFAULT_COUNTRY_RISK)
    ) / 2.0


def _obligation_signal_score(db: Session, obligation: Obligation) -> tuple[float, dict]:
    """Flags obligations that are large outliers relative to this counterparty's
    typical obligation size — less evidence backs an unusually large amount."""
    others = db.execute(
        select(Obligation.amount).where(
            Obligation.counterparty_id == obligation.counterparty_id,
            Obligation.id != obligation.id,
        )
    ).scalars().all()
    if not others:
        return 60.0, {"reason": "no_comparable_obligations"}

    typical = float(median(others))
    ratio = float(obligation.amount) / typical if typical > 0 else 1.0
    if ratio <= 1.5:
        score = 90.0
    elif ratio <= 3.0:
        score = 70.0
    else:
        score = 50.0

    return score, {"typical_amount": round(typical, 2), "amount_ratio": round(ratio, 2)}


def _sme_signal_score(db: Session, sme_id: uuid.UUID) -> tuple[float, dict]:
    """Proxy for how established the SME's data trail is on the platform: more
    recorded obligations -> more confidence in the surrounding signals."""
    n = db.execute(
        select(func.count()).select_from(Obligation).where(Obligation.sme_id == sme_id)
    ).scalar()
    score = min(100.0, 50.0 + n * 5.0)
    return score, {"sme_obligation_count": n}


def _next_version(db: Session, counterparty_id: uuid.UUID, obligation_id: uuid.UUID | None) -> int:
    existing = db.execute(
        select(ReliabilityScore.version)
        .where(
            ReliabilityScore.counterparty_id == counterparty_id,
            ReliabilityScore.obligation_id == obligation_id,
        )
        .order_by(ReliabilityScore.version.desc())
        .limit(1)
    ).scalar_one_or_none()
    return (existing or 0) + 1


def compute_counterparty_score(db: Session, counterparty_id: uuid.UUID) -> ReliabilityScore:
    counterparty = db.get(Counterparty, counterparty_id)
    if counterparty is None:
        raise ValueError(f"Counterparty {counterparty_id} not found")

    profile = recompute_profile(db, counterparty_id)  # ensure freshness (Phase 2 service)
    behavior, behavior_factors = _behavior_score(profile)
    corridor = _corridor_score_country(counterparty.country)

    score = CP_WEIGHT_BEHAVIOR * behavior + CP_WEIGHT_CORRIDOR * corridor
    tier = tier_from_score(score)

    row = ReliabilityScore(
        counterparty_id=counterparty_id,
        obligation_id=None,
        score=round(score, 2),
        tier=tier,
        version=_next_version(db, counterparty_id, None),
        factors={
            "type": "counterparty",
            "weights": {"behavior": CP_WEIGHT_BEHAVIOR, "corridor": CP_WEIGHT_CORRIDOR},
            "behavior": behavior_factors,
            "behavior_score": round(behavior, 2),
            "corridor_score": round(corridor, 2),
            "corridor_country": counterparty.country,
        },
    )
    db.add(row)
    db.flush()
    return row


def compute_obligation_score(db: Session, obligation_id: uuid.UUID) -> ReliabilityScore:
    obligation = db.get(Obligation, obligation_id)
    if obligation is None:
        raise ValueError(f"Obligation {obligation_id} not found")
    counterparty = db.get(Counterparty, obligation.counterparty_id)
    sme = db.get(SME, obligation.sme_id)

    profile = recompute_profile(db, obligation.counterparty_id)
    behavior, behavior_factors = _behavior_score(profile)
    corridor = _corridor_score_pair(sme.country, counterparty.country)
    obligation_signal, obligation_factors = _obligation_signal_score(db, obligation)
    sme_signal, sme_factors = _sme_signal_score(db, obligation.sme_id)

    score = (
        OB_WEIGHT_BEHAVIOR * behavior
        + OB_WEIGHT_CORRIDOR * corridor
        + OB_WEIGHT_OBLIGATION_SIGNAL * obligation_signal
        + OB_WEIGHT_SME_SIGNAL * sme_signal
    )
    tier = tier_from_score(score)

    row = ReliabilityScore(
        counterparty_id=obligation.counterparty_id,
        obligation_id=obligation_id,
        score=round(score, 2),
        tier=tier,
        version=_next_version(db, obligation.counterparty_id, obligation_id),
        factors={
            "type": "obligation",
            "weights": {
                "behavior": OB_WEIGHT_BEHAVIOR,
                "corridor": OB_WEIGHT_CORRIDOR,
                "obligation_signal": OB_WEIGHT_OBLIGATION_SIGNAL,
                "sme_signal": OB_WEIGHT_SME_SIGNAL,
            },
            "behavior": behavior_factors,
            "behavior_score": round(behavior, 2),
            "corridor_score": round(corridor, 2),
            "corridor_pair": [sme.country, counterparty.country],
            "obligation_signal_score": round(obligation_signal, 2),
            "obligation_signal": obligation_factors,
            "sme_signal_score": round(sme_signal, 2),
            "sme_signal": sme_factors,
        },
    )
    db.add(row)
    db.flush()
    return row


def recompute_all_counterparty_scores(db: Session) -> list[ReliabilityScore]:
    counterparty_ids = db.execute(select(Counterparty.id)).scalars().all()
    rows = [compute_counterparty_score(db, cid) for cid in counterparty_ids]
    db.commit()
    return rows
