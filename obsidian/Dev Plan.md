# DClaw Vendor — Phase-wise Dev Plan

> Synthesised on 2026-05-29 from `AGENTS.md`, `REVISED-PRD.md` (v2.3), `PRODUCT-SPEC.md`, `SCALING-PLAYBOOK.md` + a ground-truth read of the source tree.
> **Reality check:** despite docs saying "Tier 2 — Partial", the backend is a *bare scaffold* (only `models/base.py`, `repositories/base_repo.py`). No domain models/schemas/repos/routes/services; frontend `src/app` empty; no `dclaw-manifest.json`. **This plan builds the domain app from near-zero.**
> Canonical config: backend **8106**, frontend **3019**, DB `dclaw_vendor`, base path `/api/v1`.
>
> Each leaf task below has a stable ID (e.g. `V1.2`). These IDs are mirrored 1:1 into the Neon tracking DB and the GitHub Project issues. **Status here is a snapshot — the GitHub Project + Neon `tracking` schema are the live source of truth.**

Legend — **Track**: Code · Docs · Infra · Planning · AI · Frontend  ·  **Priority**: P0 · P1 · P2  ·  **Est**: hours

---

## Phase 0 — Foundation & Infra Hardening
*Goal: a clean, correctly-wired, DPanel-registered scaffold that boots end-to-end before any domain code.*

- [ ] **V0.1 — Resolve config & ports** · Infra · P0 · 1h
  - [ ] Confirm `.env.example` (backend 8106 / frontend 3019 / `dclaw_vendor`) is canonical; reconcile stale PRD ports (3032/18102)
  - [ ] Add a real `.env` for local dev (gitignored)
  - [ ] Update `obsidian/Architecture.md` "Ports TBD" note → resolved
- [ ] **V0.2 — DPanel manifest** · Infra · P0 · 1h
  - [ ] Create `frontend/public/dclaw-manifest.json` (app id `vendor`, name, category Procurement, color `#6366F1`, ports, routes)
  - [ ] Validate against another app's manifest shape (e.g. dclaw-crm)
- [ ] **V0.3 — Customize README** · Docs · P0 · 1h
  - [ ] Replace scaffold "DClaw Scaffold" text with DClaw Vendor scope, features, run instructions
  - [ ] Keep Contributors section
- [ ] **V0.4 — DB & migrations baseline** · Infra · P0 · 2h
  - [ ] Verify `core/database.py` imports `Base` from `app.models.base` (anti-pattern guard)
  - [ ] Confirm alembic env wired to async engine + `Base.metadata`
  - [ ] Establish Neon connection path (app domain schema) alongside local Postgres
- [ ] **V0.5 — Boot & CI smoke** · Infra · P0 · 2h
  - [ ] `docker compose config` passes; `docker compose up -d` healthy
  - [ ] `/health` returns `{"status":"ok"}`; frontend serves
  - [ ] Confirm `.github/workflows/ci.yml` intact and green
  - [ ] Run anti-pattern checklist from `SCALING-PLAYBOOK.md`
- [ ] **V0.6 — Adopt DKube design system** · Frontend · P0 · 3h
  - [ ] Bring in `frontend/src/styles/brand.css` (`--dk-*` tokens) — **DKube purple palette, 1:1 with dclaw-marketing**
  - [ ] Wire `frontend/tailwind.config.ts` to expose `--dk-*` tokens; light-mode only (no `dark:`)
  - [ ] Add Poppins woff2 + `@font-face`/`next/font`; `font-sans`/`font-display` → `var(--dk-font-sans)`
  - [ ] Copy `design/` reference bundle (BRAND_GUIDELINES, colors_and_type.css, preview cards, assets)
  - [ ] Keep app accent `#6366F1` for the DPanel tile only (manifest), not the UI palette
- [ ] **V0.7 — Port `dk/` primitive component library** · Frontend · P0 · 3h
  - [ ] Copy `frontend/src/components/dk/*` (28 primitives + `index.ts` + README): Button(pill)/Card/Chip/Badge/Input/Select/Dialog/Table/Tabs/Sidebar/PageHeader/…
  - [ ] Lucide icons (no emoji/hand-rolled SVG); eyeball vs `design/.../preview/*.html`
  - [ ] **All later frontend tasks (V1.7/V1.8, V2.5, V3.4, V4.5, V5.4) MUST use `Dk*` primitives** (supersedes the scaffold `ui/` set; still no shadcn CLI)

## Phase 1 — Core Domain (Vendor · PurchaseOrder · POLineItem)
*Goal: full CRUD across the PRODUCT-SPEC entities, backend + frontend, tested.*

- [ ] **V1.1 — SQLAlchemy models** · Code · P0 · 3h
  - [ ] `Vendor` (name, contact_name, email, phone, address, payment_terms, status enum active/inactive/blacklisted, timestamps)
  - [ ] `PurchaseOrder` (vendor_id FK `ondelete=SET NULL`, status enum, total, expected_delivery, notes, timestamps)
  - [ ] `POLineItem` (po_id FK `ondelete=CASCADE`, product_name, description, quantity, unit_price, received_qty, timestamps)
  - [ ] `Mapped`/`mapped_column`, `lazy="selectin"` rels, `utc_now()` for timestamps, no `default_factory`
- [ ] **V1.2 — Pydantic v2 schemas** · Code · P0 · 2h
  - [ ] Create/Update/Read for each entity; `ConfigDict(from_attributes=True)`
  - [ ] Enums shared between models and schemas
- [ ] **V1.3 — Repositories** · Code · P0 · 2h
  - [ ] `VendorRepository`, `PurchaseOrderRepository`, `POLineItemRepository` extending `BaseRepository`
  - [ ] PO total recompute helper from line items
- [ ] **V1.4 — API routers** · Code · P0 · 3h
  - [ ] `/api/v1/vendors` CRUD (+ search by name/email, status filter, pagination)
  - [ ] `/api/v1/purchase-orders` CRUD (+ vendor filter, status filter)
  - [ ] `/api/v1/po-line-items` CRUD; receive-tracking PATCH
  - [ ] Wire routers in `app/api/main.py`; all use `Depends(get_db)`
- [ ] **V1.5 — Alembic migration** · Code · P0 · 1h
  - [ ] `alembic revision --autogenerate` for the 3 tables; apply + verify
- [ ] **V1.6 — Backend tests** · Code · P0 · 3h
  - [ ] Repo + endpoint tests (httpx AsyncClient, ASGITransport, `localhost:5432`)
  - [ ] FK behaviours (SET NULL vendor delete, CASCADE PO delete)
- [ ] **V1.7 — Frontend API client + types** · Frontend · P0 · 2h
  - [ ] Add typed functions/types to `src/lib/api.ts` for all endpoints
- [ ] **V1.8 — Frontend pages** · Frontend · P0 · 6h
  - [ ] Dashboard (summary cards, recent POs, vendors-by-status, quick actions)
  - [ ] Vendors (table, search, status filter, Add Vendor modal)
  - [ ] Vendor Detail (info card edit/delete, related POs, add PO)
  - [ ] Purchase Orders (table, search, status filter, Add PO form)
  - [ ] PO Detail (line items table, receive tracking, status transitions, total)

## Phase 2 — P0.1 AI Vendor Copilot
*Goal: the mandated first-class AI Copilot — evaluate/onboard/manage vendors, accessible everywhere.*

- [ ] **V2.1 — LLM service layer** · AI · P0 · 3h
  - [ ] `services/llm.py`: Ollama local primary + OpenRouter/Kimi K2.5 cloud fallback
  - [ ] Config-driven provider selection; structured-output helper
- [ ] **V2.2 — Vendor evaluation engine** · AI · P0 · 4h
  - [ ] Evaluate a vendor: risk flags + performance prediction + summary
  - [ ] Batch evaluate (acceptance: 100 vendors < 10 min)
- [ ] **V2.3 — RAG over vendor data** · AI · P0 · 3h
  - [ ] pgvector/Qdrant index of vendor profiles + POs (only if needed for retrieval)
  - [ ] Retrieval wired into copilot context
- [ ] **V2.4 — Copilot API** · AI · P0 · 2h
  - [ ] `/api/v1/copilot/chat` (context-aware, suggests next actions)
  - [ ] Domain-data awareness + fall back to local Ollama
- [ ] **V2.5 — Copilot UI** · Frontend · P0 · 4h
  - [ ] Floating chat / sidebar on every page; streaming responses; action suggestions
- [ ] **V2.6 — Copilot tests** · Code · P0 · 2h
  - [ ] Service tests with mocked LLM; endpoint contract tests

## Phase 3 — P0.2 Vendor Directory (classification + enrichment)
- [ ] **V3.1 — AI vendor classification** · AI · P0 · 3h
  - [ ] Auto-categorise vendors (category/industry/tier) on create/update
- [ ] **V3.2 — Web data enrichment** · AI · P0 · 3h
  - [ ] Enrich vendor profile from web (domain, size, etc.); store provenance
- [ ] **V3.3 — Directory at scale** · Code · P0 · 2h
  - [ ] Pagination/indexing/filtering to track 1000 vendors performantly
- [ ] **V3.4 — Directory UI** · Frontend · P0 · 2h
  - [ ] Rich directory views: category facets, enrichment badges, bulk classify

## Phase 4 — P0.3 Onboarding Workflow
- [ ] **V4.1 — Onboarding data model** · Code · P0 · 2h
  - [ ] `OnboardingCase`, `OnboardingDocument`, `ApprovalStep` models + migration
- [ ] **V4.2 — Document storage (MinIO)** · Infra · P0 · 2h
  - [ ] MinIO bucket wiring; upload/download; secure presigned URLs
- [ ] **V4.3 — AI checklist + doc validation** · AI · P0 · 3h
  - [ ] Generate onboarding checklist; validate uploaded docs (completeness/type)
- [ ] **V4.4 — Approval routing** · Code · P0 · 2h
  - [ ] Multi-step approval state machine + status API
- [ ] **V4.5 — Onboarding UI** · Frontend · P0 · 3h
  - [ ] Wizard: collect docs → validate → route for approval → activate vendor

## Phase 5 — P0.4 Performance Tracking
- [ ] **V5.1 — KPI / score model** · Code · P0 · 2h
  - [ ] `PerformanceScore` (10 KPIs across quality/delivery/cost/compliance, 0–100) + migration
- [ ] **V5.2 — AI scoring + trend analysis** · AI · P0 · 3h
  - [ ] Compute composite score; trend over time; benchmark vs peers
- [ ] **V5.3 — Performance API** · Code · P0 · 2h
  - [ ] Endpoints for scores, trends, benchmarks
- [ ] **V5.4 — Performance UI** · Frontend · P0 · 3h
  - [ ] Scorecards, trend charts, benchmark comparison on Vendor Detail

## Phase 6 — P1 Platform Features
- [ ] **V6.1 — Risk Assessment (P1.1)** · AI · P1 · 5h
  - [ ] 20 risk types, AI risk-scoring, continuous monitoring + change alerts
- [ ] **V6.2 — Contract Management (P1.2)** · AI · P1 · 5h
  - [ ] Contract model + extraction of key terms; renewal tracking/optimization
- [ ] **V6.3 — Spend Analytics (P1.3)** · AI · P1 · 5h
  - [ ] Spend aggregation; identify ~10% savings; consolidation suggestions
- [ ] **V6.4 — Procurement Integration (P1.4)** · Code · P1 · 5h
  - [ ] ERP sync (bi-directional), PO matching, invoice reconciliation

## Phase 7 — P2 Vertical / Scale Features
- [ ] **V7.1 — Diversity Tracking (P2.1)** · AI · P2 · 4h
  - [ ] Verify diversity status; track spend; reports
- [ ] **V7.2 — Sustainability Scoring (P2.2)** · AI · P2 · 4h
  - [ ] Carbon-footprint scoring + benchmarking + targets
- [ ] **V7.3 — Survey & Feedback (P2.3)** · AI · P2 · 3h
  - [ ] Stakeholder surveys; sentiment analysis; trend
- [ ] **V7.4 — Audit & Compliance (P2.4)** · Code · P2 · 4h
  - [ ] Audit scheduling; finding tracking; closure validation

## Phase 8 — Platform Hardening & Release
- [ ] **V8.1 — Auth (Logto)** · Infra · P1 · 3h
  - [ ] JWT validation on protected routes; frontend auth flow
- [ ] **V8.2 — Billing (Stripe)** · Infra · P2 · 3h
  - [ ] Metered/per-seat plan wiring
- [ ] **V8.3 — Monitoring** · Infra · P1 · 2h
  - [ ] Prometheus metrics + Grafana dashboards; structlog everywhere (no `print`)
- [ ] **V8.4 — Helm / prod deploy** · Infra · P1 · 3h
  - [ ] `helm/values.yaml` app name/images/ports; CloudNativePG; TLS ingress
- [ ] **V8.5 — Docs & release** · Docs · P1 · 2h
  - [ ] Fill `docs/` (getting-started, guides, reference, releases); changelog; demo script
- [ ] **V8.6 — Landing site (standalone `landing/` app)** · Frontend · P1 · 4h
  - [ ] Scaffold standalone `landing/` Next.js app at repo root (own `package.json`: next + react + lucide-react) — mirrors dclaw-marketing's `landing/`; **Vercel hookup deferred**
  - [ ] Apply DKube brand (Poppins, `--dk-*` purple tokens, dclaw logos in `public/brand/`)
  - [ ] **Lean single page**: Hero (eyebrow + headline + lede) · Features · FinalCTA · Footer (©One Convergence · DKube tagline)
  - [ ] **Hero CTA button → app frontend** (`NEXT_PUBLIC_APP_URL`, dev `http://localhost:3019`)
  - [ ] Responsive, light-mode; note Vercel deploy as a follow-up (not wired now)

---

## Cross-cutting acceptance gates
- **Design**: all UI uses the DKube design system (mirrors dclaw-marketing) — `--dk-*` purple tokens, Poppins, light-mode only, pill CTAs, `Dk*` primitives, Lucide icons. No raw Tailwind grays, no `dark:` variants. Established in V0.6/V0.7.
- Every P0 ships with the AI Copilot wired in (YC S25/W26 mandate).
- No anti-patterns from `AGENTS.md` (no `declarative_base()`, no `MappedAsDataclass`, no `MOCK_*` dicts, healthchecks use `urllib`, `ARG NEXT_PUBLIC_API_URL` present, `pytest-asyncio==0.24.0` pinned, CI intact).
- Each new model → alembic migration; each repo/endpoint → tests.

## Related
- [[Home]] · [[Roadmap]] · [[Architecture]] · [[Open Issues]] · [[Project Overview]]
