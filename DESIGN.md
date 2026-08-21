# BorderPilot Design System

## 1. Product vision

BorderPilot is an intelligence, matching, and underwriting orchestration layer between cross-border SMEs
and the banks/NBFCs that hold capital. It turns trade data no single lender can see into an underwriting
signal that unlocks working capital, while reducing how much money needs to physically move to settle
those transactions. It never lends and never holds customer funds.

Every screen exists to serve one continuous system:

```
cash problem → receivable → pooled buyer intelligence → underwriting → liquidity unlock →
lender → disbursement → updated cash position → netting → settlement → new transaction data
```

If a feature doesn't help the SME unlock liquidity, help the lender underwrite more intelligently, reduce
the money that needs to move, or make the decision more trustworthy — it doesn't belong in the product.

## 2. Core user journeys

**Founder (economic buyer)** — opens the app worried about cash. Needs, in order: *am I safe? what's
wrong? what can I do about it?* Journey: Dashboard alert → Liquidity Unlock → one recommendation, not a
menu → click → done. Never wants to compare 15 receivables by hand.

**Finance Head / CFO (primary user)** — lives in the app daily. Needs receivables, payables, forecast,
buyer intelligence, financing pipeline, FX exposure, and an audit trail, in that rough order of frequency.
Journey: Receivables table → drill into a specific buyer's reliability → decide what to finance → track
the financing pipeline → periodically check Compliance and Activity for anything needing attention.

**Credit Analyst (lender-side operational user)** — receives a risk packet, needs to trust the number
fast. Journey: Financing Offer → underwriting explanation (why this tier, why this price) → approve/review
decision. Never wants a black box.

## 3. Information architecture

Top-level navigation (§27 of the product spec), 10 items:

```
Overview          → Executive Dashboard
Cash & Forecast   → Digital Twin (30/60/90 + Monte Carlo + buyer-delay slider)
Receivables       → Receivables table → Receivable Detail (drill-in)
Counterparties    → Counterparty list → Counterparty Profile (drill-in, the "moat screen")
Liquidity         → Liquidity Unlock → Financing Offer → Financing Status
Netting           → Netting Opportunities → Netting Match Detail (drill-in)
FX & Exposure     → currency/corridor exposure
Compliance        → verified vs. illustrative requirements per transaction
Assistant         → contextual AI Copilot
Activity          → Audit trail
```

`Login` sits outside the shell (pre-auth). `Financing Offer`, `Financing Status`, `Receivable Detail`,
`Counterparty Profile`, and `Netting Match Detail` are drill-in routes, not top-level nav items — this
keeps the sidebar at 10 items instead of 15+. WhatsApp simulation is reachable from Assistant as a channel
toggle, not a separate nav item.

## 4. Design language & brand direction

**Premium institutional fintech. Trusted, calm, analytical.** Not crypto (no neon, no gradients-for-their-
own-sake, no glow effects). Not gaming (no badges-as-decoration, no playful mascots). Not an AI gimmick
(no chat-bubble-first layouts, no sparkle icons, no "magic" language — the copy always says what the
system *computed*, never what it "thinks"). The visual model is closer to a modern trading terminal or an
underwriting workbench than a consumer app: dense where density carries information, spacious where a
number needs to land with weight, and always legible at a glance from across a room (this is a *demo*
product — numbers must read at judge-viewing distance).

Every screen has exactly one dominant question (§26), stated or clearly implied by its layout:

| Screen | Dominant question |
|---|---|
| Overview | Am I financially safe? |
| Receivables | Where is my money stuck? |
| Counterparty Profile | Can I trust this buyer? |
| Liquidity Unlock | How much money can I unlock today? |
| Netting | How much money actually needs to move? |
| Cash & Forecast | What happens to my cash next? |
| Compliance | What do I need to complete this transaction? |
| Financing Status | Where is my funding request right now? |

## 5. Color tokens

Extends the existing palette (kept from v1 — deliberate, non-generic: deep emerald, not the AI-cliché
purple gradient or terracotta). New tokens add a fourth semantic state (`alert`, distinct from `critical`)
for time-sensitive-but-not-yet-dangerous situations (a liquidity gap 30 days out, not a failed payment),
and a dedicated chart palette kept separate from semantic risk color so a forecast band is never confused
with a risk tier.

```css
/* existing, unchanged */
--bg, --surface, --surface-sunken, --border, --border-strong
--text, --text-muted, --text-faint
--accent, --accent-hover, --accent-soft, --accent-text
--good, --good-soft, --good-text        /* tier A/B, on-time, approved, settled */
--warning, --warning-soft, --warning-text /* tier C, needs-review, pending */
--critical, --critical-soft, --critical-text /* tier D/E, rejected, significantly late */

/* new for v2 */
--alert, --alert-soft, --alert-text      /* time-sensitive: liquidity gap approaching, offer expiring */
--info, --info-soft, --info-text         /* neutral system information, AI-sourced content marker */

/* chart palette — sequential, single-hue-family, never doubles as a semantic risk color */
--chart-line       /* the actual/base-case line */
--chart-band-80     /* 80% confidence band fill */
--chart-band-95     /* 95% confidence band fill (lighter) */
--chart-grid        /* gridlines */
--chart-axis         /* axis labels */
```

Dark-mode values follow the same derivation rule as the existing tokens (brightened, desaturated slightly,
paired soft/text variants). `--alert` sits between `--warning` (amber) and `--critical` (red) on the hue
wheel but is visually distinct at a glance — a warm gold rather than amber-brown, so a liquidity-gap
countdown never gets mistaken for a rejected financing decision.

## 6. Typography

Unchanged type pairing, formalized into a scale:

| Role | Face | Weight | Size (desktop) | Use |
|---|---|---|---|---|
| Display | Manrope | 800 | 32–40px | The one number a screen leads with (e.g. "₹62.4L Available Cash") |
| H1 | Manrope | 700 | 22px | Page title |
| H2 | Manrope | 700 | 16px | Section/card title |
| Label | Manrope | 700, uppercase, +0.05em tracking | 11–12px | Metric labels, table headers |
| Body | Manrope | 500–600 | 13–14px | Running UI text |
| Financial figure | IBM Plex Mono | 500 | matches context | Every money/percentage/count value, `font-variant-numeric: tabular-nums` always |
| Mono label | IBM Plex Mono | 400 | 11–12px | IDs, timestamps, currency codes |

Rule: **any number a user might compare against another number in the same view uses the mono face with
tabular numerals** — this is non-negotiable for tables and stat rows, it's what makes a column of amounts
scannable instead of jagged.

## 7. Spacing, radius, shadow

```css
--space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
--space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px; --space-12: 48px;

--radius-sm: 6px;   /* pills, small chips */
--radius-md: 10px;  /* cards, inputs */
--radius-lg: 14px;  /* modals, drawers */

--shadow-sm  /* existing: resting card */
--shadow-md  /* existing: raised card, dropdown */
--shadow-lg  /* new: modal, drawer over content */
```

Layout spacing always comes from flex/grid `gap`, never stacked margins — carried over from v1, keep it.

## 8. Component rules

Full primitive library (built in this phase, populated with real data from Phase 2 onward):

- **`FinancialMetric`** — the generalized stat tile: value (mono, tabular), label, optional trend
  indicator (▲/▼ + delta), optional hint line, optional size variant (`display` for the one hero number
  per screen, `default` for supporting metrics).
- **`RiskBadge`** — tier A–E as a colored badge with the numeric score alongside (`Tier B · 84`), color
  from the good/warning/critical semantic tokens via the existing tier-bucket mapping.
- **`MoneyValue`** — consistent currency formatting (symbol, thousands separator, decimals), always mono/
  tabular, accepts a `currency` prop so INR/EUR/USD/GBP all render correctly (not just USD as in v1).
- **`ForecastChart`** — Recharts line chart, actual + base-case projection, styled with the chart token set.
- **`FanChart`** — Recharts area chart layering 95%/80% confidence bands under the base-case line —
  the uncertainty-visualization primitive for the Digital Twin.
- **`LiquidityOpportunityCard`** — one recommended receivable-to-finance: amount, reliability, advance %,
  fee, net proceeds, one clear action button. Never a bare table row — this decision deserves a card.
- **`CounterpartyCard`** — the "moat" profile: transaction count, on-time/moderate/significant delay
  buckets (as a small stacked bar, not just numbers), median delay, trend, reliability score/tier, "data
  contributed by N SMEs" line.
- **`FinancingOfferCard`** — offer terms (advance %, fee, net proceeds, maturity) with an explicit "why
  this rate" expandable section showing the four scoring buckets.
- **`StatusTimeline`** — horizontal stepper for the financing pipeline (Opportunity → Offer → Submitted →
  Under Review → Approved → Disbursed → Settled), current step emphasized, past steps checked.
- **`ComplianceItem`** — a single requirement row: label, status (verified/pending/illustrative), and when
  illustrative, the mandatory caveat text inline, never hidden in a tooltip.
- **`ScenarioSlider`** — a labeled range input with a live-updating value readout, used for the buyer-delay
  what-if.
- **`InsightCard`** — AI-generated explanation text, always visually marked as AI-sourced (a small `--info`
  colored label, never disguised as a deterministic system output) with a link back to the source screen.
- **`ActivityRow`** — one audit log entry: timestamp (mono), actor (system/user), event type, one-line
  description, link to the relevant record.

Tables, cards, pills, buttons, and async states carry over from v1 largely unchanged in mechanics —
`Table.module.css`, `Card`, `Pill`, `Button`, `AsyncState` stay, extended only where a new screen needs a
variant they don't yet support.

## 9. Data visualization rules

- **Cash/forecast**: line + band chart (`ForecastChart`/`FanChart`), base case always solid, uncertainty
  always a fill, never a second solid line (a second line reads as "another actual value," not "a range").
- **Risk/reliability**: tier color (good/warning/critical) is the *only* color that carries risk meaning
  anywhere in the product — never repurpose it for anything else (e.g. never use "red" for a UI error
  unless it's also a risk signal).
- **FX/exposure**: single-hue accent bars (as in v1's `ExposureBar`) — categories differentiated by label,
  not by a rainbow of currency colors, since color-by-currency would compete with color-by-risk-tier for
  the same visual channel.
- **Netting (gross → net)**: one large number transitioning to a smaller large number, side by side or
  stacked with a clear arrow — never a chart for this, it's a single dramatic fact, charts would dilute it.
- **Network relationships** (optional network overview screen): node-edge diagram, SME and Counterparty
  nodes visually distinct (shape or fill, not color alone), edges weighted by transaction count.
- Every chart gets a faint grid (`--chart-grid`), an emphasized current/latest point, and axis labels in
  `--chart-axis` — never unlabeled axes, this is a finance product, not an art piece.

## 10. Interaction design

- **Hover**: `surface-sunken` background shift on rows/nav items, no shadow-pop (shadow-pop reads as
  "clickable card game," not "financial table").
- **Focus**: existing `outline: 2px solid var(--accent)` visible focus ring, unchanged — required for a
  product a Credit Analyst persona would actually use with a keyboard.
- **Loading**: skeleton blocks matching the shape of the content that will appear (not a spinner for
  anything that takes longer than ~300ms) — carried forward and extended from v1's `LoadingState`.
- **Empty**: every list/table gets an explicit empty state with a one-line explanation and, where relevant,
  the action that would populate it (e.g. Receivables empty → "No open obligations — trigger a seed reset.").
- **Error**: existing red-toned `ErrorState`, extended to always name what failed to load, never a bare
  "Something went wrong."
- **Success**: a transient `--good`-toned confirmation on completed actions (offer accepted, netting run
  triggered) — never a modal for something that isn't destructive.
- **Transition**: state changes that matter to the demo narrative (cash chart closing a gap, gross→net
  netting number) animate over ~400–600ms; everything else (nav, tab switches) is instant, no animation
  for its own sake. Respect `prefers-reduced-motion` throughout.

## 11. Responsive behavior

Primary target is desktop (1280px+, this is a demo on a projector/laptop, not a phone-first product).
Sidebar collapses below 860px (existing v1 behavior, kept). Tables get horizontal scroll containers below
their natural width rather than reflowing into cards — a Finance Head persona expects a real table.

## 12. Accessibility

Visible focus states everywhere (already the case), semantic HTML for tables/buttons/nav (already the
case), color never the *only* signal (tier badges always carry the letter + score, not just a color chip;
status always carries text, not just an icon), `prefers-reduced-motion` respected.

## 13. Content & tone

Plain, specific, non-promotional. "Recommended: finance 2 receivables to unlock ₹25.4L" not "Unlock your
potential today!" Never claim things the system doesn't do (§40 of the product spec — BorderPilot never
says it lends, never says AI approves financing, never says it executes netting; always "recommends,"
"identifies," "generates a recommendation subject to lender approval"). AI-sourced text is always labeled
as such and never presented as if it were the deterministic financial calculation itself.

## 14. Screen-by-screen specification

For each of the 15 required screens: objective, dominant question, layout hierarchy, key components, and
demo behavior. (Detailed data/interaction/state specs are finalized screen-by-screen as each is actually
built, in the phase that builds it — this section fixes the *shape* now so Phase 4+ has no ambiguity about
what belongs on each screen.)

1. **Login** — objective: gate the app behind a lightweight session. Single centered card, email + password
   (fixed demo credentials), no forgot-password/signup flow. Not a design centerpiece.
2. **Executive Dashboard (Overview)** — objective: "am I safe." 5-level hierarchy (§28): hero cash number →
   liquidity gap alert (if any) → one recommended action card → supporting evidence (forecast sparkline +
   why) → secondary metrics row (receivables/payables/FX/netting summary, smaller, below the fold).
3. **Cash & Forecast** — objective: "what happens next." `FanChart` centerpiece (30/60/90, confidence
   bands), the buyer-delay `ScenarioSlider` directly beneath it, liquidity-gap readout updates live as the
   slider moves.
4. **Receivables** — objective: "where is my money stuck." Table, one row per obligation, tier badge +
   advance % + potential liquidity columns, row click → Receivable Detail.
5. **Receivable Detail** — objective: full financing decision context for one receivable. Invoice facts,
   linked counterparty summary (mini `CounterpartyCard`), the four-bucket score breakdown, offer terms if
   eligible, one action button.
6. **Counterparty Profile** — objective: "can I trust this buyer." Full `CounterpartyCard` at page scale:
   transaction count, delay-bucket stacked bar, trend, reliability, "data contributed by N SMEs" —
   deliberately the single most information-dense, most "look how much we can see" screen in the product.
7. **Liquidity Unlock** — objective: "how much can I unlock today." Detected gap at top, then the *minimum*
   recommended set of `LiquidityOpportunityCard`s (never every eligible receivable), accept → Financing
   Offer.
8. **Financing Offer** — objective: review and confirm one offer. `FinancingOfferCard` with the expandable
   "why this rate" breakdown, submit → begins the pipeline.
9. **Financing Status** — objective: "where is my request." `StatusTimeline` per active/past agreement.
10. **Netting Opportunities** — objective: "how much needs to move." Big gross number → big net number,
    side-by-side, matched pairs listed beneath, illustrative-eligibility caveat always visible.
11. **Netting Match Detail** — objective: understand one specific match. The two obligations, the shared
    counterparty, the AI justification, the compliance gate result.
12. **FX & Exposure** — objective: currency/corridor risk at a glance. Exposure bars per currency (existing
    v1 component, promoted to its own screen), corridor risk table.
13. **Compliance** — objective: "what do I need." Per-transaction `ComplianceItem` list, verified items
    first, illustrative items clearly separated with the caveat text inline.
14. **AI Assistant** — objective: contextual Q&A grounded in real app state. Chat-style but every answer
    renders as result + key numbers + reasoning + link back to source screen, never prose-only.
15. **Audit Activity** — objective: trust via transparency. Reverse-chronological `ActivityRow` list,
    filterable by event type.

Optional: **WhatsApp simulation** (a phone-frame chat mock, reachable from Assistant), **Network overview**
(node-edge diagram of the SME↔Counterparty pool).
