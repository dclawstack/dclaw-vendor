"""Diversity spend tracking + reporting (Phase 7, V7.1).

Aggregates spend (cancelled POs excluded) toward diverse-owned vendors and breaks
it down by diversity category. Pure computation over the loaded vendors + POs.
"""

from __future__ import annotations

from collections import defaultdict

from app.models.enums import POStatus
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.schemas.diversity import DiversityCategorySpend, DiversityReport


def build_report(vendors: list[Vendor], pos: list[PurchaseOrder]) -> DiversityReport:
    spend_by_vendor: dict = defaultdict(float)
    for po in pos:
        if po.status == POStatus.cancelled or po.vendor_id is None:
            continue
        spend_by_vendor[po.vendor_id] += po.total or 0.0

    total_spend = sum(spend_by_vendor.values())
    diverse_spend = 0.0
    diverse_count = 0
    certified_count = 0
    cat_vendors: dict[str, int] = defaultdict(int)
    cat_spend: dict[str, float] = defaultdict(float)

    for v in vendors:
        if not v.diverse_owned:
            continue
        diverse_count += 1
        if v.diversity_certified:
            certified_count += 1
        vspend = spend_by_vendor.get(v.id, 0.0)
        diverse_spend += vspend
        for cat in v.diversity_categories or []:
            cat_vendors[cat] += 1
            cat_spend[cat] += vspend

    by_category = [
        DiversityCategorySpend(category=c, vendor_count=cat_vendors[c], spend=round(cat_spend[c], 2))
        for c in sorted(cat_vendors, key=lambda c: cat_spend[c], reverse=True)
    ]
    pct = round(100 * diverse_spend / total_spend, 1) if total_spend else 0.0
    return DiversityReport(
        total_spend=round(total_spend, 2),
        diverse_spend=round(diverse_spend, 2),
        diverse_spend_pct=pct,
        vendor_count=len(vendors),
        diverse_vendor_count=diverse_count,
        certified_count=certified_count,
        by_category=by_category,
    )
