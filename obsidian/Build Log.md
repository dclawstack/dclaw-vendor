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

## Related
- [[Home]] · [[Dev Plan]] · [[Roadmap]] · [[Open Issues]]
