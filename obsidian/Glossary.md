# Glossary

| Term | Meaning |
|------|---------|
| **AI Vendor Copilot** | Mandated P0.1: evaluates, onboards, and manages vendors with LLM risk + performance insights. |
| **Vendor** | A supplier record: contact, payment terms, status (active/inactive/blacklisted). |
| **Purchase Order (PO)** | An order placed with a vendor; tracked from draft → sent → partial → received. |
| **PO Line Item** | A single line on a PO: product, quantity, unit price, received quantity. |
| **Payment terms** | When payment is due (e.g. Net 30, Net 60). |
| **Performance tracking** | Scoring vendors 0–100 across quality, delivery, cost, compliance KPIs. |
| **Spend analytics** | P1.3: aggregating vendor spend, with AI surfacing ~10% savings + consolidation plays. |
| **Vendor tier** | Strategic importance from AI classification: strategic > preferred > approved > transactional. |
| **Enrichment** | AI/web-derived vendor profile (size, HQ, founded, industry) stored with provenance (`source`, `fetched_url`). |
| **Onboarding case** | A vendor's progression through document collection → AI validation → multi-step approval → activation. |
| **Approval chain** | Ordered `ApprovalStep`s; decided in order; all-approved → case approved; any reject → rejected. |
| **Performance score** | 10 KPIs across quality/delivery/cost/compliance → 4 dimensions → an overall 0–100 composite, benchmarked vs peers. |
| **Risk assessment** | AI scoring across a 20-type risk catalog; re-running yields change alerts (new/escalated/resolved). |
| **Contract terms** | AI-extracted key terms (payment, SLA, renewal, termination, liability) from contract text. |
| **ERP reconciliation** | Matching external invoices to local POs by `external_ref` → matched / over- / under-billed / unmatched. |
| **ESG score** | Sustainability scoring: environmental/social/governance subscores + estimated carbon footprint + targets. |
| **Diverse spend** | Share of spend directed to diverse-owned vendors, tracked by diversity category. |
| **Sentiment** | AI classification of a survey response comment as positive/neutral/negative (−1…1 score). |
| **Audit closure validation** | An audit can only be closed once every finding is closed. |
| **Test-mode integration** | An external integration (Logto/Stripe/ERP/MinIO) shipped feature-flagged with a mock backend; goes live on real credentials. |
| **DPanel** | The DClaw admin panel; apps register via `frontend/public/dclaw-manifest.json`. |
| **Repository pattern** | DClaw rule: all DB access through `app/repositories/`. |
| **Sacred stack** | The non-negotiable DClaw tech stack (Next.js 14 / FastAPI / SQLAlchemy 2.0 / Postgres 16). |
| **Maturity Tier** | DClaw readiness rating; Vendor is 🟢 Tier 3 (Complete) — v1.0 GA, all 48 tasks shipped. |

## Related

- [[Architecture]]
- [[Project Overview]]
