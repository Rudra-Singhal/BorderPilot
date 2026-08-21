"""Phase 6 checks: bank-facing output packet (M6).

Netting runs operate over the *whole* obligations pool by design (that's the
point of pooled netting), so rather than trying to isolate a clean subset of
data, these tests verify the packet's internal arithmetic invariants against
whatever a real run produces. Bedrock is mocked, same as test_explain.py.
"""

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db.session import SessionLocal
from app.services.explain import ELIGIBILITY_NEEDS_REVIEW
from app.services.netting import run_netting
from app.services.packet import FRICTION_RATE, build_packet


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def _bedrock_response(text: str):
    body = MagicMock()
    body.read.return_value = json.dumps({"content": [{"text": text}]}).encode()
    return {"body": body}


@pytest.fixture
def mocked_bedrock():
    with patch("app.services.explain.boto3.client") as mock_boto_client:
        mock_client = MagicMock()
        mock_client.invoke_model.return_value = _bedrock_response("Mocked justification.")
        mock_boto_client.return_value = mock_client
        yield


def test_build_packet_raises_for_unknown_run(db):
    with pytest.raises(ValueError):
        build_packet(db, uuid.uuid4())


def test_build_packet_arithmetic_invariants(db, mocked_bedrock):
    run = run_netting(db)
    packet = build_packet(db, run.id)

    assert packet.matches_count == run.matches_created
    assert packet.total_matched_usd == round(sum(m["matched_amount_usd"] for m in packet.body["matches"]), 2)
    # netting removes the matched amount from both the payable and receivable leg
    assert packet.net_settlement_usd == pytest.approx(
        packet.gross_obligations_usd - 2 * packet.total_matched_usd, abs=0.02
    )
    assert packet.fx_friction_savings_usd == round(packet.total_matched_usd * FRICTION_RATE, 2)
    assert packet.auto_eligible_count + packet.needs_review_count == packet.matches_count


def test_flagged_section_only_contains_needs_review_and_positive_residuals(db, mocked_bedrock):
    run = run_netting(db)
    packet = build_packet(db, run.id)

    flagged = packet.body["flagged_for_review"]
    assert all(m["eligibility_flag"] == ELIGIBILITY_NEEDS_REVIEW for m in flagged["needs_review_matches"])
    assert all(r["residual_usd"] > 0 for r in flagged["residual_obligations"])
    # auto-eligible matches must not leak into the flagged list
    flagged_ids = {m["match_id"] for m in flagged["needs_review_matches"]}
    auto_eligible_ids = {
        m["match_id"] for m in packet.body["matches"] if m["eligibility_flag"] != ELIGIBILITY_NEEDS_REVIEW
    }
    assert flagged_ids.isdisjoint(auto_eligible_ids)


def test_build_packet_upserts_same_row_on_regenerate(db, mocked_bedrock):
    run = run_netting(db)
    first = build_packet(db, run.id)
    first_id = first.id

    second = build_packet(db, run.id)

    assert second.id == first_id  # same packet row, not a duplicate
