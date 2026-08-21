# BorderPilot

AI netting engine on pooled SME transaction data, producing a bank-facing output packet. See `docs/` for the phased build plan and manual test checklists.

## Backend (Phase 1+)

```bash
cd backend
docker-compose up -d --build
docker-compose exec api alembic upgrade head
docker-compose exec api python -m app.seed.seed
docker-compose exec api pytest -q
```

API: http://localhost:8000 (docs at `/docs`). Postgres is exposed on host port `5544` (`5432` and `5433` were already in use locally).
