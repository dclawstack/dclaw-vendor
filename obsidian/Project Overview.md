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

Tier 2 (Partial). P0 partially implemented; P1/P2 not started. See [[Roadmap]] and [[Open Issues]].

## Related

- [[Architecture]]
- [[Roadmap]]
- [[Glossary]]
