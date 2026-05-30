# Open Issues

> Updated 2026-05-30 — **plan complete (48/48).** `gh issue list` shows **0 open** · GitHub Project #4 all Done · Neon `tracking` all done. No blocking issues remain.

## Original gaps — ✅ all resolved

| # | Gap | Resolution |
|---|-----|------------|
| 1 | Missing `dclaw-manifest.json` | ✅ Created in V0.2 (`frontend/public/dclaw-manifest.json`). |
| 2 | Partial implementation | ✅ All 9 phases shipped — full platform, 16 routers, 9 pages, 117 backend tests. |
| 3 | README was the un-customized scaffold | ✅ Rewritten for DClaw Vendor in V0.3; docs filled in V8.5. |
| 4 | Ports TBD / conflicting | ✅ Resolved in V0.1 → canonical 8146 / 3060 / `dclaw_vendor`. |
| 5 | PRODUCT-SPEC vs PRD scope (no model for richer features) | ✅ Resolved — risk, contracts, performance, sustainability, surveys, audits, onboarding models all shipped (Phases 3–7). |

## Known follow-ups (tracked, not blocking — future polish)

- **Live integration credentials** — Logto auth, Stripe billing, ERP sync, and MinIO storage are code-complete in **test-mode** (mock/feature-flagged). They go live by setting the relevant env flag + credentials; no code change needed.
- **Copilot streaming** — chat is non-streaming (typing indicator + action chips); token streaming is deferred polish.
- **OpenRouter cloud fallback** — wired and config-ready; unused until a key is added on Settings (Ollama is the active dev provider).
- **Landing CTA target** — points at the running app via `NEXT_PUBLIC_APP_URL` (localhost dev); repoint when the app frontend is publicly hosted.
- **Local Docker DB resets** — the standalone backend uses `create_all` on boot, so a `down -v` rebuild starts with an empty DB; the Neon runtime DB is unaffected.

## Related

- [[Architecture]]
- [[Roadmap]]
- [[Build Log]]
