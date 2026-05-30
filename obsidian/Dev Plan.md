# DClaw Vendor — Phase-wise Dev Plan

> Synthesised on 2026-05-29 from `AGENTS.md`, `REVISED-PRD.md` (v2.3), `PRODUCT-SPEC.md`, `SCALING-PLAYBOOK.md` + a ground-truth read of the source tree.
> **✅ COMPLETE (2026-05-30): all 9 phases done — 48/48 tasks (V0.1–V8.6) shipped & merged.** What began as a bare scaffold is now the full AI-native vendor platform: core domain, AI Copilot, directory, onboarding, performance, risk, contracts, analytics, ERP integration, diversity, sustainability, surveys, audits, auth, billing, monitoring, Helm, docs, and landing. 117 backend tests green; migration head `a1c5e9b3d7f2`.
> Canonical config: backend **8146**, frontend **3060**, DB `dclaw_vendor`, base path `/api/v1`.
>
> Each leaf task below has a stable ID (e.g. `V1.2`), mirrored 1:1 into the Neon tracking DB and the GitHub Project issues — **all now `done` / `Done` / closed**. See [[Build Log]] for the per-task PR record; boxes below are all ticked to match.

Legend — **Track**: Code · Docs · Infra · Planning · AI · Frontend  ·  **Priority**: P0 · P1 · P2  ·  **Est**: hours

---

## Phase 0 — Foundation & Infra Hardening
*Goal: a clean, correctly-wired, DPanel-registered scaffold that boots end-to-end before any domain code.*

- [x] **V0.1 — Resolve config & ports** · Infra · P0 · 1h
  - [x] Confirm `.env.example` (backend 8146 / frontend 3060 / `dclaw_vendor`) is canonical; reconcile stale PRD ports (3032/18102)
  - [x] Add a real `.env` for local dev (gitignored)
  - [x] Update `obsidian/Architecture.md` "Ports TBD" note → resolved
- [x] **V0.2 — DPanel manifest** · Infra · P0 · 1h
  - [x] Create `frontend/public/dclaw-manifest.json` (app id `vendor`, name, category Procurement, color `#6366F1`, ports, routes)
  - [x] Validate against another app's manifest shape (e.g. dclaw-crm)
- [x] **V0.3 — Customize README** · Docs · P0 · 1h
  - [x] Replace scaffold "DClaw Scaffold" text with DClaw Vendor scope, features, run instructions
  - [x] Keep Contributors section
- [x] **V0.4 — DB & migrations baseline** · Infra · P0 · 2h
  - [x] Verify `core/database.py` imports `Base` from `app.models.base` (anti-pattern guard)
  - [x] Confirm alembic env wired to async engine + `Base.metadata`
  - [x] Establish Neon connection path (app domain schema) alongside local Postgres
- [x] **V0.5 — Boot & CI smoke** · Infra · P0 · 2h
  - [x] `docker compose config` passes; `docker compose up -d` healthy
  - [x] `/health` returns `{"status":"ok"}`; frontend serves
  - [x] Confirm `.github/workflows/ci.yml` intact and green
  - [x] Run anti-pattern checklist from `SCALING-PLAYBOOK.md`
- [x] **V0.6 — Adopt DKube design system** · Frontend · P0 · 3h
  - [x] Bring in `frontend/src/styles/brand.css` (`--dk-*` tokens) — **DKube purple palette, 1:1 with dclaw-marketing**
  - [x] Wire `frontend/tailwind.config.ts` to expose `--dk-*` tokens; light-mode only (no `dark:`)
  - [x] Add Poppins woff2 + `@font-face`/`next/font`; `font-sans`/`font-display` → `var(--dk-font-sans)`
  - [x] Copy `design/` reference bundle (BRAND_GUIDELINES, colors_and_type.css, preview cards, assets)
  - [x] Keep app accent `#6366F1` for the DPanel tile only (manifest), not the UI palette
- [x] **V0.7 — Port `dk/` primitive component library** · Frontend · P0 · 3h
  - [x] Copy `frontend/src/components/dk/*` (28 primitives + `index.ts` + README): Button(pill)/Card/Chip/Badge/Input/Select/Dialog/Table/Tabs/Sidebar/PageHeader/…
  - [x] Lucide icons (no emoji/hand-rolled SVG); eyeball vs `design/.../preview/*.html`
  - [x] **All later frontend tasks (V1.7/V1.8, V2.5, V3.4, V4.5, V5.4) MUST use `Dk*` primitives** (supersedes the scaffold `ui/` set; still no shadcn CLI)

## Phase 1 — Core Domain (Vendor · PurchaseOrder · POLineItem)
*Goal: full CRUD across the PRODUCT-SPEC entities, backend + frontend, tested.*

- [x] **V1.1 — SQLAlchemy models** · Code · P0 · 3h
  - [x] `Vendor` (name, contact_name, email, phone, address, payment_terms, status enum active/inactive/blacklisted, timestamps)
  - [x] `PurchaseOrder` (vendor_id FK `ondelete=SET NULL`, status enum, total, expected_delivery, notes, timestamps)
  - [x] `POLineItem` (po_id FK `ondelete=CASCADE`, product_name, description, quantity, unit_price, received_qty, timestamps)
  - [x] `Mapped`/`mapped_column`, `lazy="selectin"` rels, `utc_now()` for timestamps, no `default_factory`
- [x] **V1.2 — Pydantic v2 schemas** · Code · P0 · 2h
  - [x] Create/Update/Read for each entity; `ConfigDict(from_attributes=True)`
  - [x] Enums shared between models and schemas
- [x] **V1.3 — Repositories** · Code · P0 · 2h
  - [x] `VendorRepository`, `PurchaseOrderRepository`, `POLineItemRepository` extending `BaseRepository`
  - [x] PO total recompute helper from line items
- [x] **V1.4 — API routers** · Code · P0 · 3h
  - [x] `/api/v1/vendors` CRUD (+ search by name/email, status filter, pagination)
  - [x] `/api/v1/purchase-orders` CRUD (+ vendor filter, status filter)
  - [x] `/api/v1/po-line-items` CRUD; receive-tracking PATCH
  - [x] Wire routers in `app/api/main.py`; all use `Depends(get_db)`
- [x] **V1.5 — Alembic migration** · Code · P0 · 1h
  - [x] `alembic revision --autogenerate` for the 3 tables; apply + verify
- [x] **V1.6 — Backend tests** · Code · P0 · 3h
  - [x] Repo + endpoint tests (httpx AsyncClient, ASGITransport, `localhost:5432`)
  - [x] FK behaviours (SET NULL vendor delete, CASCADE PO delete)
- [x] **V1.7 — Frontend API client + types** · Frontend · P0 · 2h
  - [x] Add typed functions/types to `src/lib/api.ts` for all endpoints
- [x] **V1.8 — Frontend pages** · Frontend · P0 · 6h
  - [x] Dashboard (summary cards, recent POs, vendors-by-status, quick actions)
  - [x] Vendors (table, search, status filter, Add Vendor modal)
  - [x] Vendor Detail (info card edit/delete, related POs, add PO)
  - [x] Purchase Orders (table, search, status filter, Add PO form)
  - [x] PO Detail (line items table, receive tracking, status transitions, total)

## Phase 2 — P0.1 AI Vendor Copilot
*Goal: the mandated first-class AI Copilot — evaluate/onboard/manage vendors, accessible everywhere.*

- [x] **V2.1 — LLM service layer** · AI · P0 · 3h
  - [x] `services/llm.py`: Ollama local primary + OpenRouter/Kimi K2.5 cloud fallback
  - [x] Config-driven provider selection; structured-output helper
- [x] **V2.2 — Vendor evaluation engine** · AI · P0 · 4h
  - [x] Evaluate a vendor: risk flags + performance prediction + summary
  - [x] Batch evaluate (acceptance: 100 vendors < 10 min)
- [x] **V2.3 — RAG over vendor data** · AI · P0 · 3h
  - [x] pgvector/Qdrant index of vendor profiles + POs (only if needed for retrieval)
  - [x] Retrieval wired into copilot context
- [x] **V2.4 — Copilot API** · AI · P0 · 2h
  - [x] `/api/v1/copilot/chat` (context-aware, suggests next actions)
  - [x] Domain-data awareness + fall back to local Ollama
- [x] **V2.5 — Copilot UI** · Frontend · P0 · 4h
  - [x] Floating chat / sidebar on every page; streaming responses; action suggestions
- [x] **V2.6 — Copilot tests** · Code · P0 · 2h
  - [x] Service tests with mocked LLM; endpoint contract tests

## Phase 3 — P0.2 Vendor Directory (classification + enrichment)
- [x] **V3.1 — AI vendor classification** · AI · P0 · 3h
  - [x] Auto-categorise vendors (category/industry/tier) on create/update
- [x] **V3.2 — Web data enrichment** · AI · P0 · 3h
  - [x] Enrich vendor profile from web (domain, size, etc.); store provenance
- [x] **V3.3 — Directory at scale** · Code · P0 · 2h
  - [x] Pagination/indexing/filtering to track 1000 vendors performantly
- [x] **V3.4 — Directory UI** · Frontend · P0 · 2h
  - [x] Rich directory views: category facets, enrichment badges, bulk classify

## Phase 4 — P0.3 Onboarding Workflow
- [x] **V4.1 — Onboarding data model** · Code · P0 · 2h
  - [x] `OnboardingCase`, `OnboardingDocument`, `ApprovalStep` models + migration
- [x] **V4.2 — Document storage (MinIO)** · Infra · P0 · 2h
  - [x] MinIO bucket wiring; upload/download; secure presigned URLs
- [x] **V4.3 — AI checklist + doc validation** · AI · P0 · 3h
  - [x] Generate onboarding checklist; validate uploaded docs (completeness/type)
- [x] **V4.4 — Approval routing** · Code · P0 · 2h
  - [x] Multi-step approval state machine + status API
- [x] **V4.5 — Onboarding UI** · Frontend · P0 · 3h
  - [x] Wizard: collect docs → validate → route for approval → activate vendor

## Phase 5 — P0.4 Performance Tracking
- [x] **V5.1 — KPI / score model** · Code · P0 · 2h
  - [x] `PerformanceScore` (10 KPIs across quality/delivery/cost/compliance, 0–100) + migration
- [x] **V5.2 — AI scoring + trend analysis** · AI · P0 · 3h
  - [x] Compute composite score; trend over time; benchmark vs peers
- [x] **V5.3 — Performance API** · Code · P0 · 2h
  - [x] Endpoints for scores, trends, benchmarks
- [x] **V5.4 — Performance UI** · Frontend · P0 · 3h
  - [x] Scorecards, trend charts, benchmark comparison on Vendor Detail

## Phase 6 — P1 Platform Features
- [x] **V6.1 — Risk Assessment (P1.1)** · AI · P1 · 5h
  - [x] 20 risk types, AI risk-scoring, continuous monitoring + change alerts
- [x] **V6.2 — Contract Management (P1.2)** · AI · P1 · 5h
  - [x] Contract model + extraction of key terms; renewal tracking/optimization
- [x] **V6.3 — Spend Analytics (P1.3)** · AI · P1 · 5h
  - [x] Spend aggregation; identify ~10% savings; consolidation suggestions
- [x] **V6.4 — Procurement Integration (P1.4)** · Code · P1 · 5h
  - [x] ERP sync (bi-directional), PO matching, invoice reconciliation

## Phase 7 — P2 Vertical / Scale Features
- [x] **V7.1 — Diversity Tracking (P2.1)** · AI · P2 · 4h
  - [x] Verify diversity status; track spend; reports
- [x] **V7.2 — Sustainability Scoring (P2.2)** · AI · P2 · 4h
  - [x] Carbon-footprint scoring + benchmarking + targets
- [x] **V7.3 — Survey & Feedback (P2.3)** · AI · P2 · 3h
  - [x] Stakeholder surveys; sentiment analysis; trend
- [x] **V7.4 — Audit & Compliance (P2.4)** · Code · P2 · 4h
  - [x] Audit scheduling; finding tracking; closure validation

## Phase 8 — Platform Hardening & Release
- [x] **V8.1 — Auth (Logto)** · Infra · P1 · 3h
  - [x] JWT validation on protected routes; frontend auth flow
- [x] **V8.2 — Billing (Stripe)** · Infra · P2 · 3h
  - [x] Metered/per-seat plan wiring
- [x] **V8.3 — Monitoring** · Infra · P1 · 2h
  - [x] Prometheus metrics + Grafana dashboards; structlog everywhere (no `print`)
- [x] **V8.4 — Helm / prod deploy** · Infra · P1 · 3h
  - [x] `helm/values.yaml` app name/images/ports; CloudNativePG; TLS ingress
- [x] **V8.5 — Docs & release** · Docs · P1 · 2h
  - [x] Fill `docs/` (getting-started, guides, reference, releases); changelog; demo script
- [x] **V8.6 — Landing site (standalone `landing/` app)** · Frontend · P1 · 4h
  - [x] Scaffold standalone `landing/` Next.js app at repo root (own `package.json`: next + react + lucide-react) — mirrors dclaw-marketing's `landing/`; **Vercel hookup deferred**
  - [x] Apply DKube brand (Poppins, `--dk-*` purple tokens, dclaw logos in `public/brand/`)
  - [x] **Lean single page**: Hero (eyebrow + headline + lede) · Features · FinalCTA · Footer (©One Convergence · DKube tagline)
  - [x] **Hero CTA button → app frontend** (`NEXT_PUBLIC_APP_URL`, dev `http://localhost:3060`)
  - [x] Responsive, light-mode; note Vercel deploy as a follow-up (not wired now)

---

## Cross-cutting acceptance gates
- **Design**: all UI uses the DKube design system (mirrors dclaw-marketing) — `--dk-*` purple tokens, Poppins, light-mode only, pill CTAs, `Dk*` primitives, Lucide icons. No raw Tailwind grays, no `dark:` variants. Established in V0.6/V0.7.
- Every P0 ships with the AI Copilot wired in (YC S25/W26 mandate).
- No anti-patterns from `AGENTS.md` (no `declarative_base()`, no `MappedAsDataclass`, no `MOCK_*` dicts, healthchecks use `urllib`, `ARG NEXT_PUBLIC_API_URL` present, `pytest-asyncio==0.24.0` pinned, CI intact).
- Each new model → alembic migration; each repo/endpoint → tests.

## Related
- [[Home]] · [[Roadmap]] · [[Architecture]] · [[Open Issues]] · [[Project Overview]]
