# BorderPilot Demo Script

Fixed walkthrough: pooled SME data → netting run → AI-explained matches → bank packet. Rehearsed twice
against a clean reset (`python -m app.seed.reset`) with identical results both times — see numbers below.

**Reset before the demo starts** (locally or on EC2 — same command either way):

```bash
docker compose exec api python -m app.seed.reset
```

This wipes every table and reseeds from scratch, including the two "guaranteed" scenarios baked into
`app/seed/seed.py` specifically so a fresh reset always reproduces a rich result — not just the one thin
match the raw base data would otherwise produce.

## The walkthrough (~4 minutes)

**1. Dashboard** (`/`) — "Here's BorderPilot: six SMEs, twelve shared counterparties, pooled across all of
them." Point at the FX exposure breakdown — four currencies, real cross-border exposure, not a toy dataset.

**2. Receivables** (`/receivables`) — "Every obligation carries a reliability tier computed from that
counterparty's *pooled* payment history — not just this one SME's view of them." Point at Harbor Logistics:
tier B, because its behavior profile is built from real on-time payment history.

**3. Netting runs → Trigger netting run** — "Watch this happen live." The run groups obligations by
settlement window and pooled counterparty, then nets what it can. Expect ~4-6 seconds (live Bedrock calls
per match). Auto-navigates to the run detail page.

**4. Run detail — the two sections are the story:**
   - **Auto-eligible (1 match)**: Acme Textiles → Harbor Logistics → Pacific Foods, $2.00, **Tier B**. Small
     dollar amount, but the point is the *tier*, not the size — this is what "safe to automate" looks like.
   - **Needs review (3 matches)**: point at the **Kestrel Electronics → Northwind Traders** pair — one
     $1,000 GBP payable split across **two different SMEs'** receivables (Nordic Gears $762, Baltic Steel
     $508). *This is the actual pooled-netting result* — a single obligation resolved through the shared
     counterparty across two unrelated companies, which no single-SME view could ever produce.

**5. Bank packet** — "This is the artifact a bank would actually receive." Walk the four summary tiles:
   - Gross obligations **$174,426.23**
   - Total matched **$1,332.00**
   - Net settlement required **$171,762.23** (gross − 2×matched, since netting clears both legs)
   - Est. FX/friction saved **$6.66**

   Scroll to a justification and read one aloud — e.g. Northwind Traders': *"...tier D rating (46.19/100)
   and poor on-time payment record (16.7%) present elevated counterparty risk..."* — point out every number
   in that sentence is real, pulled from the actual pooled profile, not invented.

**6. Close on "Open print-ready view"** — the exact document, self-contained, that would go to a bank. No
live API needed to view it once opened.

## Expected numbers (from two independent rehearsals against a clean reset)

| Figure | Value |
|---|---|
| Obligations considered | 22 |
| Matches created | 4 |
| Auto-eligible | 1 |
| Needs review | 3 |
| Gross obligations | $174,426.23 |
| Total matched | $1,332.00 |
| Net settlement required | $171,762.23 |
| Est. FX/friction saved | $6.66 |

If live numbers differ from this table during a real run, the most likely cause is stale data from manual
testing — run the reset command above and re-trigger.

## If live systems fail mid-demo

- **Bedrock is down / no AWS connectivity**: the netting engine still works — matches still get created,
  just with a deterministic fallback justification instead of an AI-generated one (this is real
  degradation behavior, verified in Phase 5, not a demo trick — worth saying out loud if it happens).
- **EC2 / network is down**: fall back to `docs/demo/fallback-snapshot.html` — a static, self-contained
  copy of a real, verified run (the exact numbers above), viewable offline with zero backend dependency.
- **Local backend crashes**: `docker compose up -d` restarts it in seconds; Postgres data persists in the
  named volume unless `-v` was passed.
