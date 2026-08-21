# Phase 1 — Pooled Data Foundation: Manual Test Checklist

Run from `backend/`: `docker-compose up -d`, then `docker-compose exec api alembic upgrade head && docker-compose exec api python -m app.seed.seed`.

- [x] `docker-compose up` brings up DB + API cleanly
- [x] Seed script runs idempotently (re-running doesn't duplicate/crash) — verified: row counts identical after 2nd run (6 SMEs, 12 counterparties, 17 obligations, 51 payment events)
- [x] Query counterparties table, confirm ≥3 counterparties have Obligations from ≥2 distinct SMEs — verified via `GET /counterparties/pooled-overlap`: 4 counterparties overlap (3 with 2 SMEs, 1 with 3 SMEs — Global Retail Corp)
- [x] Spot-check obligation amounts/currencies/dates look realistic (no negative amounts, sane date ranges) — verified via `GET /obligations` and pytest `test_no_negative_or_zero_obligation_amounts`
- [x] API endpoints return the seeded data correctly via curl/Postman — verified `/health`, `/smes`, `/counterparties/pooled-overlap`, `/counterparties/{id}/obligations`

**Result:** PASS — Phase 1 complete, proceed to Phase 2.
