# Changelog

## v1.0.0 — General Availability

The full vendor-management platform, AI-native across every module. Built in nine
phases (V0–V8); each P0 ships with the AI Copilot wired in.

### Phase 0 — Foundation
- Config/ports reconciled (backend 8146, frontend 3060), DPanel manifest, DB + alembic baseline, CI smoke.
- DKube design system adopted (`--dk-*` tokens, Poppins, `Dk*` primitive library).

### Phase 1 — Core domain
- Vendor / PurchaseOrder / POLineItem: models, schemas, repositories, CRUD API, migration, tests.
- Typed frontend API client + 5 screens (dashboard, vendors, vendor detail, POs, PO detail).

### Phase 2 — AI Vendor Copilot
- LLM service layer (Ollama local + OpenRouter cloud, structured output).
- Vendor evaluation engine (single + batch), RAG-style retrieval, copilot chat API + floating UI.

### Phase 3 — Vendor Directory
- AI classification (category/industry/tier), web/AI enrichment with provenance, facets, directory UI.

### Phase 4 — Onboarding workflow
- Cases, documents (MinIO/local storage), AI checklist + document validation, multi-step approval state machine, wizard UI.

### Phase 5 — Performance tracking
- 10-KPI scorecards (quality/delivery/cost/compliance), AI scoring, trends, peer benchmarks, vendor-detail panel.

### Phase 6 — P1 platform features
- Risk assessment (20-type catalog, AI scoring, change-alert monitoring).
- Contract management (AI key-term extraction, renewal tracking).
- Spend analytics (aggregation + AI ~10% savings + consolidation).
- Procurement/ERP integration (sync, PO matching, invoice reconciliation).

### Phase 7 — P2 vertical features
- Diversity tracking + spend reporting.
- Sustainability (ESG) scoring with carbon footprint + targets.
- Stakeholder surveys with AI sentiment + trend.
- Audit & compliance with finding tracking + closure validation.

### Phase 8 — Hardening & release
- Auth (Logto JWT, feature-flagged), Billing (Stripe, per-seat), Monitoring (Prometheus + structlog + Grafana), Helm prod deploy (CloudNativePG, TLS ingress), this documentation set, and the standalone landing site.

### Notes
- External integrations (Logto, Stripe, ERP, MinIO) ship **code-complete in test-mode**:
  feature-flagged, with mock backends by default, and go live the moment real
  credentials are supplied.

## v0.1.0 — Initial scaffold
- Next.js frontend + FastAPI backend scaffold, Helm chart, docs structure.
