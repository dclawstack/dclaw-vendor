# Quickstart

DClaw Vendor is an AI-native vendor & purchase-order management app: a FastAPI
backend (`:8146`), a Next.js frontend (`:3060`), Postgres, and an LLM-powered
Vendor Copilot.

## Option A — one command (bundled Postgres)

```bash
docker compose -f docker-compose.standalone.yml up --build
```

- Frontend: <http://localhost:3060>
- Backend API: <http://localhost:8146> (interactive docs at `/docs`)

Postgres runs inside the stack (not published), so it never collides with a host
Postgres. The backend creates its schema on first boot.

## Option B — native (for development)

```bash
# Backend
cd backend
python -m venv .venv && ./.venv/bin/pip install -r requirements.txt
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_vendor \
  ./.venv/bin/alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_vendor \
  ./.venv/bin/uvicorn app.api.main:app --port 8146

# Frontend (separate shell)
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:8146 npm run dev   # http://localhost:3060
```

## The AI Copilot

The Copilot and every AI feature (vendor evaluation, classification, enrichment,
performance / ESG / risk scoring, contract extraction, spend insights, survey
sentiment) run against a configurable LLM provider:

- **Ollama** (local, default) — `ollama serve` + `ollama pull llama3.2:3b`.
- **OpenRouter** (cloud fallback) — paste an API key on the **Settings** page.

Pick the provider on **Settings → LLM provider** (or the `LLM_PROVIDER` env var). A
containerized backend reaches host Ollama at `http://host.docker.internal:11434`.

## Next steps

- [Configuration](configuration.md) — environment variables
- [Use cases](../guides/use-cases.md) — a tour of every feature
- [API reference](../reference/api.md) — the full endpoint surface
- [Demo script](../demo.md) — a 5-minute guided walkthrough
