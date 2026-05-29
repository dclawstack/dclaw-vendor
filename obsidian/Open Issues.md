# Open Issues

> Updated 2026-05-29 after Phase 2. Live status of record: `gh issue list` (26 open = the 26 not-yet-started tasks) + GitHub Project #4 + Neon `tracking`.

## Original gaps — ✅ all resolved

| # | Gap | Resolution |
|---|-----|------------|
| 1 | Missing `dclaw-manifest.json` | ✅ Created in V0.2 (`frontend/public/dclaw-manifest.json`). |
| 2 | Partial implementation | ✅ Core domain (Phase 1) + AI Copilot (Phase 2) shipped; backend services + all 5 frontend screens in place. |
| 3 | README was the un-customized scaffold | ✅ Rewritten for DClaw Vendor in V0.3. |
| 4 | Ports TBD / conflicting | ✅ Resolved in V0.1 → canonical 8106 / 3019 / `dclaw_vendor`. |
| 5 | PRODUCT-SPEC vs PRD scope (no model for richer features) | 🟡 Partially open — domain models for risk scoring, contracts, spend, etc. arrive with Phases 3–8. |

## Known follow-ups (tracked, not blocking)

- **Copilot streaming** — V2.5 ships non-streaming chat (typing indicator + action chips); token streaming is deferred polish.
- **OpenRouter cloud fallback** — wired and config-ready, but unused until a key is added on the Settings page (Ollama is the active dev provider).
- **Deferred `dk/` composites** — `DkOrgSwitcher` (→ V8.1 auth) and `DkAgentChat` (a vendor-specific Copilot widget was built instead).
- **Landing CTA target** — points at the running app via `NEXT_PUBLIC_APP_URL` (localhost dev); repoint when the app frontend is publicly hosted.

## Related

- [[Architecture]]
- [[Roadmap]]
- [[Build Log]]
