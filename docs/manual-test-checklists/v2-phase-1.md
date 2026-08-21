# v2 Phase 1 — Product + Design Foundation: Manual Test Checklist

Deliverables: `DESIGN.md` (full spec — vision, journeys, IA, design language, tokens, typography, 15
screen specs), expanded `tokens.css` (semantic `--alert`/`--info` states + dedicated chart palette,
spacing/radius/shadow scale), 13 new component primitives (`FinancialMetric`, `RiskBadge`, `MoneyValue`,
`ForecastChart`, `FanChart`, `LiquidityOpportunityCard`, `CounterpartyCard`, `FinancingOfferCard`,
`StatusTimeline`, `ComplianceItem`, `ScenarioSlider`, `InsightCard`, `ActivityRow`), Recharts dependency,
new 10-item nav (`Overview, Cash & Forecast, Receivables, Counterparties, Liquidity, Netting, FX &
Exposure, Compliance, Assistant, Activity`), a lightweight demo session auth + `Login` screen, and 7
"design preview" pages showing each primitive with realistic mock data ahead of real data wiring in later
phases.

- [x] Nav is fully navigable — all 10 items route to a real page, no dead ends, no 404s
- [x] Login gates the app: unauthenticated visit to any route redirects to `/login`; correct demo
      credentials sign in and redirect to Overview; incorrect credentials show an inline error; "Sign out"
      returns to the login screen
- [x] All 3 pre-existing live-data pages (Dashboard/Overview, Receivables, Netting) still render real
      backend data correctly after the shell rebuild — confirmed via screenshot and network log (`200 OK`
      on every request), no regression from the nav/routing changes
- [x] All 7 new design-preview pages render their intended primitive(s) with mock data, each clearly
      labeled with a `PhaseNotice` banner stating which later phase wires it to live data — confirmed via
      screenshot: Cash & Forecast (`FanChart` + live-recomputing `ScenarioSlider`), Counterparties
      (`CounterpartyCard` incl. thin-data flag), Liquidity (`LiquidityOpportunityCard` ×2), FX & Exposure
      (`ExposureBar` reused + `RiskBadge` corridor table), Compliance (`ComplianceItem` verified/pending/
      illustrative), Assistant (`InsightCard` example Q&A), Activity (`ActivityRow` audit feed)
- [x] `ScenarioSlider` on Cash & Forecast actually recomputes the chart and the 60-day confidence range
      live when dragged (verified: 15d → 30d moved the range from ₹34.3L–₹39.0L to ₹33.8L–₹38.5L) — not a
      static mock, a real (if illustrative-data) recompute, matching the discipline required before Phase 7
      builds the real Monte Carlo version on top of this same component
- [x] Both themes (light/dark) checked on multiple new screens (Counterparties, Cash & Forecast) —
      contrast and hierarchy hold in both, no token defined only in one theme
- [x] `npx tsc -b` — zero type errors; `npm run build` — succeeds; `npm run lint` (oxlint) — zero warnings
- [x] Backend untouched by this phase — full pytest suite (33/33) still passing, confirming Phase 1 was a
      frontend-only phase as scoped

**Result:** PASS — Phase 1 complete. Proceed to Phase 2 (Data Foundation).
