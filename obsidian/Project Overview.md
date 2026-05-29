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

Tier 2 (Building). **Phase 0 complete** — scaffold hardened, DPanel-registered, DKube design system + `dk/` primitives in place. **Phase 1 backend complete** — Vendor / PurchaseOrder / POLineItem models, schemas, repositories, CRUD API, alembic migration, and tests (20 passing). Runtime DB tables live in the Neon `vendor` schema (via `schema_translate_map`); local/CI use `public`. Frontend pages (V1.7/V1.8) and the AI Copilot (Phase 2+) next. See [[Build Log]], [[Roadmap]], [[Open Issues]].

## Related

- [[Architecture]]
- [[Roadmap]]
- [[Glossary]]
