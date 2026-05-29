# Roadmap

From `REVISED-PRD.md` v2.3. Every P0 must ship with an AI Copilot (YC S25/W26 mandate).
> **Status as of 2026-05-29:** Foundation + Core Domain shipped (Phases 0–1); **P0.1 AI Vendor Copilot shipped** (Phase 2). P0.2–P0.4 + P1/P2 are next (Phases 3–8). Live status of record: GitHub Project #4 + Neon `tracking`. See [[Build Log]].

## Core Domain (pre-P0 foundation) — ✅ Shipped (Phases 0–1)

Vendor / PurchaseOrder / POLineItem CRUD across backend + 5 frontend screens, DKube design system, DPanel manifest, alembic migrations, 40 backend tests. Landing site live.

## P0 — Must have (demo-ready)

| # | Feature | Status | AI component | Acceptance |
|---|---------|--------|--------------|------------|
| P0.1 | **AI Vendor Copilot** | ✅ **Shipped** (Phase 2) | LLM evaluation + risk + performance prediction | Evaluate 100 vendors <10min; flag risks |
| P0.2 | **Vendor Directory** | ⬜ Next (Phase 3) | Vendor classification + data enrichment | Track 1000 vendors; auto-classify; enrich from web |
| P0.3 | **Onboarding Workflow** | ⬜ Planned (Phase 4) | Onboarding checklist + document validation | Digital workflow; doc collection; approval routing |
| P0.4 | **Performance Tracking** | ⬜ Planned (Phase 5) | Performance scoring + trend analysis | Track 10 KPIs; score 0–100; benchmark |

## P1 — Should have (v1.1–1.2) — ⬜ Planned (Phase 6)

- **P1.1 Risk Assessment** — 20 risk types, continuous monitoring, change alerts.
- **P1.2 Contract Management** — contract extraction + renewal optimization.
- **P1.3 Spend Analytics** — analyze $100M spend; identify 10% savings; suggest consolidation.
- **P1.4 Integration with Procurement** — ERP sync, PO matching, invoice reconciliation.

## P2 — Could have (v1.3+) — ⬜ Planned (Phase 7)

- **P2.1 Diversity Tracking** — verify diversity status + spend reporting.
- **P2.2 Sustainability Scoring** — carbon-footprint scoring + benchmarking.
- **P2.3 Survey & Feedback** — stakeholder sentiment analysis.
- **P2.4 Audit & Compliance** — audit scheduling + finding tracking + closure validation.

## Platform hardening — ⬜ Planned (Phase 8)

Auth (Logto), billing (Stripe), monitoring, Helm/prod deploy, docs/release. (Landing site ✅ already live.)

## Related

- [[Project Overview]]
- [[Open Issues]]
