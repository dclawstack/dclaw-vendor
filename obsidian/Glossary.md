# Glossary

| Term | Meaning |
|------|---------|
| **AI Vendor Copilot** | Mandated P0.1: evaluates, onboards, and manages vendors with LLM risk + performance insights. |
| **Vendor** | A supplier record: contact, payment terms, status (active/inactive/blacklisted). |
| **Purchase Order (PO)** | An order placed with a vendor; tracked from draft → sent → partial → received. |
| **PO Line Item** | A single line on a PO: product, quantity, unit price, received quantity. |
| **Payment terms** | When payment is due (e.g. Net 30, Net 60). |
| **Performance tracking** | Scoring vendors 0–100 across quality, delivery, cost, compliance KPIs. |
| **Spend analytics** | P1 feature: analyzing vendor spend to find savings/consolidation opportunities. |
| **DPanel** | The DClaw admin panel; apps register via `frontend/public/dclaw-manifest.json`. |
| **Repository pattern** | DClaw rule: all DB access through `app/repositories/`. |
| **Sacred stack** | The non-negotiable DClaw tech stack (Next.js 14 / FastAPI / SQLAlchemy 2.0 / Postgres 16). |
| **Maturity Tier** | DClaw readiness rating; Vendor is 🟡 Tier 2 (Partial). |

## Related

- [[Architecture]]
- [[Project Overview]]
