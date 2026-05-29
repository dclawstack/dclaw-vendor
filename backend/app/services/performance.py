"""Vendor performance scoring (Phase 5, V5.2).

The LLM assesses the 10 KPI subscores (0–100) from a vendor's profile + PO
history; the four dimension scores and the overall composite are then computed
deterministically in Python (equal weights) so the rollup is reproducible and
not at the mercy of the model's arithmetic. Trend and peer benchmarking are
plain DB aggregates and live in the repository.
"""

from __future__ import annotations

from app.models.performance import PerformanceScore
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.schemas.performance import ScoredAssessment
from app.services.llm import LLMService

_SYSTEM = (
    "You are a vendor performance analyst. From the vendor profile and purchase-order "
    "history, score 10 KPIs from 0–100 (higher is better) across quality, delivery, "
    "cost, and compliance. Be realistic: a healthy received-order history and short "
    "payment terms lift delivery/cost; cancellations and long terms lower them; "
    "blacklisted/inactive status drags compliance. Provide a brief summary."
)

_QUALITY = ("defect_rate", "return_rate", "quality_audit")
_DELIVERY = ("on_time_delivery", "lead_time_adherence")
_COST = ("price_competitiveness", "cost_savings")
_COMPLIANCE = ("documentation", "certifications", "responsiveness")


def current_quarter(year: int, month: int) -> str:
    return f"{year}-Q{(month - 1) // 3 + 1}"


def _avg(kpis: dict[str, float], keys: tuple[str, ...]) -> float:
    return round(sum(kpis[k] for k in keys) / len(keys), 1)


def compute_dimensions(kpis: dict[str, float]) -> dict[str, float]:
    quality = _avg(kpis, _QUALITY)
    delivery = _avg(kpis, _DELIVERY)
    cost = _avg(kpis, _COST)
    compliance = _avg(kpis, _COMPLIANCE)
    overall = round((quality + delivery + cost + compliance) / 4, 1)
    return {
        "quality_score": quality,
        "delivery_score": delivery,
        "cost_score": cost,
        "compliance_score": compliance,
        "overall_score": overall,
    }


def _context(vendor: Vendor, pos: list[PurchaseOrder]) -> str:
    by_status: dict[str, int] = {}
    total = 0.0
    for po in pos:
        by_status[po.status.value] = by_status.get(po.status.value, 0) + 1
        total += po.total or 0.0
    status_line = ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())) or "none"
    return (
        f"Vendor: {vendor.name}\n"
        f"Status: {vendor.status.value}\n"
        f"Tier: {vendor.tier.value if vendor.tier else 'unclassified'}\n"
        f"Payment terms: {vendor.payment_terms or 'unspecified'}\n"
        f"Purchase orders: {len(pos)} (by status: {status_line})\n"
        f"Total PO value: ${total:,.2f}"
    )


async def score_vendor(
    llm: LLMService, vendor: Vendor, pos: list[PurchaseOrder], period: str
) -> PerformanceScore:
    assessment: ScoredAssessment = await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Score this vendor:\n\n{_context(vendor, pos)}"},
        ],
        ScoredAssessment,
    )
    kpis = assessment.kpis.model_dump()
    dims = compute_dimensions(kpis)
    return PerformanceScore(
        vendor_id=vendor.id,
        period=period,
        kpis=kpis,
        summary=assessment.summary,
        **dims,
    )
