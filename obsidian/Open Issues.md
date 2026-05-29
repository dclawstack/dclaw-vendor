# Open Issues

> Snapshot at 2026-05-29 from `REVISED-PRD.md` gap analysis + cross-doc review. Re-run `gh issue list` for the authoritative live state.

## Gaps (from REVISED-PRD v2.3)

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | Missing `dclaw-manifest.json` | 🔴 | Create `frontend/public/dclaw-manifest.json` for DPanel |
| 2 | Partial implementation | 🟡 | Expand backend services + frontend pages per P0 roadmap |

## Doc inconsistencies (worth resolving)

- **README is the un-customized scaffold.** `README.md` still reads "DClaw Scaffold" rather than describing DClaw Vendor. Only the Contributors section has been added so far.
- **Ports TBD / conflicting.** PRD says 3032 / 18102; the shared registry says 3019 / 8106. Assign one canonically.
- **PRODUCT-SPEC vs PRD scope.** PRODUCT-SPEC covers a focused vendor + purchase-order model, while the PRD frames a broader evaluation/onboarding/performance platform. The richer PRD features (risk scoring, spend analytics) have no domain model yet.

## Related

- [[Architecture]]
- [[Roadmap]]
