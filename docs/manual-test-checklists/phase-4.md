# Phase 4 — Netting Engine Core (M5 core): Manual Test Checklist

Algorithm: obligations are grouped by `(settlement_bucket, counterparty_id)` — 14-day buckets anchored at
a fixed epoch (2026-01-01) — then payables (SME owes counterparty) are greedily netted against receivables
(counterparty owes SME) within each group, largest-remaining-first with id tie-break for determinism.
Currency is normalized via a static FX-to-USD table. Obligations must be `OPEN` and in a supported currency
to enter the graph at all (the compliance-eligibility gate) — everything else is silently excluded, never
force-matched. A run never mutates `Obligation` rows, so it's a repeatable proposal. See `app/services/netting.py`.

Endpoints: `POST /netting-runs`, `GET /netting-runs`, `GET /netting-runs/{id}`, `GET /netting-runs/{id}/residuals`.

- [x] Run netting over seeded data, manually verify at least one match by hand — **Global Retail Corp**:
      Acme Textiles' 5000 INR receivable (→ 60.00 USD) matched against Pacific Foods' 5733 USD payable,
      `matched_amount_usd = 60.0` = `min(60, 5733)`. Confirmed by hand against `to_usd()`.
- [x] Confirm currency normalization is correct for at least one cross-currency match — same match above is
      INR↔USD; also unit-tested directly (`test_cross_currency_normalization`: 1000 GBP payable vs 500 EUR
      receivable → matched at 540.0 USD, the smaller normalized side).
- [x] Confirm a partial match produces the correct residual amount — Pacific Foods' obligation (total 5733.0
      USD) shows `matched_usd=60.0, residual_usd=5673.0, fully_matched=false` via `/residuals`; Acme's smaller
      leg shows `residual_usd=0.0, fully_matched=true`.
- [x] Confirm obligations with no viable counterpart are left unmatched, not force-matched — of 17 seeded
      obligations, 15 had `matched_usd == 0` after the first run (no same-bucket, same-counterparty opposite
      leg existed for them); confirmed via `/residuals`, no errors, no forced pairing.
- [x] Re-run netting twice on identical data, confirm deterministic/stable output — same obligation pair,
      same `matched_amount_usd = 60.0`, on two independent runs with no data change in between.
- [x] Deliberately add an obligation just outside the settlement-date bucket window, confirm it's excluded
      from that run — **naturally occurring** in the seed data: Global Retail Corp's Andes Coffee Co
      receivable (2026-09-14, bucket 18) sits one bucket away from Acme/Pacific Foods (bucket 17,
      2026-08-27→2026-09-09) despite sharing the same counterparty — confirmed excluded from the match.
      Also confirmed for Northwind Traders' own payable/receivable pair (buckets 19 vs 20).
- [x] **Multilateral proof (pooled netting, not just bilateral)**: inserted a 1000 GBP payable (Kestrel
      Electronics → Northwind Traders) and two receivables (Nordic Gears 600 GBP, Baltic Steel 400 GBP —
      Baltic Steel newly linked to Northwind Traders for this test) in the same bucket. Result: the single
      payable split across **two** `OffsetMatch` rows (508.0 + 762.0 = 1270.0 USD-equiv = 1000 GBP × 1.27),
      fully clearing all three obligations (`residual_usd = 0.0` on all three). This is the concrete "pooled,
      not just pairwise" netting result the mentor's framing is asking for.
- [x] Automated coverage: `tests/test_netting.py` — 9 tests covering bilateral match, cross-currency, partial
      residual, bucket exclusion, multilateral one-to-many split, no-viable-counterpart, determinism, and the
      eligibility gate (status + currency filters). Full suite 22/22 passing. DB row counts confirmed
      consistent with the 5 manual runs triggered during this checklist (no test pollution — `compute_matches`
      is a pure function tested without touching the DB).

**Result:** PASS — Phase 4 complete, proceed to Phase 5.
