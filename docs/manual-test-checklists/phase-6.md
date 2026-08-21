# Phase 6 — Bank-Facing Output Packet (M6) + EC2 Stand-up: Manual Test Checklist

`BankPacket` model (one row per NettingRun, upserted on regenerate) + `services/packet.py` assembling
gross obligations in, matches with tier/justification, net settlement required, an FX/friction savings
estimate (0.5% of matched USD — a placeholder, not a real treasury cost model), and flagged items
(needs-review matches + any obligation with a positive residual). Endpoints:
`GET /netting-runs/{id}/packet` (JSON) and `GET /netting-runs/{id}/packet.html` (self-contained,
print-styled document — the "PDF-style view" called for in place of a real bank API integration).
See `infra/ec2-setup.md` for the deployed instance's details.

- [x] Locally: generate a packet for a completed netting run, confirm all fields populate correctly and
      match the underlying `OffsetMatch` data — verified the full arithmetic chain by hand:
      `net_settlement_usd (171,762.23) = gross_obligations_usd (174,426.23) − 2 × total_matched_usd (1,332.00)`
      (netting removes the matched amount from both legs), and
      `fx_friction_savings_usd (6.66) = total_matched_usd × 0.5%`. Every match in the packet body traced
      back to a real `OffsetMatch` row with matching tier/justification/amount.
- [x] Confirm flagged (needs-review) items are visibly separated from auto-eligible ones in the packet —
      JSON has a dedicated `flagged_for_review` section (needs-review matches + positive-residual
      obligations, kept disjoint from auto-eligible matches — unit-tested); the HTML render puts them in a
      visually distinct "Flagged for manual review" panel with amber pills vs. green "Auto-eligible" pills,
      confirmed via a live screenshot.
- [x] On EC2: `docker-compose up` (`docker compose`, plugin form) brings up the full stack identically to
      local — provisioned a fresh t3.small Ubuntu 24.04 instance in `eu-north-1`, cloud-init installed
      Docker, `rsync`'d the backend, `docker compose up -d --build` succeeded, all 6 Alembic migrations
      applied cleanly in the same order as local.
- [x] Re-seed and re-run netting on EC2, confirm a packet generates correctly there too — seeded fresh (6
      SMEs / 12 counterparties / 17 obligations), triggered a netting run via the **public IP**
      (`http://51.20.181.222:8000`), found the same Global Retail Corp cross-currency match as the original
      local run, generated a packet with correct summary figures, and confirmed `packet.html` returns
      `200`.
- [x] Confirmed Bedrock also works live from EC2 (not just locally) — the match's `justification_text` came
      back with `ai_generated: true` and cited real, current profile numbers (11.1% on-time, tier E
      35.32/100) — not a fallback template.
- [x] Confirm EC2 security group is not open to `0.0.0.0/0` unless intentionally required for the demo —
      it **is** open on both 22 and 8000 to `0.0.0.0/0`, but this was an explicit, informed choice made
      with the user during this phase (favoring not getting locked out while building over locking down
      early) — documented in `infra/ec2-setup.md` as something to tighten before this is more than a
      throwaway demo host.
- [x] Note current AWS spend against the $300 credit budget — Cost Explorer shows **$0.000028** spent
      month-to-date as of provisioning (billing data lags real-time by ~24h, so today's EC2 hours aren't
      reflected yet). t3.small in `eu-north-1` is ~$0.021/hr (~$15/mo if left running continuously) —
      trivial against the budget, but the instance should be stopped between demo sessions rather than
      left running idle.
- [x] Automated coverage: `tests/test_packet.py` — 4 tests covering unknown-run error handling, the
      summary arithmetic invariants, the flagged-section disjointness property, and upsert-not-duplicate
      on regenerate. Full suite: **32/32 passing**, confirmed both locally and on the EC2 instance itself.

**Result:** PASS — Phase 6 complete (the second phase the plan says must not slip). Proceed to Phase 7.
