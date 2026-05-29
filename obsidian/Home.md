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
| **Progress** | 22/48 tasks — Phases 0–2 ✅ + landing live |
| **Maturity** | 🟢 Tier 2 — Building (core domain + AI Copilot shipped) |
| **Live** | Landing: https://dclaw-vendor.vercel.app |
| **Stack** | Next.js 14 · FastAPI · SQLAlchemy 2.0 · Postgres 16 · Ollama/OpenRouter |
| **GitHub** | [dclawstack/dclaw-vendor](https://github.com/dclawstack/dclaw-vendor) |

---

## Repository ground-truth

```
backend/    FastAPI · SQLAlchemy 2.0 async · Pydantic v2 · ~24 py files · alembic present
frontend/   Next.js 14 App Router · Tailwind · pre-built UI · ~15 tsx files
docs/       getting-started · guides · reference · releases · troubleshooting
helm/       Kubernetes Helm chart
obsidian/   This vault
.github/    CI workflows (incl. Claude Code Action)
```

## Domain entities (PRODUCT-SPEC)

`Vendor` (status, payment terms) · `PurchaseOrder` (status, total, delivery) · `POLineItem` (qty, unit price, received qty)

Inspired by SAP Ariba, Coupa, Ivalua, Jaggaer — AI vendor management reduces risk and optimizes spend.
