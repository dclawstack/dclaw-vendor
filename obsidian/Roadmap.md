# Roadmap

From `REVISED-PRD.md` v2.3. Every P0 must ship with an AI Copilot (YC S25/W26 mandate).
> **✅ Status as of 2026-05-30: every roadmap item shipped (v1.0 GA).** P0.1–P0.4, all P1, all P2, and platform hardening are complete. Live status of record: GitHub Project #4 (48 Done) + Neon `tracking` (48 done). See [[Build Log]].

## Core Domain (pre-P0 foundation) — ✅ Shipped (Phases 0–1)

Vendor / PurchaseOrder / POLineItem CRUD across backend + 5 frontend screens, DKube design system, DPanel manifest, alembic migrations. Landing site live.

## P0 — Must have (demo-ready) — ✅ All shipped

| # | Feature | Status | AI component | Acceptance |
|---|---------|--------|--------------|------------|
| P0.1 | **AI Vendor Copilot** | ✅ Shipped (Phase 2) | LLM evaluation + risk + performance prediction | Evaluate 100 vendors <10min; flag risks |
| P0.2 | **Vendor Directory** | ✅ Shipped (Phase 3) | Classification + web/AI enrichment | Track 1000 vendors; auto-classify; enrich from web |
| P0.3 | **Onboarding Workflow** | ✅ Shipped (Phase 4) | AI checklist + document validation | Digital workflow; doc collection; approval routing |
| P0.4 | **Performance Tracking** | ✅ Shipped (Phase 5) | Performance scoring + trend analysis | Track 10 KPIs; score 0–100; benchmark |

## P1 — Should have — ✅ Shipped (Phase 6)

- **P1.1 Risk Assessment** ✅ — 20 risk types, AI scoring, change-alert monitoring.
- **P1.2 Contract Management** ✅ — AI key-term extraction + renewal tracking.
- **P1.3 Spend Analytics** ✅ — spend aggregation; AI ~10% savings + consolidation.
- **P1.4 Integration with Procurement** ✅ — ERP sync, PO matching, invoice reconciliation.

## P2 — Could have — ✅ Shipped (Phase 7)

- **P2.1 Diversity Tracking** ✅ — diversity attributes + spend reporting.
- **P2.2 Sustainability Scoring** ✅ — ESG scores + carbon footprint + targets.
- **P2.3 Survey & Feedback** ✅ — surveys with AI sentiment + trend.
- **P2.4 Audit & Compliance** ✅ — audit scheduling + finding tracking + closure validation.

## Platform hardening — ✅ Shipped (Phase 8)

Auth (Logto JWT, feature-flagged) ✅ · billing (Stripe, per-seat) ✅ · monitoring (Prometheus + structlog + Grafana) ✅ · Helm/prod deploy (CloudNativePG + TLS ingress) ✅ · docs/release ✅ · landing site ✅ (live).

> **Note:** external integrations (Logto, Stripe, ERP, MinIO) ship code-complete in **test-mode** — feature-flagged with mock backends, live on real credentials. Future polish: Copilot token streaming; repoint landing CTA when the app is publicly hosted.

## Related

- [[Project Overview]]
- [[Open Issues]]
