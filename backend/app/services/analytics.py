"""Spend analytics (Phase 6, V6.3).

Deterministic spend aggregation over purchase orders (cancelled excluded), plus
an AI insights pass that targets ~10% savings and proposes vendor consolidation.
The dataset is small and fully structured, so aggregation happens in Python.
"""

from __future__ import annotations

from collections import defaultdict

from app.models.enums import POStatus
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.schemas.analytics import SpendBucket, SpendInsights, SpendInsightsAI, SpendSummary
from app.services.llm import LLMService

SAVINGS_TARGET_RATE = 0.10

_SYSTEM = (
    "You are a procurement spend analyst. From the spend breakdown, identify concrete "
    "savings opportunities (consolidation, renegotiation, demand management, maverick-spend "
    "reduction) and vendor-consolidation plays where several vendors serve one category. "
    "Aim for roughly a 10% reduction of total spend overall. Give realistic per-opportunity "
    "estimates in USD."
)


def _buckets(d: dict[str, tuple[float, int]], *, top: int | None = None) -> list[SpendBucket]:
    items = [SpendBucket(key=k, spend=round(v[0], 2), count=v[1]) for k, v in d.items()]
    items.sort(key=lambda b: b.spend, reverse=True)
    return items[:top] if top else items


def build_summary(vendors: list[Vendor], pos: list[PurchaseOrder]) -> SpendSummary:
    vname = {v.id: v.name for v in vendors}
    vcat = {v.id: (v.category or "Uncategorized") for v in vendors}

    by_status: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_category: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_vendor: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_month: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    total = 0.0
    counted = 0

    for po in pos:
        amount = po.total or 0.0
        # status breakdown includes everything; spend totals exclude cancelled
        s = by_status[po.status.value]
        by_status[po.status.value] = (s[0] + amount, s[1] + 1)
        if po.status == POStatus.cancelled:
            continue
        total += amount
        counted += 1
        cat = vcat.get(po.vendor_id, "Uncategorized") if po.vendor_id else "Uncategorized"
        c = by_category[cat]
        by_category[cat] = (c[0] + amount, c[1] + 1)
        vn = vname.get(po.vendor_id, "—") if po.vendor_id else "—"
        v = by_vendor[vn]
        by_vendor[vn] = (v[0] + amount, v[1] + 1)
        month = po.created_at.strftime("%Y-%m")
        m = by_month[month]
        by_month[month] = (m[0] + amount, m[1] + 1)

    summary = SpendSummary(
        total_spend=round(total, 2),
        po_count=counted,
        by_status=_buckets(by_status),
        by_category=_buckets(by_category),
        by_vendor=_buckets(by_vendor, top=10),
        by_month=sorted(_buckets(by_month), key=lambda b: b.key),
    )
    return summary


def _insights_context(summary: SpendSummary) -> str:
    cats = "; ".join(f"{b.key}=${b.spend:,.0f} ({b.count} POs)" for b in summary.by_category)
    vendors = "; ".join(f"{b.key}=${b.spend:,.0f}" for b in summary.by_vendor)
    return (
        f"Total spend: ${summary.total_spend:,.2f} across {summary.po_count} POs.\n"
        f"By category: {cats or 'none'}\n"
        f"Top vendors: {vendors or 'none'}"
    )


async def generate_insights(
    llm: LLMService, summary: SpendSummary
) -> SpendInsights:
    ai: SpendInsightsAI = await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Spend breakdown:\n\n{_insights_context(summary)}"},
        ],
        SpendInsightsAI,
    )
    return SpendInsights(
        total_spend=summary.total_spend,
        target_savings=round(summary.total_spend * SAVINGS_TARGET_RATE, 2),
        opportunities=ai.opportunities,
        consolidation=ai.consolidation,
        summary=ai.summary,
    )
