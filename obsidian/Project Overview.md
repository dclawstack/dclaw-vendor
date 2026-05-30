# Project Overview

## What DClaw Vendor is

**An AI vendor / supplier management and procurement app.** It evaluates, onboards, and manages vendors; maintains a centralized vendor directory; runs onboarding workflows with document collection; and scores vendor performance on quality, delivery, cost, and compliance. An AI Vendor Copilot is the first-class P0 entry point (per the DClaw AI-Copilot mandate).

## Core value props

- **AI Vendor Copilot** — evaluate, onboard, and manage vendors with LLM evaluation + risk assessment + performance prediction (evaluate 100 vendors in <10 min).
- **Vendor directory** — centralized database with AI classification and web data enrichment (track 1000 vendors).
- **Onboarding workflow** — digital document collection, validation, and approval routing.
- **Performance tracking** — score 0–100 across 10 KPIs with trend analysis and benchmarking.

## Domain model (from PRODUCT-SPEC)

- **Vendor** — name, contact, payment terms (e.g. Net 30), status (active/inactive/blacklisted).
- **PurchaseOrder** — vendor FK (SET NULL), status (draft→received→cancelled), total, expected delivery.
- **POLineItem** — product, quantity, unit price, received quantity (for partial-receipt tracking).

Screens: Dashboard · Vendors · Vendor Detail · Purchase Orders · PO Detail (line items + receive tracking).

## Maturity

🟢 Tier 3 (Complete) — **48 of 48 tasks done (v1.0 GA, 2026-05-30).** All 9 phases shipped & merged; 117 backend tests green.

- **Phase 0 ✅** — scaffold hardened, DPanel-registered, DKube design system + `dk/` primitives.
- **Phase 1 ✅** — Vendor / PurchaseOrder / POLineItem: models, schemas, repositories, CRUD API, migration + 5 frontend screens.
- **Phase 2 ✅ (AI Vendor Copilot)** — LLM service (Ollama + OpenRouter, structured output), evaluation engine, retrieval, `/copilot/chat`, floating Copilot UI + "Evaluate (AI)".
- **Phase 3 ✅ (Vendor Directory)** — AI classification (category/industry/tier), web/AI enrichment with provenance, facets, directory UI.
- **Phase 4 ✅ (Onboarding)** — cases/docs (MinIO/local storage), AI checklist + document validation, multi-step approval state machine, wizard UI.
- **Phase 5 ✅ (Performance)** — 10-KPI scorecards, AI scoring, trends, peer benchmarks.
- **Phase 6 ✅ (P1)** — risk assessment (20 types + monitoring), contracts (AI extract), spend analytics (~10% savings), ERP integration.
- **Phase 7 ✅ (P2)** — diversity tracking, ESG/sustainability scoring, surveys + AI sentiment, audits + closure validation.
- **Phase 8 ✅ (Hardening/release)** — Logto auth, Stripe billing, Prometheus + structlog monitoring, Helm (CloudNativePG + TLS), docs, landing site.

Runtime DB tables live in the Neon `vendor` schema (via `schema_translate_map`); local/CI use `public`. The plan is **fully complete** — see [[Build Log]] for the per-task PR record, [[Roadmap]], [[Open Issues]].

## Related

- [[Architecture]]
- [[Roadmap]]
- [[Glossary]]
