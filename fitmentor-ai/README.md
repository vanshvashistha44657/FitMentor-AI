# FitMentor AI

**Your Personal AI Trainer. Nutritionist. Coach.**

An AI-powered fitness platform that generates fully personalized workout plans,
nutrition plans, and live coaching — driven by a real user profile, not a
template. Built with Next.js/FastAPI/PostgreSQL, deployable via Docker Compose.

---

## Architecture

```
fitmentor-ai/
├── backend/            FastAPI (Python 3.12), clean architecture
│   ├── app/
│   │   ├── api/v1/endpoints/   HTTP layer — thin, delegates to services
│   │   ├── ai/                 Prompt engineering + provider abstraction + scoring math
│   │   ├── services/           Business logic orchestration
│   │   ├── repositories/       All DB queries — the only layer that touches the ORM
│   │   ├── models/              SQLAlchemy ORM models (12 tables)
│   │   ├── schemas/            Pydantic request/response contracts
│   │   ├── core/                Config, security (JWT/bcrypt), dependency injection
│   │   └── db/                  Session factory, seed script
│   ├── migrations/              Alembic (async)
│   └── tests/                   pytest — unit (scoring) + integration (auth, SQLite)
├── frontend/            Next.js 14 (App Router), TypeScript, Tailwind
│   └── src/
│       ├── app/                 Routes: landing, auth, onboarding, dashboard/*, admin
│       ├── hooks/                React Query hooks — one per backend feature area
│       ├── store/                Zustand auth store (persisted, token-refresh aware)
│       └── lib/                  Axios client with auto-refresh interceptor
├── nginx/                Reverse proxy config (routes /api → backend, / → frontend)
└── docker-compose.yml    Postgres, Redis, backend, Celery worker+beat, frontend, nginx
```

## Why it's built this way

- **Deterministic scores, AI explanations.** The five onboarding scores (Fitness,
  Health, Muscle Balance, Lifestyle, Recovery) are computed with plain Python math
  in `app/ai/scoring.py` — not the LLM — so they're reproducible and auditable.
  The LLM's job is only to *explain* the numbers in plain language, with a
  template fallback if the AI call fails, so onboarding never blocks on an AI outage.
- **One AI provider abstraction, three backends.** `app/ai/provider.py` exposes a
  single `generate()`/`generate_json()` interface; OpenAI, Anthropic, and Gemini
  are interchangeable via `DEFAULT_AI_PROVIDER` in `.env` — no business logic
  changes needed to switch.
- **Every AI generation is schema-validated.** Workout and nutrition plans are
  parsed into Pydantic models (`WorkoutPlanAIResponse`, `NutritionPlanAIResponse`)
  before being persisted — a malformed LLM response fails loudly with a clear
  502, never silently ships a broken plan.
- **Repository pattern throughout.** Services never touch SQLAlchemy directly;
  every query lives in a `*Repository` class, which is what makes the in-memory
  SQLite test suite possible without touching Postgres.

## Local development

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # fill in SECRET_KEY, DATABASE_URL, at least one AI key
alembic upgrade head
python -m app.db.seed     # optional: seed exercises + admin@fitmentor.ai
uvicorn app.main:app --reload
```
API docs: `http://localhost:8000/api/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App: `http://localhost:3000`

### Tests
```bash
cd backend
pytest tests/ -v
```
15 tests: 9 unit tests on the scoring engine (no DB/network), 6 integration
tests against an in-memory SQLite database covering register/login/duplicate-email/auth-guard flows.

## Full stack via Docker

```bash
cp .env.example .env   # fill in real values
docker compose up --build
```
This starts Postgres, Redis, the FastAPI backend (auto-runs migrations on boot),
a Celery worker + beat scheduler for notifications, the Next.js frontend, and
an Nginx reverse proxy on port 80 (`/api/*` → backend, everything else → frontend).

## Environment variables

See `.env.example` for the full list. At minimum you need:
- `SECRET_KEY` — long random string for JWT signing
- `DATABASE_URL` — Postgres connection string
- One of `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY`, matching `DEFAULT_AI_PROVIDER`

Without an AI key configured, onboarding/scoring still completes (using fallback
explanation text), but workout generation, nutrition generation, and chat coach
will return a 503 until a provider key is set.

## API surface (34 endpoints)

| Area | Endpoints |
|---|---|
| Auth | register, login, Google login, refresh, me |
| Onboarding | complete questionnaire, get profile, get latest AI scores |
| Workouts | generate plan, get active/history, log session, get sessions |
| Nutrition | generate plan, get active/history |
| AI Chat Coach | send message (with persisted memory), get history |
| Daily check-in | submit today, get history |
| Progress | log entry, get entries, weekly review (adherence/strength/recovery + AI suggestions) |
| Gamification | get XP/level/streak/badges |
| Notifications | list, mark read |
| Admin | list/deactivate/reactivate users, analytics summary, exercise DB CRUD |

## What's deliberately out of scope for this build

- Image upload (progress photos, measurements photos) — the `photo_urls` JSON
  field exists on `ProgressEntry`, but the S3/Cloudinary upload flow itself
  isn't wired up.
- Push notification device-token registration — `send_push()` and the Celery
  beat schedule are implemented, but there's no `UserDevice` table yet to
  store FCM tokens per device.
- Payment/subscription billing — `subscription_tier` exists on `User` but
  there's no Stripe/payment integration.
