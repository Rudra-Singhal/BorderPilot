# Phase 8 — Demo Rehearsal: Manual Test Checklist

Built `app/seed/reset.py` (wipes all 9 tables in FK-safe order, then reseeds) and enriched
`app/seed/seed.py` with two "guaranteed demo scenarios" baked directly into the base dataset — the
multilateral split (Kestrel Electronics payable → Northwind Traders → Nordic Gears + Baltic Steel
receivables) and a naturally tier-B counterparty (Harbor Logistics, via 10 on-time payments) producing an
auto-eligible match. Without this, a fresh reset only ever reproduced the one thin cross-currency match —
not a fair showcase of what the netting engine actually does on pooled data. Presenter script and a static
offline fallback in `docs/demo/`.

- [x] Run the full demo script end-to-end at least twice without intervention — reset → seed → trigger
      netting run → generate packet, run twice independently. **Identical results both times**:
      22 obligations considered, 4 matches, 1 auto-eligible / 3 needs-review, gross $174,426.23, matched
      $1,332.00, net settlement $171,762.23, FX/friction saved $6.66. Full test suite (32/32) also passing
      after the seed change.
- [x] Confirm fallback recording covers the same flow if live infra fails — built
      `docs/demo/fallback-snapshot.html`: a static, self-contained copy of the Phase 6 print-ready packet
      view captured from a real verified rehearsal run, confirmed to render correctly fully offline
      (`file://`, zero network calls) at desktop width. Note: this is a static data snapshot, not a video
      recording — no tooling available in this session to produce a screen-capture video, and a static
      snapshot of real, verified numbers was judged the more honest and directly useful fallback artifact.
      `docs/demo/demo-script.md` also documents the exact narration and expected numbers so a presenter can
      talk through the flow from the script alone if nothing is viewable at all.
- [x] Confirm EC2 instance is in the expected state right before the demo (not mid-crash, data not
      stale/corrupted) — synced the updated backend (including the new reset/seed scripts) to EC2, rebuilt,
      ran the same reset there, and verified via the **public IP** that triggering a run reproduces the
      identical numbers above. `describe_instance_status` confirms both instance and system status checks
      are `ok`. Left EC2 in a clean **pre-run** state (seeded, zero netting runs) so the live trigger during
      the actual demo isn't replaying a stale cached run.
- [x] Final AWS spend check — Cost Explorer grouped by service shows effectively $0.00 month-to-date
      (EC2 usage doesn't appear yet due to the usual ~24h billing lag, consistent with the Phase 6 reading).
      Trivial against the $300 credit budget either way.

**Result:** PASS — Phase 8 complete. All 8 phases of the narrowed build plan are now shipped and
hand-verified end-to-end, locally and on the deployed EC2 host.
