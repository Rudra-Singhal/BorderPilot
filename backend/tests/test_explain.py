"""Phase 5 checks: AI match explanation layer (M5 completion).

Bedrock calls are mocked here so the suite stays fast, free, and independent
of live AWS credentials -- live verification against the real model is a
manual test checklist step, not part of CI.
"""

import json
import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.db.session import SessionLocal
from app.models import SME, Counterparty, PaymentEvent
from app.services.explain import (
    build_counterparty_context,
    eligibility_flag_for_tier,
    generate_justification,
)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


BASE_CONTEXT = {
    "counterparty_name": "Test Traders",
    "counterparty_country": "US",
    "tier": "B",
    "score": 75.0,
    "transaction_count": 8,
    "on_time_ratio_pct": 90.0,
    "median_delay_days": 0.0,
    "payable_sme_name": "SME Alpha",
    "receivable_sme_name": "SME Beta",
    "matched_amount_usd": 1000.0,
}


def _bedrock_response(text: str):
    body = MagicMock()
    body.read.return_value = json.dumps({"content": [{"text": text}]}).encode()
    return {"body": body}


def test_eligibility_flag_for_tier():
    assert eligibility_flag_for_tier("A") == "auto_eligible"
    assert eligibility_flag_for_tier("B") == "auto_eligible"
    assert eligibility_flag_for_tier("C") == "needs_review"
    assert eligibility_flag_for_tier("D") == "needs_review"
    assert eligibility_flag_for_tier("E") == "needs_review"


@patch("app.services.explain.boto3.client")
def test_generate_justification_success(mock_boto_client):
    mock_client = MagicMock()
    mock_client.invoke_model.return_value = _bedrock_response("A clean, factual justification.")
    mock_boto_client.return_value = mock_client

    text, ai_generated = generate_justification(BASE_CONTEXT)

    assert ai_generated is True
    assert text == "A clean, factual justification."
    call_kwargs = mock_client.invoke_model.call_args.kwargs
    body = json.loads(call_kwargs["body"])
    assert "Test Traders" in body["messages"][0]["content"]
    assert "1000.0" in body["messages"][0]["content"]


@patch("app.services.explain.boto3.client")
def test_generate_justification_falls_back_on_bedrock_error(mock_boto_client):
    mock_client = MagicMock()
    mock_client.invoke_model.side_effect = Exception("simulated Bedrock outage")
    mock_boto_client.return_value = mock_client

    text, ai_generated = generate_justification(BASE_CONTEXT)

    assert ai_generated is False
    assert "Test Traders" in text
    assert "1000.0" in text  # fallback template still uses the real facts, no crash


@patch("app.services.explain.boto3.client")
def test_generate_justification_falls_back_on_empty_completion(mock_boto_client):
    mock_client = MagicMock()
    mock_client.invoke_model.return_value = _bedrock_response("")
    mock_boto_client.return_value = mock_client

    text, ai_generated = generate_justification(BASE_CONTEXT)

    assert ai_generated is False
    assert text  # non-empty fallback, not blank


def test_fallback_mentions_no_history_when_profile_missing():
    context = dict(BASE_CONTEXT, transaction_count=0, on_time_ratio_pct=None, median_delay_days=None)
    with patch("app.services.explain.boto3.client") as mock_boto_client:
        mock_boto_client.side_effect = Exception("no creds")
        text, ai_generated = generate_justification(context)
    assert ai_generated is False
    assert "no recorded payment history" in text


def _make_sme(db) -> SME:
    sme = SME(id=uuid.uuid4(), name=f"Test SME {uuid.uuid4()}", country="US", base_currency="USD")
    db.add(sme)
    db.flush()
    return sme


def _make_counterparty(db) -> Counterparty:
    cp = Counterparty(id=uuid.uuid4(), name=f"Test Counterparty {uuid.uuid4()}", country="US")
    db.add(cp)
    db.flush()
    return cp


def test_build_counterparty_context_reflects_real_profile_and_score(db):
    cp = _make_counterparty(db)
    sme = _make_sme(db)
    for _ in range(5):
        db.add(
            PaymentEvent(
                counterparty_id=cp.id,
                sme_id=sme.id,
                due_date=date(2026, 1, 1),
                paid_date=date(2026, 1, 1),
                amount=100,
                currency="USD",
            )
        )
    db.flush()

    context = build_counterparty_context(db, cp.id)

    assert context["counterparty_name"] == cp.name
    assert context["transaction_count"] == 5
    assert context["on_time_ratio_pct"] == 100.0
    assert context["tier"] in {"A", "B", "C", "D", "E"}
