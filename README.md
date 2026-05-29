# DClaw Vendor

> **AI-native vendor & purchase order management** — part of the DClaw vertical SaaS stack.

Supplier directory, purchase orders, onboarding workflows, performance tracking, and a
first-class **AI Vendor Copilot** for procurement teams and operations managers.

## Scope

DClaw Vendor manages the full supplier lifecycle around three core domain entities:

- **Vendor** — supplier records (contact, payment terms, status: active/inactive/blacklisted)
- **PurchaseOrder** — POs against a vendor (status: draft → sent → partial → received / cancelled)
- **POLineItem** — line items per PO with receive tracking

See [`PRODUCT-SPEC.md`](PRODUCT-SPEC.md) for the entity/API contract and
[`obsidian/Dev Plan.md`](obsidian/Dev%20Plan.md) for the phased build plan (V0.1–V8.6).

## Features

| Phase | Capability |
|-------|------------|
| Core | Vendor / PO / line-item CRUD, dashboard, search, status filters |
| P0.1 | AI Vendor Copilot — evaluate, onboard, and manage vendors (everywhere) |
| P0.2 | Vendor Directory — AI classification + web enrichment, at scale |
| P0.3 | Onboarding workflow — document collection, AI validation, approval routing |
| P0.4 | Performance tracking — KPI scoring, trends, benchmarking |
| P1/P2 | Risk, contracts, spend analytics, diversity/sustainability, audit |

## Stack

- **Backend:** FastAPI · SQLAlchemy 2.0 (async) · Pydantic v2 · asyncpg · Alembic
- **Frontend:** Next.js 14 (App Router) · Tailwind · DKube design system (`dk/` primitives)
- **DB:** PostgreSQL 16 (Neon for runtime; CloudNativePG in K8s)
- **AI:** Ollama (local) · OpenRouter / Kimi K2.5 (cloud fallback)
- **Infra:** Docker Compose (dev) · Helm (prod)

## Configuration

| Setting | Value |
|---------|-------|
| Backend port | `8146` |
| Frontend port | `3060` |
| Database | `dclaw_vendor` |
| API base path | `/api/v1` |

Copy `.env.example` to `.env` and adjust as needed. See [`AGENTS.md`](AGENTS.md) for the
architecture lock and anti-patterns — **read it before making code changes.**

## Run locally

```bash
# Backend (FastAPI on :8146)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8146
# Health: http://localhost:8146/health/  ->  {"status":"ok"}

# Frontend (Next.js on :3060)
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8146 npm run dev
```

Or with Docker:

```bash
docker compose up -d   # postgres + backend(:8146) + frontend(:3060)
```

## Tests

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_vendor_test \
  python -m pytest -v
```

Tests require PostgreSQL on `localhost:5432` (matches CI). Keep `pytest-asyncio==0.24.0` pinned.

## Contributors

- [Deepro Mallick (@deepro713)](https://github.com/deepro713)
