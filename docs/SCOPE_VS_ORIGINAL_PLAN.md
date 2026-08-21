# BorderPilot — Scope vs. Original 8-Module Plan

The original hackathon strategy doc specified **8 modules** built around a lending/financing product
(SME uploads invoice → pooled reliability score → one-click cash advance → mock bank disburses →
netting reduces gross settlement on the side). Early in this build, you handed me a **"Refreshed
Implementation Plan"** that deliberately narrowed this to a 6-phase pipeline, reasoning: *"prove the
harder, more defensible part first — that pooled SME data can produce real, AI-explained net settlement
instructions a bank could act on"* — and explicitly deferred Compliance (M7) and Bank/NBFC Integration
(M8), with Module 6 **redefined** from "one-click liquidity unlock" into "bank-facing output packet."

That narrowing was intentional and you approved it. But it cut more than a glance at the phase list
shows — an entire product surface (lending, pricing, disbursement, cash-runway impact, compliance,
auth) doesn't exist at all. This document is the honest, complete accounting: what got built, what
diverged, and what's missing, module by module against the **original** plan.

**Legend:** ✅ built as specified · 🟡 built, but narrower/different than specified · ❌ not built at all

---

## Module 1 — SME Financial Command Center

**Original:** cash position, receivables, payables, upcoming obligations, FX exposure, liquidity gap,
financed-receivables outstanding, risk indicators, 30/60/90-day projected cash runway.

**Built (🟡):** `frontend/src/pages/Dashboard.tsx` — SME count, counterparty count, gross obligations
(USD-equivalent), open/netted obligation split, FX exposure by currency (bar breakdown).

**Missing:**
- ❌ Liquidity gap calculation
- ❌ Financed-receivables outstanding (moot — no financing exists, see M6)
- ❌ Risk indicators
- ❌ 30/60/90-day cash-runway projection — **this was the chart the entire demo script was built around**
  ("projected cash going negative in 12 days")

## Module 2 — Receivables Intelligence

**Original:** buyer, country, currency, amount, due date, buyer payment history, reliability score,
late-payment distribution, **expected** (behavior-adjusted) payment date, financing eligibility,
recommended advance %.

**Built (🟡):** `frontend/src/pages/Receivables.tsx` — buyer, country, currency, amount, due date,
reliability tier + score.

**Missing:**
- ❌ Late-payment distribution (on-time / moderately-late / significantly-late buckets)
- ❌ Expected payment date (only the contractual due date is shown, never adjusted by behavior)
- ❌ Financing eligibility flag
- ❌ Recommended advance % — doesn't exist because no financing/advance concept exists at all

## Module 3 — Pooled Counterparty Intelligence ("the moat, made visible")

**Original:** a dedicated **profile screen per buyer** — pool-wide transaction count, on-time/moderate/
significant delay buckets, median delay, corridor, currency, reliability score, trend (improving/
declining), "data contributed by N SMEs." Called out as *the single screen that should make a judge
say "oh, this is why one bank couldn't do this."*

**Built (🟡, backend only):** The underlying data is real and computed correctly —
`PaymentBehaviorProfile` (on-time ratio, median delay, delay variance, transaction count, recency) is
built pool-wide across every SME touching a counterparty, exactly per spec, and is exposed via
`GET /behavior-profiles/{counterparty_id}`.

**Missing:**
- ❌ **There is no Counterparty Profile page in the frontend at all.** The pooled data is real and
  tested, but nothing renders it as its own screen — it only surfaces indirectly as a tier pill in the
  Receivables table and inside AI match justifications. The specific "moat made visible" card the
  original plan calls its most important screen does not exist.
- ❌ Delay bucket breakdown (on-time/moderate/significant) as a display — the raw stats exist, the
  bucketed view doesn't
- ❌ Trend (improving/declining over time) — `ReliabilityScore` is versioned so the *data* to compute a
  trend exists, but nothing computes or displays one
- ❌ "Data contributed by N SMEs" framing

## Module 4 — Underwriting Engine

**Original:** 4-bucket weighted score — Counterparty 45%, Receivable Quality 25%, Corridor/Currency 15%,
SME Signal 15% — producing reliability score → tier → **advance % → price** (a full pricing table,
A through E, 90% advance at 1.5–2% down to "not eligible").

**Built (🟡, substantially different formula):** `app/services/scoring.py` — counterparty-level score =
0.7×behavior + 0.3×corridor; obligation-level = 0.5×behavior + 0.2×corridor + 0.15×obligation-size-signal
+ 0.15×SME-signal. Produces tier A–E only.

**Diverged / Missing:**
- 🟡 Completely different weight scheme — not 45/25/15/15, and "Receivable Quality" (documentation
  completeness, historical dispute rate, invoice-vs-average-size) collapsed into one much simpler
  "obligation size vs. counterparty's typical" signal
- ❌ No advance % output
- ❌ No price/fee output — the entire pricing table doesn't exist
- ❌ No approve/review/reject decision — tier is used only for `auto_eligible`/`needs_review` netting
  flags, never a lending decision
- ✅ The confidence-multiplier idea (thin data → score shrinks toward neutral) **is** implemented, just
  via score-shrinkage rather than a tier-cap rule — same spirit, different mechanism

## Module 5 — Netting / Offset Engine

**Original:** graph-based matching, currency normalization, settlement-date bucketing, greedy matching,
partial matching + residual, compliance gate, FX/friction savings estimate.

**Built (✅, the most faithful module):** All of the above is implemented essentially as specified —
graph grouped by `(settlement bucket, counterparty)`, static FX table, greedy largest-first matching,
partial/residual handling verified with real numbers, a compliance gate (simplified to `status == OPEN`,
exactly as the original plan allowed: *"the compliance eligibility rule... should be clearly mocked/
simplified"*), and an FX/friction savings estimate.

**Enhancement beyond spec:** the original asked for a static "one-line compliance justification." What's
built goes further — a live AI-generated (AWS Bedrock), fact-constrained justification per match, plus an
auto-eligible/needs-review flag driven by the tier. This is genuinely more than the original M5 asked for.

## Module 6 — Liquidity Unlock Engine → redefined to "Bank-Facing Output Packet"

**Original:** *the primary "WOW moment."* Detects a projected cash shortfall, ranks eligible receivables
by `(reliability × advance amount) / days-to-maturity`, surfaces a one-click **"Unlock ₹X today"** action,
calls a mock NBFC, and animates the cash-runway chart closing live in front of judges.

**Built:** ❌ **None of this exists.** The refreshed plan renamed "Module 6" to mean something else
entirely — a structured JSON/HTML report *for* a bank (`BankPacket`), not an SME-facing unlock action.
There is no shortfall detection, no ranking algorithm, no "Unlock" button anywhere in the UI, no cash
delta animation. This is the single largest gap against the original plan — the feature the entire
demo script and win condition were built around does not exist in this codebase.

## Module 7 — Compliance Intelligence

**Original:** real FEMA/RBI concept references (Form A2, netting-eligible categories, export realization
timelines), a dedicated Compliance screen, explicit "illustrative / demo-only, not verified" labeling
discipline in the UI itself.

**Built:** ❌ **Not built at all** — explicitly deferred from the start of this build pass. The only trace
is the static `status == OPEN` gate inside the netting engine, which has no FEMA/RBI framing, no UI
screen, and no illustrative/verified labeling anywhere.

## Module 8 — Bank/NBFC Integration Layer

**Original:** a **separate mock NBFC service** with its own simulated latency and decision logic —
BorderPilot sends a risk packet, the mock service "approves" and "disburses," architecturally proving the
separation of responsibilities.

**Built:** 🟡 partial, one-directional. The `BankPacket` *is* the risk packet the original plan describes
— gross obligations, matches with justification, net settlement, flagged items — genuinely well-built.
But ❌ there is no second service to send it to, no mock approval/disbursement call, no simulated latency
or decision variance. The packet is generated and stops there; nothing "receives" it.

---

## Cross-cutting things in the original plan that don't exist anywhere in this build

- ❌ **Document/invoice extraction** (Ollama-based) — no upload flow, no extraction, all data is seeded
- ❌ **Entity resolution / fuzzy-matching** buyer names across SMEs — seed data uses exact canonical
  names; the "Schmidt Industrial GmbH vs Schmidt Industrial Gmbh." vs Schmidt Ind." problem is never
  actually solved because it's never posed
- ❌ **Anomaly/fraud flagging**
- ❌ **What-if simulation** (buyer-delay slider, FX slider, etc.)
- ❌ **Financing status pipeline** screen (Requested → Under Review → Approved → Disbursed → Settled) —
  moot, no financing exists
- ❌ **Audit log viewer** — the underlying data trail exists (versioned `ReliabilityScore`, timestamped
  `NettingRun`/`OffsetMatch` rows), but there's no screen that presents it as an audit log
- ❌ **Auth / login screen** — the original plan explicitly said build one anyway "because judges expect
  it, even if simplified." This build has no auth layer at all — anyone with the URL has full access.
- ❌ **Business model plumbing** — no `FinancingOffer`, `FinancingAgreement`, `LiquidityEvent`,
  `BankNBFCPartner`, or `ComplianceRequirement` entities exist in the schema. The refreshed plan explicitly
  chose to leave these out "to keep the schema honest about current scope" rather than stub them — a
  reasonable call, but it means the entire monetization story (§22 of the original doc, the "we touch
  $243, not $45,000" line) has zero implementation to point to.
- 🟡 **Demo dataset scale** — original spec: 8 SMEs, 15 counterparties, ~120 transactions, 3 buyer
  archetypes (reliable/moderate/unreliable), 1–2 thin-data buyers. Built: 6 SMEs, 12 counterparties, 17
  obligations + ~60 payment events. Smaller across the board, though the "thin-data buyer" and "shared
  counterparty" ideas are both represented.
- 🟡 **Tech stack** — original specified Tailwind + Recharts for the frontend and Ollama for local/private
  AI extraction. Built: hand-rolled CSS modules (no Tailwind), hand-built SVG bars (no Recharts), and AWS
  Bedrock instead of Ollama for AI — a reasonable substitution for what got built (there's no document
  extraction to run locally), but it means the "local model, privacy-first" narrative from the original
  plan's AI section no longer has anything backing it, since the AI that *is* used runs in AWS, not locally.

---

## What this actually adds up to

**What's real and solid:** the two pieces of "real, working, explainable logic" the original plan's own
closing argument (§29) says are what separate this from every other AI-fintech-dashboard pitch —
the underwriting-adjacent scoring engine and the netting engine — are genuinely built, tested, and
verified against live data. M5 in particular matches the original spec closely and adds an AI layer
beyond what was asked.

**What's not real:** the actual *product* the original plan describes — an SME uploading an invoice,
seeing a cash gap, clicking one button, and receiving simulated money — does not exist. What's built
instead is the analytical/infrastructure half of that story (score buyers, net obligations, produce a
bank report) without the SME-facing financing half (M6 as originally conceived) or the bank-facing
confirmation half (M8's mock service). The Raj narrative (§4 of the original doc) cannot currently be
demoed end-to-end — there is no screen where a cash shortfall appears, no "Unlock" button, no
disbursement, no runway chart closing.

If the goal is the original hackathon pitch, the highest-leverage next work, in order, is:
1. **Counterparty Profile screen** (M3) — the data already exists, this is pure frontend work
2. **Cash-runway projection + Liquidity Unlock flow** (M1 + M6 original) — the actual missing "WOW moment"
3. **A mock NBFC service** (M8) — architecturally separate, even a stub, to close the loop the packet
   currently dead-ends into
4. **Compliance screen with illustrative/verified labeling** (M7) — lowest effort, high credibility payoff
