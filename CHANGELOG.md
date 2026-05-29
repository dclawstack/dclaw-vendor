# Changelog

All notable changes to DClaw Vendor. See `docs/releases/changelog.md` for the
phase-by-phase detail.

## [1.0.0] — General Availability

AI-native vendor & purchase-order management, complete across nine phases (V0–V8).

### Added
- **Core** — vendors, purchase orders, line items (CRUD, search, pagination).
- **AI Copilot** — context-grounded chat, vendor evaluation (single + batch).
- **Directory** — AI classification (category/industry/tier), web/AI enrichment, facets.
- **Onboarding** — cases, document storage (MinIO/local), AI checklist + validation, multi-step approvals.
- **Performance** — 10-KPI scorecards, AI scoring, trends, peer benchmarks.
- **Risk** — 20-type assessment, AI scoring, change-alert monitoring.
- **Contracts** — AI key-term extraction, renewal tracking.
- **Analytics** — spend aggregation, AI ~10% savings + consolidation.
- **Integration** — ERP sync, PO matching, invoice reconciliation.
- **Diversity** — diverse-spend tracking + reporting.
- **Sustainability** — ESG scoring with carbon footprint + targets.
- **Surveys** — stakeholder feedback with AI sentiment + trend.
- **Audits** — finding tracking + closure validation.
- **Platform** — Logto auth, Stripe billing, Prometheus + structlog monitoring, Helm (CloudNativePG, TLS ingress), docs, landing site.

### Notes
- External integrations (Logto, Stripe, ERP, MinIO) are code-complete in test-mode:
  feature-flagged with mock backends, live on real credentials.

## [0.1.0]
- Initial scaffold (Next.js + FastAPI), Helm chart, docs structure.
