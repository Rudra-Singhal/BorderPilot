# Phase 3 — Reliability Scoring (M4, narrowed): Manual Test Checklist

Deterministic formula: counterparty behavior (M3, weight 0.7) + corridor country-risk (weight 0.3) for
counterparty-level scores; behavior (0.5) + corridor pair (0.2) + obligation-size signal (0.15) +
SME-obligation-count signal (0.15) for per-obligation scores. Tiers: A≥85, B≥70, C≥55, D≥40, E<40.
No advance-rate, pricing, or approve/reject logic — tier only. See `app/services/scoring.py` for the
full formula (weights/thresholds are named constants).

Endpoints: `GET/POST /reliability-scores/counterparty/{id}[/recompute]`, `GET .../counterparty/{id}/history`,
`GET/POST /reliability-scores/obligation/{id}[/recompute]`, `POST /reliability-scores/counterparty/recompute-all`.

- [x] Recompute scores after Phase 2's new PaymentEvent, confirm tier for that counterparty moves in the
      expected direction — added 10 on-time PaymentEvents to Harbor Logistics: score moved **56.49 (tier C) →
      83.52 (tier B)**, confirmed by hand: `0.7×82.89 (behavior) + 0.3×85 (SG corridor) = 83.52`
- [x] Confirm a counterparty with poor/sparse history lands in a lower tier (C/D/E) — 11 of 12 seeded
      counterparties land in C/D/E after the initial recompute; Global Retail Corp (carrying the deliberately
      30-days-late event from Phase 2's cross-SME test) scored 27.0 / tier E
- [x] Confirm scoring is deterministic — same input data produces same score on repeated runs — recomputed
      Harbor Logistics twice back-to-back with no data change: `56.49` both times (version incremented, score
      identical)
- [x] Spot check 3–4 counterparties by hand against the formula — verified Global Retail Corp, Sunrise
      Distribution, and Harbor Logistics (before and after) match the documented weights exactly
- [x] Per-obligation score computes without crashing when there are no comparable obligations for that
      counterparty to compare against (neutral obligation-signal fallback, not a divide-by-zero)
- [x] Automated coverage: `tests/test_scoring.py` — 5 tests covering tier boundaries, neutral score on no
      history, determinism, score direction on improved history, and the no-comparable-obligations edge case.
      Full suite 13/13 passing. DB row counts confirmed unchanged by the test run (flush+rollback pattern).

**Result:** PASS — Phase 3 complete, proceed to Phase 4.
