# Demo Script (~5 minutes)

A guided walkthrough that exercises every major capability. Assumes the stack is
running (`docker compose -f docker-compose.standalone.yml up --build`) with an LLM
provider configured on **Settings**.

## 0. Setup (15s)
Open <http://localhost:3060>. On **Settings**, confirm the LLM provider is reachable
("Test connection"). Note the **Billing** card showing the current plan.

## 1. Vendors & the Copilot (60s)
1. **Vendors → Add Vendor** — create "Acme Industrial" (category *Raw Materials*, website `acme.example.com`).
2. Open the vendor → **Evaluate (AI)** — show risk level + recommendation.
3. Open the floating **Copilot** → ask *"How many vendors do I have and what's my total spend?"*.

## 2. Directory intelligence (45s)
1. On the vendor, click **Classify** then **Enrich** — watch tier/category and the enriched profile fill in.
2. Back on **Vendors**, use the category facet chips and the **AI Classify** bulk button.

## 3. Onboarding (45s)
1. **Onboarding → New Onboarding** for Acme.
2. **Generate checklist** → **Upload** a document → **Validate** it.
3. **Submit for approval** → approve both steps → **Activate vendor**.

## 4. Performance, risk & contracts (60s)
On the vendor detail page:
1. **Performance → Score (AI)** — show dimension bars, benchmark, trend.
2. **Risk → Assess (AI)** — show factors; assess again to show change alerts.
3. **Contracts → Add contract**, then **Extract** terms from pasted text.

## 5. Analytics & integration (45s)
**Analytics** page: review spend-by-category, **Find savings**, the diversity report,
then **Sync ERP** and read the invoice **reconciliation** table.

## 6. ESG, feedback, audits (45s)
1. Vendor detail → **Sustainability → Score (AI)** and set **Diversity** attributes.
2. **Feedback** → new survey → add a response → see AI sentiment + the vendor summary.
3. **Audits** → schedule an audit → add a finding → close the finding → **Close audit**.

## 7. Ops (15s)
Hit `GET /metrics` to show Prometheus output; mention the Helm chart (CloudNativePG +
TLS ingress) and that Auth/Billing/ERP go live by dropping in real credentials.
