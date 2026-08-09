# FitMentor AI — Deployment Guide

## 1. Prerequisites
- A server/VM with Docker + Docker Compose v2 (e.g. a $20/mo DigitalOcean droplet is enough to start)
- A domain name pointed at the server's IP (for HTTPS)
- API keys for at least one AI provider (OpenAI, Anthropic, or Gemini)
- (Optional) AWS S3 or Cloudinary credentials for progress photo uploads
- (Optional) Firebase project + service account JSON for push notifications

## 2. Environment setup
```bash
git clone <your-repo-url> fitmentor-ai
cd fitmentor-ai
cp .env.example .env
```
Edit `.env`:
- `SECRET_KEY`: generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- `DATABASE_URL` / credentials: leave as-is if using the bundled Postgres container,
  or point at a managed Postgres (RDS, Supabase, Neon, etc.)
- `DEFAULT_AI_PROVIDER` + matching API key
- `CORS_ORIGINS`: set to your real frontend domain(s), e.g. `["https://fitmentor.ai"]`
- `NEXT_PUBLIC_API_URL`: set to `https://fitmentor.ai/api/v1` (or your domain)

## 3. First boot
```bash
docker compose up --build -d
docker compose logs -f backend   # confirm "alembic upgrade head" succeeded, then uvicorn started
```
The backend container runs migrations automatically on startup (see the
`command:` in `docker-compose.yml`). To seed exercises + a default admin account:
```bash
docker compose exec backend python -m app.db.seed
```
**Immediately log in as `admin@fitmentor.ai` and change the seeded password.**

## 4. HTTPS
The bundled `nginx/nginx.conf` serves plain HTTP on port 80. For production,
put a TLS-terminating layer in front of it — the simplest options:
- **Caddy** as a drop-in replacement for the nginx container (automatic Let's Encrypt certs)
- **Certbot** + the existing nginx container (add a `certbot` service and a
  `443 ssl` server block)
- A managed load balancer (AWS ALB, DigitalOcean LB, Cloudflare) terminating
  TLS in front of port 80

## 5. Scaling notes
- **Backend**: stateless — scale horizontally by running multiple `backend`
  replicas behind nginx/a load balancer. Session state lives in JWTs, not
  server memory.
- **Celery worker**: scale replicas of `celery_worker` independently if
  notification volume grows; `celery_beat` must stay at exactly one replica
  (it's the scheduler, not a worker).
- **Database**: the schema is fully normalized with indexes on every
  `user_id` foreign key (see migration `0001_initial_schema.py`). For heavy
  read load on progress charts, consider a read replica.
- **AI calls**: `app/ai/provider.py` makes one outbound call per generation
  request with no built-in queueing — for high traffic, move workout/nutrition
  generation onto a Celery task with a "generating…" status the frontend polls,
  rather than holding the HTTP request open.

## 6. Monitoring
- `/api/health` is a liveness endpoint — point your load balancer's health
  check at it.
- Backend Dockerfile includes a `HEALTHCHECK` hitting the same endpoint.
- Structured logging: the app currently uses Python's stdlib `logging`
  (see `score_service.py`, `weekly_review_service.py` for examples of the
  pattern) — wire this to your log aggregator of choice (e.g. ship container
  stdout to Datadog/CloudWatch/Loki).

## 7. Backups
- Postgres: schedule `pg_dump` on a cron, or use your managed provider's
  automated backup feature if you're not using the bundled container.
- The `postgres_data` named volume in `docker-compose.yml` persists data
  across container restarts, but is **not** a backup — back it up separately.

## 8. Zero-downtime deploys
```bash
git pull
docker compose build backend frontend
docker compose up -d --no-deps backend frontend
```
Alembic migrations run automatically on backend container start; write
migrations to be backward-compatible with the previous release for true
zero-downtime rollout (add columns as nullable first, backfill, then tighten
constraints in a follow-up migration).
