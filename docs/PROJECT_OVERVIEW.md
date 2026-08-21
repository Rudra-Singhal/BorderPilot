# BorderPilot — Project Overview

**One-sentence pitch:** prove that pooled SME transaction data can be turned into real, AI-explained net
settlement instructions a bank could act on — before building the SME-facing lending product.

This file is the single consolidated explanation of the whole system. Per-phase evidence (exact numbers,
hand-verified proof points) lives in [`manual-test-checklists/`](manual-test-checklists/); the presenter
script lives in [`demo/demo-script.md`](demo/demo-script.md).

---

## 1. The pipeline

```
SME / Counterparty / Obligation data (M1, M2)
        ↓
Pooled payment behavior per counterparty, across ALL SMEs that touch it (M3)
        ↓
Deterministic 0–100 reliability score → tier A–E (M4)
        ↓
Graph-based netting: group by settlement window + counterparty, net payables against receivables (M5)
        ↓
AI (Bedrock) writes a fact-only justification per match; tier decides auto-eligible vs needs-review (M5)
        ↓
Bank-facing packet: gross obligations, matches, net settlement required, flagged items (M6)
```

Every arrow above is a real, tested call — not a mock. M5 calls M3 and M4 live when it builds a match
(refreshing the counterparty's behavior profile and reliability score in the process); M6 calls M5's
output directly.

## 2. Data model

| Entity | Purpose |
|---|---|
| `SME` | One of six seeded companies (id, name, country, base currency) |
| `Counterparty` | A buyer/supplier shared across SMEs — the "pool" itself |
| `Obligation` | A receivable or payable between one SME and one counterparty |
| `PaymentEvent` | Historical settled payment, feeds the behavior profile |
| `PaymentBehaviorProfile` | Derived per-counterparty stats (on-time ratio, delay variance, etc.) |
| `ReliabilityScore` | Versioned (append-only) score + tier A–E, per counterparty or per obligation |
| `NettingRun` | One execution of the netting engine |
| `OffsetMatch` | One netted pair (a payable offset against a receivable), belongs to a run |
| `BankPacket` | The assembled deliverable for one run |

Seed data: 6 SMEs, 12 counterparties, deliberately overlapping — 4 counterparties are shared across 2–3
different SMEs, which is the entire premise the pooling story depends on.

## 3. How netting actually works (the centerpiece)

Every open obligation is grouped by **which counterparty it's with** and **which 14-day settlement
window** its due date falls into. Within each group, the engine greedily matches payables against
receivables — largest-remaining-first, currencies normalized through a static FX table. Nothing is
force-matched: obligations with no viable counterpart, or in the wrong window, are simply left alone.

The "pooled" payoff: because the *same counterparty* can appear on both sides via *different SMEs*, one
company's debt can settle against a completely unrelated company's credit, with the counterparty in the
middle. The seeded proof: Kestrel Electronics owes Northwind Traders £1,000; Northwind Traders separately
owes Nordic Gears £600 and Baltic Steel £400. The engine finds this and proposes **one payable split
across two different companies' receivables** — a result no single-SME view could ever produce.

A run never mutates `Obligation` rows — it's a repeatable proposal, not a settlement action.

## 4. The AI layer (AWS Bedrock)

For every match, Bedrock (`eu.anthropic.claude-haiku-4-5`, in `eu-north-1`) writes a 1–2 sentence
justification from a constrained prompt: it's handed the counterparty's real tier, score, on-time ratio,
and delay stats, and explicitly told not to invent anything beyond that. Hand-verified: a real
justification citing specific numbers matched the live database exactly, character for character.

The tier also drives `eligibility_flag`: tiers A/B → `auto_eligible`, C/D/E → `needs_review`.

If Bedrock is unreachable, a deterministic fallback template takes over instead of failing the run —
verified by deliberately breaking the model ID mid-run and confirming the run still completed.

## 5. The bank packet (M6)

The actual deliverable: gross obligations, every proposed match with its tier and justification, the
net cash that still needs to move (`gross − 2×matched`, since netting clears both legs of a match), an
estimated FX/friction savings (0.5% of matched value — explicitly a placeholder, not a real treasury cost
model), and everything flagged for manual review. Available as JSON (`GET /netting-runs/{id}/packet`) or
as a self-contained, print-ready HTML document (`GET /netting-runs/{id}/packet.html`).

## 6. Infrastructure

- **Local**: FastAPI + Postgres via Docker Compose (`backend/docker-compose.yml`)
- **Live demo host**: real EC2 instance (t3.small, Ubuntu 24.04, `eu-north-1`), provisioned via boto3,
  Docker installed by cloud-init. Full pipeline verified through its **public IP**, not just localhost.
  Details and redeploy steps in [`../infra/ec2-setup.md`](../infra/ec2-setup.md).
- **Cost**: effectively $0 against the $300 credit budget as of last check.

## 7. The dashboard

React + Vite + TypeScript, bespoke design system (Manrope + IBM Plex Mono, deep emerald accent, full
light/dark theming). Four pages: Dashboard (KPI tiles, FX exposure by currency), Receivables (every
obligation with a live reliability tier), Netting Runs (list + detail, auto-eligible vs needs-review
visually separated), Bank Packet (summary, matches, flagged residuals, JSON export + print-ready link).

## 8. Testing

- **33 automated tests** (pytest), all passing — service-level, deterministic, Bedrock mocked so the
  suite runs fast/free/offline. Covers scoring math, netting matching logic (bilateral, multilateral,
  partial residuals, bucket exclusion), packet arithmetic invariants, and the two race/type bugs below.
- **8 manual test checklists** (`manual-test-checklists/phase-1.md` through `phase-8.md`) — every
  headline number in this document was pulled from a real API call during the build, hand-verified against
  the underlying formula, not assumed.

## 9. Bugs found and fixed after Phase 8 (during your live testing)

Two real bugs surfaced once a human actually clicked through the running app instead of me driving it —
worth documenting since they were genuine defects, not edge cases I'd already covered:

1. **Race condition in packet generation.** `GET /netting-runs/{id}/packet` used a check-then-write
   pattern (SELECT for an existing packet, INSERT if none) that wasn't safe under concurrent requests —
   React's dev-mode double effect invocation fires the same request twice, and both could see "no packet
   yet" before either finished inserting, so the second hit a database uniqueness violation and returned a
   500. **Fixed** with an atomic `INSERT ... ON CONFLICT DO UPDATE` (database-level, no race window
   regardless of how many requests overlap). Added a regression test using two real concurrent DB sessions.

2. **Numeric columns returning `Decimal` instead of `float` on a fresh read.** Six monetary columns
   across the schema were annotated `Mapped[float]` but the underlying `Numeric(14,2)` type returns
   Python's `decimal.Decimal` on an actual database round-trip — this only stayed hidden because the
   objects were previously populated by direct in-memory assignment, never re-fetched. Fixing bug #1
   (which now does a real re-fetch) exposed it. **Fixed** by adding `asdecimal=False` to all six columns
   so runtime behavior matches the type annotation everywhere, not just the one spot that surfaced it.

3. **Not every counterparty had a reliability score on a fresh seed.** Only counterparties that happened
   to land inside a netting match ever got scored (scoring was only triggered from inside the netting
   service). Everyone else sat "not scored" until someone called the bulk recompute endpoint — which
   showed up as a wall of expected-but-noisy 404s in the browser console on the Receivables page after a
   reset. **Fixed** by having the seed script score every counterparty immediately after seeding, so a
   fresh reset always leaves all 12 counterparties scored from the start.

All three fixed, tested, and committed. Full suite: 33/33 passing.

## 10. Where things stand right now

- **All 8 phases of the build plan shipped and verified** — locally and on the live EC2 host
- **3 post-completion bugs found via real usage, fixed, tested, committed**
- **10 commits on `main`, not pushed to `origin`** (repo has a remote configured but nothing pushed yet —
  say the word if you want that pushed)
- Backend running locally on `localhost:8000`, frontend dev server on `localhost:5173`, data currently
  seeded and scored (reset anytime with `docker-compose exec api python -m app.seed.reset`)
- Live demo host reachable at the EC2 public IP in `infra/ec2-setup.md`

## 11. What's honestly simplified (by design, per the narrowed scope)

- FX rates are a static table, not a live feed
- No compliance engine — a placeholder gate (`status == OPEN`) stands in for real eligibility rules
- No real bank API integration — the packet is the interface contract for one, not a live connection
- No lending/financing logic anywhere — tiers exist purely to gate netting confidence, not to price a loan
- EC2 security group has SSH + API open to `0.0.0.0/0` by explicit choice during the build — tighten
  before this is anything more than a demo host
