# Build Log

> Chronological record of completed [[Dev Plan]] tasks. One entry per task: ID · title · PR · issue · outcome · date.
> Live status of record is the GitHub Project (#4) + Neon `tracking` schema; this is the human-readable mirror.

## Phase 0 — Foundation & Infra Hardening

### 2026-05-29

- **V0.1 — Resolve config & ports** · PR #50 · issue #1 — Fixed backend/frontend Dockerfile ports to 8106/3019 (were 8095/3006, contradicting compose); corrected AGENTS.md App Identity; resolved Architecture.md "Ports TBD"; removed 3 broken scaffold orphans (`app/config.py`, `app/models.py`, `app/dependencies.py`).
- **V0.2 — DPanel manifest** · PR #50 · issue #2 — Added `frontend/public/dclaw-manifest.json` (app_id `vendor`, category Procurement, color `#6366F1`, ports/routes/nav); superset of the DPanel loader interface + ecosystem template.
- **V0.3 — Customize README** · PR #50 · issue #3 — Rewrote README for DClaw Vendor scope/features/run/test; kept Contributors.
- **V0.4 — DB & migrations baseline** · PR #50 · issue #4 — Verified `Base`/alembic async wiring; added config-driven `db_schema` (empty=public for local/CI; `DB_SCHEMA=vendor` on Neon pins asyncpg search_path + alembic schema/version table). Created `vendor` schema on Neon.
- **V0.5 — Boot & CI smoke** · PR #50 · issue #5 — `/health` green (pytest), `docker-compose config` valid, compose↔Dockerfile port invariants hold, CI intact, anti-pattern checklist clean.
- **V0.6 — Adopt DKube design system** · PR #52 · issue #46 — Copied verbatim from `dclaw-marketing@main`: `frontend/src/styles/brand.css` (`--dk-*` purple tokens), `tailwind.config.ts` (token wiring), brand-wired `globals.css` (light-mode only, no `.dark`), Poppins via `next/font/google` + brand body in `layout.tsx`, `public/brand/` logos + favicons, and a lean `design/` brand book (BRAND_GUIDELINES, colors_and_type.css, preview/, fonts/, brand SVG assets — heavy customer imagery/decks skipped).
- **V0.7 — Port `dk/` primitive component library** · PR #52 · issue #47 — Copied 26 `Dk*` primitives + README + `index.ts` barrel. `next build` type-checks clean. Two app-coupled composites deferred to the phases that provide their deps: `DkOrgSwitcher` → V8.1 (auth/org contexts), `DkAgentChat` → V2.5 (Copilot API). `dk/` is the UI library for all later frontend work; scaffold `ui/` left unused.

## Related
- [[Home]] · [[Dev Plan]] · [[Roadmap]] · [[Open Issues]]
