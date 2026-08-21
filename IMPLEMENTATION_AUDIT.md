# BorderPilot v2 — Implementation Audit (Phase 0)

Repository audit against the full original 8-module hackathon spec, ahead of the v2 rebuild. Companion to
`docs/SCOPE_VS_ORIGINAL_PLAN.md` (which explains *why* each gap exists); this document is the forward-
looking KEEP/MODIFY/REWRITE/DELETE/MISSING decision record for the rebuild itself.

## KEEP — real, correct, build on top of it

| Item | Why |
|---|---|
| `backend/app/services/behavior.py` | Pooled behavior aggregation is genuinely pool-wide and correct — proven in Phase 2 of the original build (profile visibly shifts when a new SME transacts with a shared counterparty) |
| `backend/app/services/netting.py` | Graph matching, FX normalization, settlement bucketing, greedy match, partial residual — the most faithful module against the original spec. Algorithm stays untouched; only its UI presentation changes (Phase 6) |
| `backend/app/services/explain.py` | Constrained-prompt Bedrock pattern with graceful fallback — the template every new AI surface (Copilot, entity resolution, document extraction, compliance language) should follow |
| `SME`, `Counterparty`, `PaymentEvent`, `PaymentBehaviorProfile`, `NettingRun`, `OffsetMatch` models | Correct shape, no changes needed |
| Docker Compose local stack, EC2 deployment pattern (`infra/ec2-setup.md`), Alembic migration flow | Infrastructure is sound and already proven live on a real EC2 host |
| pytest patterns (flush+rollback fixtures, mocked Bedrock, real concurrent-session regression tests) | Keep this discipline for every new test in the rebuild |
| Design token *philosophy* (Manrope + IBM Plex Mono, deep emerald accent, light/dark CSS custom properties) | The palette and type pairing are deliberate and non-generic — expand the token set, don't replace the foundation |

## MODIFY — right idea, needs real change

| Item | Change needed |
|---|---|
| `Obligation` model | Gains an `Invoice` parent entity; becomes explicitly Receivable/Payable-typed with extraction metadata (invoice date, invoice ID, PO reference) |
| `ReliabilityScore` / `services/scoring.py` | Reweight from the current 0.7/0.3 (counterparty-level) and 0.5/0.2/0.15/0.15 (obligation-level) scheme to the spec's fixed 45/25/15/15 buckets; add `advance_pct` + `fee_pct` tier-pricing output (currently tier-only, no pricing) |
| `BankPacket` / `services/packet.py` | Keep the "risk packet" shape (gross obligations, matches, justification, flagged items) but stop treating it as a dead-end report — wire it into the new `FinancingOffer` → mock-lender flow |
| `AppShell.tsx` | Restructure navigation to the spec's §27 hierarchy: Overview, Cash & Forecast, Receivables, Counterparties, Liquidity, Netting, FX & Exposure, Compliance, Assistant, Activity |
| `Dashboard.tsx` | Rebuild to the 5-level hierarchy (current state → critical alert → recommended action → supporting evidence → detailed analytics) instead of a flat grid of stat tiles |
| `Receivables.tsx` | Add expected-payment-date (behavior-adjusted, not just contractual due date), eligibility, advance %, and potential-liquidity columns; row click routes to new Receivable Detail |

## REWRITE — same problem space, new implementation

| Item | Why a rewrite, not a patch |
|---|---|
| Frontend component primitives (`components/`) | Current set (`StatTile`, `Card`, `Pill`, `MatchCard`) is too thin for the required surface. Needs the full library from §33: `FinancialMetric`, `RiskBadge`, `MoneyValue`, `ForecastChart`, `FanChart`, `LiquidityOpportunity`, `CounterpartyCard`, `FinancingOfferCard`, `StatusTimeline`, `ComplianceItem`, `ScenarioSlider`, `InsightCard`, `ActivityRow` |
| `NettingRunDetail.tsx` / `PacketView.tsx` | Currently a flat matches list; needs to become the dramatic before/after gross→matched→residual transition the spec calls for (§13), legible in under 5 seconds |

## DELETE — nothing

No existing code is actively wrong or harmful. This is an expansion of a correct foundation, not a
correction of a broken one — every KEEP/MODIFY item above stays load-bearing in the rebuilt product.

## MISSING — net new (the bulk of the work)

**Data model:** `Invoice`, `UnderwritingDecision`, `FinancingOffer`, `FinancingAgreement`, `Settlement`,
`ComplianceRequirement`, `BankNBFCPartner`, `LiquidityEvent`, `CurrencyExposure`, `AuditEvent`

**Engines:** cash-runway/liquidity-gap projection (30/60/90-day), liquidity-unlock recommendation
algorithm (minimum receivable set to close a gap — not "finance everything"), Monte Carlo digital twin
with uncertainty bands, buyer-delay what-if recompute

**Services:** a **separate** mock NBFC service (own deployable, own decision logic, simulated latency —
not a function call inside the existing backend), settlement fast-forward simulation, entity resolution
(fuzzy buyer-name matching), document extraction, contextual AI Copilot, simple session auth

**Screens:** Login, Receivable Detail, Counterparty Profile, Liquidity Unlock, Financing Offer, Financing
Status, FX & Exposure, Compliance, AI Assistant, Audit Activity, WhatsApp simulation

---

## Sequencing (full detail in the approved plan, `docs/` will get a copy as work proceeds)

Phase 0 (this document) → Phase 1 (`DESIGN.md` + design system) → Phase 2 (data foundation + expanded
seed) → Phase 3 (financial engines) → Phase 4 (core SME experience, MUST WORK) → Phase 5 (financing
orchestration + mock lender, MUST WORK) → Phase 6 (netting UI, MUST WORK) → Phase 7 (digital twin, SHOULD
WORK) → Phase 8 (AI + compliance, SHOULD/NICE) → Phase 9 (polish + demo rehearsal).

Each phase gets a manual test checkpoint before the next one starts, matching the cadence of the original
8-phase build.
