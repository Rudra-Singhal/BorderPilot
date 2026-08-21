# EC2 demo host

Single instance running the full backend stack (Postgres + FastAPI) via Docker Compose, provisioned
in Phase 6. Not behind a load balancer or auto-scaling — this is a demo/dev host, not production infra.

## Current instance

- **Instance ID:** `i-0623ae5fa8f423a39`
- **Type:** t3.small (2 GB RAM), 20 GB gp3 EBS
- **Region:** eu-north-1 (same region as Bedrock model access, avoids cross-region calls)
- **AMI:** Ubuntu 24.04 LTS (`ami-0cda11afd45b74b89` at provision time — Canonical owner `099720109477`)
- **Public IP:** `51.20.181.222` (will change if the instance is stopped/started; re-fetch via
  `describe_instances` if so — Elastic IP was not allocated to keep this reversible/cheap)
- **Security group:** `sg-04f0526b2fc3c9d6a` (`borderpilot-sg`) — **SSH (22) and API (8000) both open to
  `0.0.0.0/0`**, an explicit choice made during Phase 6 for ease of access while building. Tighten this
  (at minimum SSH to a specific IP) before this is anything more than a throwaway demo host.
- **SSH key:** `infra/borderpilot-key.pem` (gitignored, not committed — matches the `borderpilot-key` EC2
  key pair). `chmod 600` required before use.

## Redeploying after a local code change

```bash
rsync -avz -e "ssh -i infra/borderpilot-key.pem -o StrictHostKeyChecking=accept-new" \
  --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' \
  backend/ ubuntu@51.20.181.222:/home/ubuntu/backend/

ssh -i infra/borderpilot-key.pem ubuntu@51.20.181.222 \
  "cd backend && sudo docker compose up -d --build && sudo docker compose exec -T api alembic upgrade head"
```

Re-seed / re-run netting the same way as locally, just prefixed with `ssh ... "cd backend && sudo docker compose exec -T api ..."`.

## Notes

- Docker + the Compose plugin are installed via cloud-init on first boot (see the `UserData` script used
  at launch time) — `docker compose` (space, plugin form), not the standalone `docker-compose` binary.
- `backend/.env` (AWS credentials + Bedrock model ID) was copied to the instance via the same rsync —
  it's gitignored locally and was never committed; it only exists on this instance's disk and in your
  local `backend/.env`.
- Postgres data lives in a named Docker volume on the instance (`backend_borderpilot_pgdata`) — it does
  **not** survive `docker compose down -v` or instance termination.
- Estimated cost: t3.small in eu-north-1 is roughly $0.021/hr on-demand (~$15/mo if left running
  continuously) plus a few cents/month for the 20 GB gp3 volume. Stop (not just the containers, the
  instance itself) when not actively demoing to avoid idle spend.
