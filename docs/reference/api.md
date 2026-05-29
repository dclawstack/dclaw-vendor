# API Reference

Base path: `/api/v1`. Interactive OpenAPI docs are served at `/docs` and the raw
spec at `/openapi.json`.

## Authentication

Auth is **Logto JWT**, disabled by default (dev/CI run open). When `AUTH_ENABLED=true`,
the `vendors` and `purchase-orders` routes require a Bearer token:

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8146/api/v1/vendors
```

- `GET /api/v1/auth/config` — whether auth is enabled + Logto endpoint (public).
- `GET /api/v1/auth/me` — the current user (anonymous when auth is off).

## Health & monitoring

- `GET /health/` → `{"status":"ok"}`
- `GET /metrics` → Prometheus metrics (`http_requests_total`, `http_request_duration_seconds`).

## Core domain

| Resource | Endpoints |
|---|---|
| **Vendors** | `GET/POST /vendors`, `GET/PATCH/DELETE /vendors/{id}`, `GET /vendors/facets` |
| **Purchase orders** | `GET/POST /purchase-orders`, `GET/PATCH/DELETE /purchase-orders/{id}` |
| **PO line items** | `GET/POST /po-line-items`, `PATCH/DELETE /po-line-items/{id}` |

Vendors support `search`, `status`, `category`, `tier` filters + pagination.

## AI Copilot (Phase 2)

- `POST /copilot/chat` — context-aware chat grounded in your vendor/PO data.
- `POST /copilot/vendors/{id}/evaluate` — risk + outlook + recommendation.
- `POST /copilot/vendors/evaluate-batch` — bulk evaluation.

## Vendor Directory (Phase 3)

- `POST /vendors/{id}/classify`, `POST /vendors/classify-batch` — AI category/industry/tier.
- `POST /vendors/{id}/enrich` — web/AI profile enrichment with provenance.
- `GET /vendors/facets` — category/tier/status/industry counts.

## Onboarding (Phase 4)

- `POST/GET /onboarding/cases`, `GET/DELETE /onboarding/cases/{id}`
- `POST /onboarding/cases/{id}/checklist` — AI checklist
- `POST /onboarding/cases/{id}/documents` — upload (multipart); `GET .../documents/download`
- `POST /onboarding/documents/{id}/validate` — AI document validation
- `POST /onboarding/cases/{id}/submit`, `POST /onboarding/steps/{id}/decision`, `POST /onboarding/cases/{id}/activate`

## Performance (Phase 5)

- `POST /performance/vendors/{id}/score` — AI KPI scoring (10 KPIs → 4 dimensions → overall)
- `GET /performance/vendors/{id}/{scores,latest,trend,benchmark}`

## Risk & Contracts (Phase 6)

- `POST /risk/vendors/{id}/assess` (20-type catalog + change alerts), `GET /risk/vendors/{id}/{latest,history}`, `GET /risk/types`
- `GET/POST /contracts`, `GET/PATCH/DELETE /contracts/{id}`, `GET /contracts/renewals`, `POST /contracts/{id}/extract`

## Analytics & Integration (Phase 6)

- `GET /analytics/spend`, `POST /analytics/spend/insights` (~10% savings + consolidation)
- `GET /integration/status`, `POST /integration/sync`, `GET /integration/reconciliation`

## Diversity, Sustainability, Surveys, Audits (Phase 7)

- `GET /diversity/report`
- `POST /sustainability/vendors/{id}/score`, `GET /sustainability/vendors/{id}/{latest,history}`
- `GET/POST /surveys`, `POST /surveys/{id}/responses`, `GET /surveys/vendors/{id}/sentiment`
- `GET/POST /audits`, `POST /audits/{id}/findings`, `PATCH /audits/findings/{id}`, `POST /audits/{id}/close`

## Billing (Phase 8)

- `GET /billing/plans`, `GET /billing/subscription`, `POST /billing/checkout`

## Errors

Errors return a FastAPI problem body: `{"detail": "..."}` with an appropriate status
(`404` not found, `409` invalid state transition, `422` validation, `502` LLM unavailable).
