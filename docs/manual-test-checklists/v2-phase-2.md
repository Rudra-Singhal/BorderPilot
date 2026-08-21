# v2 Phase 2 — Data Foundation: Manual Test Checklist

Deliverables: 10 new models + migration (`Invoice`, `BankNBFCPartner`, `UnderwritingDecision`,
`FinancingOffer`, `FinancingAgreement`, `Settlement`, `ComplianceRequirement`, `LiquidityEvent`,
`CurrencyExposure`, `AuditEvent`); `Obligation.invoice_id` FK; read APIs (`/invoices`, `/bank-partners`,
`/entities/counts`); a full seed rewrite to the reference §24 scale replacing the old 6/12/17 dataset; and
`reset.py` updated for the new tables. Aligns the data model with the reference spec's §23 (with the
plan-approved deltas: no separate `Transaction` wrapper — `Invoice` + `Obligation` cover it; `NettingRun`
kept over the spec's `NettingOpportunity` naming; both noted).

- [x] All 10 new tables + `obligations.invoice_id` created via one Alembic migration — autogenerate
      detected every table and the FK; hit the classic shared-enum bug (Alembic tried to re-`CREATE TYPE
      obligationdirection`, reused by `Invoice`) and fixed it with `postgresql.ENUM(..., create_type=False)`;
      migration now applies cleanly from the prior head
- [x] `reset.py` drops all 19 tables in FK-safe order and reseeds without error
- [x] Every new table is queryable via API — `GET /entities/counts` returns row counts for all 18 tracked
      tables (seeded ones populated, engine-populated ones correctly at 0); `GET /invoices` and
      `GET /bank-partners` return typed seeded data
- [x] Dataset hits §24 scale: **8 SMEs, 15 counterparties** across 6 countries (DE/US/GB/AE/VN/NL), 4
      currencies (EUR/USD/GBP/INR), **273 payment events**, 21 open obligations each backed by an Invoice, 2
      lender partners
- [x] **Hero pooling number is real**: Schmidt Industrial GmbH computes to **94 payment events across 6
      distinct SMEs**, 91.5% on-time — verified via SQL and the behavior-profile endpoint. This is the
      "no single lender sees this much history" moment, driven by actual seeded data, not a hardcoded number.
- [x] Archetypes visibly differentiate the reliability score: tier distribution across the 15 buyers is
      A:1, B:5, C:4, D:5 — reliable/moderate/unreliable buyers land in distinct tiers
- [x] 2 thin-data buyers (<5 events: Delta Materials NV, Emirates Auto Parts) exist for the
      confidence-multiplier story; one risky corridor (Vietnam→India) and one high-concentration SME
      (Indus Leatherworks) present
- [x] **Netting produces 6 matches** on the new seed (target was 4+), including the hero (Schmidt €30k
      payable → $32,400 matched against Raj's €50k receivable) and a Tier A match. Fixed a real flaw found
      here: several hand-crafted scenario dates straddled the engine's 14-day bucket boundaries, silently
      breaking intended matches — re-picked all dates mid-bucket.
- [x] Seed is idempotent (re-run seeds 0 new rows, counts unchanged) and deterministic (fixed RNG seed)
- [x] Hero invoice `INV-0001` (Raj Exports → Schmidt, EUR 50,000, due 2026-10-05) exists and links to an
      obligation; every open obligation is invoice-backed (0 unlinked)
- [x] Frontend regression check: Receivables page renders the new dataset correctly (Raj Exports, Schmidt,
      new buyers, live tiers) — API contracts unchanged, no frontend changes needed
- [x] Automated coverage: `tests/test_seed_v2.py` (4 tests: scale, Schmidt 6-SME pooling, thin-data buyers,
      hero invoice + obligation linkage). Full suite **37/37 passing**.

## Scoring note (deferred to Phase 3, by design)

Schmidt currently scores **Tier B (78.6)**, not Tier A, under the *old* 0.7/0.3 counterparty formula —
its high delay variance (a few significant-late events in the synthetic history) drags the score via the
variance penalty. Re-tuning to the reference's 45/25/15/15 weighting (so a 94-transaction, 91.5%-on-time
reliable buyer lands Tier A) is an explicit **Phase 3** deliverable (Core Financial Engines). The Phase 2
data is correct; the scoring formula is Phase 3's job.

**Result:** PASS — Phase 2 complete. Proceed to Phase 3 (Core Financial Engines).
