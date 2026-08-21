"""Phase 4 checks: netting engine core (M5).

compute_matches() is a pure function over in-memory Obligation objects, so
these tests don't need the DB at all -- fast and fully isolated.
"""

import uuid
from datetime import date

from app.models import Obligation
from app.models.obligation import ObligationDirection, ObligationStatus
from app.services.netting import (
    compute_matches,
    is_eligible_for_netting,
    settlement_bucket_index,
    to_usd,
)

CP_A = uuid.uuid4()
CP_B = uuid.uuid4()
SME_1 = uuid.uuid4()
SME_2 = uuid.uuid4()
SME_3 = uuid.uuid4()


def _ob(counterparty_id, sme_id, direction, amount, currency, settlement_date, status=ObligationStatus.OPEN):
    return Obligation(
        id=uuid.uuid4(),
        sme_id=sme_id,
        counterparty_id=counterparty_id,
        direction=direction,
        amount=amount,
        currency=currency,
        expected_settlement_date=settlement_date,
        status=status,
    )


def test_simple_bilateral_match_same_bucket():
    d = date(2026, 1, 5)
    payable = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 1000, "USD", d)
    receivable = _ob(CP_A, SME_2, ObligationDirection.RECEIVABLE, 1000, "USD", d)

    matches = compute_matches([payable, receivable])

    assert len(matches) == 1
    assert matches[0]["payable_obligation_id"] == payable.id
    assert matches[0]["receivable_obligation_id"] == receivable.id
    assert matches[0]["matched_amount_usd"] == 1000.0


def test_cross_currency_normalization():
    d = date(2026, 1, 5)
    payable = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 1000, "GBP", d)  # 1000 * 1.27 = 1270 USD
    receivable = _ob(CP_A, SME_2, ObligationDirection.RECEIVABLE, 500, "EUR", d)  # 500 * 1.08 = 540 USD

    matches = compute_matches([payable, receivable])

    assert len(matches) == 1
    assert matches[0]["matched_amount_usd"] == 540.0  # smaller side fully consumed


def test_partial_match_leaves_correct_residual():
    d = date(2026, 1, 5)
    payable = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 1000, "USD", d)
    receivable = _ob(CP_A, SME_2, ObligationDirection.RECEIVABLE, 400, "USD", d)

    matches = compute_matches([payable, receivable])

    assert len(matches) == 1
    assert matches[0]["matched_amount_usd"] == 400.0  # residual of 600 on the payable is implicit (untouched)


def test_obligations_outside_bucket_window_do_not_match():
    payable = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 1000, "USD", date(2026, 1, 1))
    receivable = _ob(CP_A, SME_2, ObligationDirection.RECEIVABLE, 1000, "USD", date(2026, 3, 1))
    assert settlement_bucket_index(date(2026, 1, 1)) != settlement_bucket_index(date(2026, 3, 1))

    matches = compute_matches([payable, receivable])

    assert matches == []


def test_multilateral_one_payable_splits_across_two_receivables():
    d = date(2026, 1, 5)
    payable = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 1000, "USD", d)
    receivable_a = _ob(CP_A, SME_2, ObligationDirection.RECEIVABLE, 600, "USD", d)
    receivable_b = _ob(CP_A, SME_3, ObligationDirection.RECEIVABLE, 400, "USD", d)

    matches = compute_matches([payable, receivable_a, receivable_b])

    assert len(matches) == 2
    assert {m["receivable_obligation_id"] for m in matches} == {receivable_a.id, receivable_b.id}
    assert all(m["payable_obligation_id"] == payable.id for m in matches)
    assert sum(m["matched_amount_usd"] for m in matches) == 1000.0


def test_no_viable_counterpart_left_unmatched():
    d = date(2026, 1, 5)
    payable = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 1000, "USD", d)
    unrelated_receivable = _ob(CP_B, SME_2, ObligationDirection.RECEIVABLE, 1000, "USD", d)  # different counterparty

    matches = compute_matches([payable, unrelated_receivable])

    assert matches == []


def test_compute_matches_is_deterministic():
    d = date(2026, 1, 5)
    obligations = [
        _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 1000, "USD", d),
        _ob(CP_A, SME_2, ObligationDirection.RECEIVABLE, 600, "USD", d),
        _ob(CP_A, SME_3, ObligationDirection.RECEIVABLE, 400, "USD", d),
    ]

    first = compute_matches(obligations)
    second = compute_matches(obligations)

    assert first == second


def test_is_eligible_for_netting_filters_status_and_currency():
    d = date(2026, 1, 5)
    open_ob = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 100, "USD", d, status=ObligationStatus.OPEN)
    settled_ob = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 100, "USD", d, status=ObligationStatus.SETTLED)
    unknown_currency_ob = _ob(CP_A, SME_1, ObligationDirection.PAYABLE, 100, "XYZ", d, status=ObligationStatus.OPEN)

    assert is_eligible_for_netting(open_ob) is True
    assert is_eligible_for_netting(settled_ob) is False
    assert is_eligible_for_netting(unknown_currency_ob) is False


def test_to_usd_known_and_unknown_currency():
    assert to_usd(100, "USD") == 100.0
    assert to_usd(100, "GBP") == 127.0
    try:
        to_usd(100, "XYZ")
        assert False, "expected ValueError for unconfigured currency"
    except ValueError:
        pass
