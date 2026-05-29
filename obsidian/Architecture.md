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

## Ports

| Source | Frontend | Backend |
|--------|----------|---------|
| `REVISED-PRD.md` (TBD) | 3032 | 18102 |
| `dclaw-seo` AGENTS port registry | 3019 | 8106 |

> The PRD ports are placeholders; the shared registry (in dclaw-seo's AGENTS.md) lists `dclaw-vendor` at `8106 / 3019`. Assign canonically before build. DB name `dclaw_vendor`.

## API surface (PRODUCT-SPEC)

```
/api/v1/vendors           CRUD
/api/v1/purchase-orders   CRUD
/api/v1/po-line-items     CRUD
```

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
