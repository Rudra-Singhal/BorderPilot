# Phase 2 — Payment Behavior Aggregation (M3): Manual Test Checklist

Endpoints: `GET /behavior-profiles/{counterparty_id}`, `POST /behavior-profiles/recompute`, `POST /behavior-profiles/recompute/{counterparty_id}`.

- [x] Pick a shared counterparty (linked to 2+ SMEs), record its profile — Global Retail Corp (3 linked SMEs: Acme Textiles, Pacific Foods, Andes Coffee Co), profile after seed recompute: `transaction_count=9, on_time_ratio=0.111, median_delay_days=2.0, delay_variance=1.33`
- [x] Insert a new PaymentEvent for that counterparty under a **different** SME than before — inserted an event for Global Retail Corp under **Baltic Steel** (confirmed not previously linked), 30 days late
- [x] Recompute profile, confirm the numbers visibly shift — after recompute: `transaction_count=10 (was 9), on_time_ratio=0.1 (was 0.111), delay_variance=71.76 (was 1.33)`. Confirms pooling is real: a brand-new SME's transaction with a shared counterparty measurably changes that counterparty's pooled profile.
- [x] Confirm a counterparty linked to only 1 SME still computes a sane profile (no divide-by-zero, no crash on low sample size) — Sunrise Distribution (single-SME, n=3 events): profile computed cleanly (`on_time_ratio=0.333, delay_variance=2.89`), no error
- [x] Automated coverage: `tests/test_behavior.py` — 4 tests covering no-events → None, cross-SME shift, single-SME/no-crash on low sample size (n=1, variance=0.0), determinism on repeated recompute. All passing (8/8 full suite).

**Result:** PASS — Phase 2 complete, proceed to Phase 3.
