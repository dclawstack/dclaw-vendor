# DClaw Vendor — Vault Home

> Project wiki for **DClaw Vendor**. Synthesised from the repo docs (`AGENTS.md`, `PLAN-v1.2.md`, `REVISED-PRD.md`, `PRODUCT-SPEC.md`) on 2026-05-29.
> Ground truth is always `git log` / the source tree; this vault is the human-readable map.

---

## Quick links

- [[Project Overview]] — what DClaw Vendor is and who it's for
- [[Architecture]] — stack, ports, directory layout, anti-patterns
- [[Roadmap]] — P0 → P1 → P2 feature plan
- [[Dev Plan]] — phase-wise build plan (mirrored to Neon + GitHub Project)
- [[Build Log]] — chronological record of completed tasks (PRs / issues / outcomes)
- [[Open Issues]] — known gaps
- [[Glossary]] — terms and acronyms

---

## At a glance

| | |
|---|---|
| **App ID** | `vendor` |
| **Tagline** | Vendor evaluation |
| **Category** | Procurement |
| **Brand color** | `#6366F1` |
| **Progress** | **48/48 tasks ✅ — all 9 phases shipped (v1.0 GA, 2026-05-30)** |
| **Maturity** | 🟢 Tier 3 — Complete (full platform; 117 backend tests green) |
| **Live** | Landing: https://dclaw-vendor.vercel.app · App runs locally on :3060/:8146 |
| **Stack** | Next.js 14 · FastAPI · SQLAlchemy 2.0 · Postgres 16 · Ollama/OpenRouter |
| **GitHub** | [dclawstack/dclaw-vendor](https://github.com/dclawstack/dclaw-vendor) |

---

## Repository ground-truth

```
backend/    FastAPI · SQLAlchemy 2.0 async · Pydantic v2 · 16 routers · 8 migrations · 117 tests
frontend/   Next.js 14 App Router · Tailwind · dk/ primitives · 9 pages + feature panels
docs/       getting-started · guides · reference · releases · troubleshooting · demo
helm/       Helm chart — CloudNativePG + TLS ingress + Prometheus annotations
monitoring/ Prometheus notes + Grafana dashboard
landing/    Standalone Next.js marketing site (live on Vercel)
obsidian/   This vault
.github/    CI workflows (incl. Claude Code Action)
```

## Domain entities

**Core:** `Vendor` · `PurchaseOrder` · `POLineItem`
**AI/feature models:** `OnboardingCase` / `OnboardingDocument` / `ApprovalStep` · `PerformanceScore` · `RiskAssessment` · `Contract` · `SustainabilityScore` · `Survey` / `SurveyResponse` · `Audit` / `AuditFinding` · `AppSetting`

Vendors carry directory (category/industry/tier/website/enrichment) and diversity attributes; POs carry an ERP `external_ref`.

Inspired by SAP Ariba, Coupa, Ivalua, Jaggaer — AI vendor management reduces risk and optimizes spend.
