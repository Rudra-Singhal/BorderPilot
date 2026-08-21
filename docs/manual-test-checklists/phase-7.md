# Phase 7 — Dashboard Polish (React frontend): Manual Test Checklist

React + Vite + TypeScript, no UI kit — a bespoke design system (`frontend/src/styles/tokens.css`)
extending the palette established in the Phase 5/6 progress-report artifact: Manrope for UI text,
IBM Plex Mono for figures/ids, a deep emerald accent, full light/dark theming via CSS custom properties
with a persisted toggle. Four pages: Dashboard, Receivables, Netting Runs (list + detail), Bank Packet.
CORS enabled on the backend (`backend/app/main.py`) for the dev server origin.

- [x] Dashboard loads and reflects current seeded data correctly against the live backend — verified via
      screenshot: SME/counterparty counts, gross obligations (USD-equivalent), open/netted split, and the
      FX-exposure-by-currency breakdown all matched the API responses at time of load.
- [x] Receivables table reliability tiers match what Phase 3's endpoint returns — cross-checked several
      rows against `GET /reliability-scores/counterparty/{id}` directly (e.g. Harbor Logistics showing
      "Tier B · 84" in the table, matching the live endpoint).
- [x] Netting run view correctly renders auto-eligible vs needs-review matches distinctly — confirmed via
      screenshot: two separate cards ("Auto-eligible matches" / "Needs review"), each match additionally
      carries a color-coded tier pill and an eligibility pill (green vs amber).
- [x] Bank packet view renders and export produces a usable file — summary tiles, full match list with
      justification text, and the flagged-residuals table all render correctly; "Download JSON" triggers a
      client-side blob download of the exact `BankPacketOut` payload; "Open print-ready view" opens the
      Phase 6 server-rendered `packet.html` in a new tab.
- [x] Full click-through: seed → trigger netting run → view matches → view packet, with no console errors
      — clicked "Trigger netting run" from the Netting Runs page, watched a fresh run (with newly-generated
      Bedrock justifications, confirmed different wording than the cached run) complete and auto-navigate to
      its detail page, then to its packet. Verified via network inspector that all API calls returned `200`;
      the only console errors present were stale CORS failures logged before the backend's CORS middleware
      was picked up on container restart (pre-existing dev-loop issue, not a frontend bug) — confirmed clean
      on a fresh reload afterward.

**Result:** PASS — Phase 7 complete. Proceed to Phase 8 (demo rehearsal).
