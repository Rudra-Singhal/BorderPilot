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

## Frontend (Phase 7+)

```bash
cd frontend
npm install
npm run dev
```

Dashboard: http://localhost:5173 (expects the backend running at `http://localhost:8000` — see
`frontend/.env`). Requires the backend's CORS origins in `backend/app/main.py` to include the dev
server's origin (already configured for `localhost:5173`).
