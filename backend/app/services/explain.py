"""M5 completion: AI-assisted match explanation via AWS Bedrock, plus the
confidence/eligibility flag derived from M4's reliability tier.

The prompt is deliberately constrained: the model is handed a fixed set of
facts (M3's pooled behavior profile, M4's tier, and the match's own numbers)
and told to restate only those -- never to invent a number, date, or claim
that isn't in the input. If Bedrock is unreachable or misconfigured, a
netting run must still complete, so generation falls back to a deterministic
template rather than raising.
"""

import json
import logging
import uuid

import boto3
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import SME, Counterparty, Obligation, PaymentBehaviorProfile
from app.services.scoring import compute_counterparty_score

logger = logging.getLogger(__name__)

AUTO_ELIGIBLE_TIERS = {"A", "B"}
ELIGIBILITY_AUTO = "auto_eligible"
ELIGIBILITY_NEEDS_REVIEW = "needs_review"

SYSTEM_PROMPT = (
    "You write a one-to-two sentence justification for a proposed netting match, for a report "
    "a bank will read. Use ONLY the facts given to you in the message -- never invent a number, "
    "date, or claim that is not explicitly provided. Do not give financial or investment advice. "
    "Be factual, concise, and plain -- no marketing language."
)


def eligibility_flag_for_tier(tier: str) -> str:
    return ELIGIBILITY_AUTO if tier in AUTO_ELIGIBLE_TIERS else ELIGIBILITY_NEEDS_REVIEW


def build_counterparty_context(db: Session, counterparty_id: uuid.UUID) -> dict:
    """Facts about the shared counterparty a match routes through: M4's tier/score and
    M3's pooled behavior profile. Independent of which specific obligations are being matched."""
    counterparty = db.get(Counterparty, counterparty_id)
    score_row = compute_counterparty_score(db, counterparty_id)  # also refreshes the M3 profile
    profile = db.execute(
        select(PaymentBehaviorProfile).where(PaymentBehaviorProfile.counterparty_id == counterparty_id)
    ).scalar_one_or_none()

    return {
        "counterparty_name": counterparty.name,
        "counterparty_country": counterparty.country,
        "tier": score_row.tier,
        "score": score_row.score,
        "transaction_count": profile.transaction_count if profile else 0,
        "on_time_ratio_pct": round(profile.on_time_ratio * 100, 1) if profile else None,
        "median_delay_days": profile.median_delay_days if profile else None,
    }


def _build_user_prompt(context: dict) -> str:
    if context["transaction_count"] > 0:
        history_line = (
            f"Pooled payment history: {context['transaction_count']} recorded payments across all SMEs "
            f"linked to this counterparty, {context['on_time_ratio_pct']}% on time, "
            f"median delay {context['median_delay_days']} days"
        )
    else:
        history_line = "Pooled payment history: no recorded payments yet for this counterparty"

    return (
        f"Counterparty: {context['counterparty_name']} ({context['counterparty_country']})\n"
        f"Reliability tier: {context['tier']} (score {context['score']}/100)\n"
        f"{history_line}\n"
        f"Proposed match: {context['payable_sme_name']} owes {context['counterparty_name']}, which "
        f"separately owes {context['receivable_sme_name']}\n"
        f"Matched amount: {context['matched_amount_usd']} USD-equivalent\n\n"
        "Write a 1-2 sentence justification for why this net match is reasonable, using only the "
        "facts above."
    )


def _fallback_justification(context: dict) -> str:
    if context["transaction_count"] > 0:
        history = (
            f"{context['transaction_count']} pooled payment records at a "
            f"{context['on_time_ratio_pct']}% on-time rate"
        )
    else:
        history = "no recorded payment history yet"
    return (
        f"Nets a {context['matched_amount_usd']} USD-equivalent obligation between "
        f"{context['payable_sme_name']} and {context['receivable_sme_name']} through "
        f"{context['counterparty_name']} (tier {context['tier']}), based on {history}."
    )


def generate_justification(context: dict) -> tuple[str, bool]:
    """Returns (justification_text, ai_generated). Never raises -- falls back to a
    deterministic template on any Bedrock failure so a netting run always completes."""
    try:
        client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 150,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": _build_user_prompt(context)}],
            }
        )
        response = client.invoke_model(modelId=settings.bedrock_model_id, body=body)
        payload = json.loads(response["body"].read())
        text = payload["content"][0]["text"].strip()
        if not text:
            raise ValueError("empty completion from Bedrock")
        return text, True
    except Exception:
        logger.exception("Bedrock justification generation failed; using fallback template")
        return _fallback_justification(context), False
