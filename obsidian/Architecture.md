# Architecture

## Stack (the "sacred" DClaw stack)

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14+ App Router · Tailwind · pre-built UI components (no shadcn CLI) |
| Backend | FastAPI · SQLAlchemy 2.0 async (`Mapped`/`mapped_column`) · Pydantic v2 · asyncpg |
| DB | PostgreSQL 16 (CloudNativePG operator in K8s) |
| Vector | Qdrant / pgvector (only if RAG/semantic search) |
| Cache/Bus | Redis 7.x |
| Object storage | MinIO (vendor documents) |
| Auth | Logto (JWT validation on protected routes) |
| LLM | Ollama (local) · OpenRouter + Kimi K2.5 (cloud fallback) |
| Container | Docker Compose (dev) · Helm chart (prod) |

## Ports (resolved — V0.1)

| Frontend | Backend | DB |
|----------|---------|-----|
| 3060 | 8146 | `dclaw_vendor` |

> **Canonical (locked V0.1):** `8146` backend / `3060` frontend / DB `dclaw_vendor`, base path `/api/v1`.
> Reconciled from the shared DClaw port registry (AGENTS.md). The stale `REVISED-PRD.md` ports
> (3032 / 18102) are placeholders and are superseded by these. `docker-compose.yml`, both
> Dockerfiles, `.env.example`, and AGENTS.md all agree on `8146 / 3060`.

## API surface (as built — 16 routers under `/api/v1`)

```
Core      /vendors  /purchase-orders  /po-line-items
AI        /copilot  /settings (LLM provider)
Directory /vendors/facets  /vendors/{id}/classify|enrich  /vendors/classify-batch
Onboard   /onboarding/cases|documents|steps  (checklist · upload · validate · approve · activate)
Perf      /performance/vendors/{id}/score|scores|latest|trend|benchmark
Risk      /risk/vendors/{id}/assess|latest|history   /risk/types
Contracts /contracts (+ /renewals · /{id}/extract)
Analytics /analytics/spend  /analytics/spend/insights
Integration /integration/status|sync|reconciliation
ESG/P2    /sustainability/...  /diversity/report  /surveys/...  /audits/...
Platform  /auth/{config,me}  /billing/{plans,subscription,checkout}  /metrics  /health
```

Full reference: `docs/reference/api.md` + the live OpenAPI at `/openapi.json`.

## Realized infrastructure (Phase 6–8)

- **Auth** — Logto JWT (JWKS RS256) in `core/auth.py`, gating `vendors` + `purchase-orders`; feature-flagged via `AUTH_ENABLED` (open in dev/CI).
- **Billing** — `services/billing.py` Mock/Stripe providers; per-seat plans + checkout.
- **Storage** — `services/storage.py` Local (default) / MinIO backends for onboarding docs, presigned URLs.
- **ERP** — `services/erp.py` Mock/HTTP connectors; sync + invoice reconciliation.
- **Observability** — `core/observability.py` structlog (JSON/console) + Prometheus middleware + `/metrics`; Grafana dashboard in `monitoring/`.
- **Deploy** — Helm chart with CloudNativePG `Cluster`, TLS ingress, Prometheus scrape annotations.

> Integrations (Logto / Stripe / MinIO / ERP) are code-complete in **test-mode**: mock backends by default, live on real credentials. Redis is reserved (not yet used). pgvector/Qdrant deferred — retrieval is query-based over the structured dataset.

## Architecture lock — DO NOT CHANGE

- `DeclarativeBase` from `app.models.base` — never `declarative_base()` / `MappedAsDataclass`.
- Repository pattern + `Depends(get_db)`; no manual `AsyncSession`, no mock dicts.
- `pytest-asyncio==0.24.0` pinned; tests use `localhost:5432`.
- Frontend Dockerfile declares `ARG NEXT_PUBLIC_API_URL` before build.
- No shadcn CLI / `@base-ui/react`. Don't delete `.github/workflows/ci.yml`.
- FK conventions: `ondelete="CASCADE"` for child tables (POLineItem→PO), `ondelete="SET NULL"` for optional refs (PO→Vendor).

## Related

- [[Project Overview]]
- [[Glossary]]
- [[Open Issues]]
