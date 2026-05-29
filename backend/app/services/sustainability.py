"""Sustainability scoring (Phase 7, V7.2).

The LLM estimates ESG subscores + an annual carbon footprint and proposes
reduction targets; the overall composite is the mean of the three ESG scores,
computed in Python.
"""

from __future__ import annotations

from app.models.purchase_order import PurchaseOrder
from app.models.sustainability import SustainabilityScore
from app.models.vendor import Vendor
from app.schemas.sustainability import SustainabilityAssessment
from app.services.llm import LLMService

_SYSTEM = (
    "You are an ESG / sustainability analyst. From the vendor profile, estimate "
    "environmental, social, and governance scores (0–100, higher is better), an "
    "approximate annual carbon footprint in tonnes CO2e, and 2–3 concrete reduction "
    "targets. Heavy-industry/logistics categories imply higher footprints; software/"
    "services lower. Be realistic and concise."
)


def _context(vendor: Vendor, pos: list[PurchaseOrder]) -> str:
    spend = sum(p.total or 0.0 for p in pos)
    return (
        f"Vendor: {vendor.name}\n"
        f"Category: {vendor.category or 'unknown'}\n"
        f"Industry: {vendor.industry or 'unknown'}\n"
        f"Annual purchase volume: ${spend:,.2f} across {len(pos)} POs"
    )


async def score_vendor(
    llm: LLMService, vendor: Vendor, pos: list[PurchaseOrder], period: str
) -> SustainabilityScore:
    a: SustainabilityAssessment = await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Assess sustainability for:\n\n{_context(vendor, pos)}"},
        ],
        SustainabilityAssessment,
    )
    overall = round((a.environmental_score + a.social_score + a.governance_score) / 3, 1)
    return SustainabilityScore(
        vendor_id=vendor.id,
        period=period,
        carbon_footprint=a.carbon_footprint,
        environmental_score=a.environmental_score,
        social_score=a.social_score,
        governance_score=a.governance_score,
        overall_score=overall,
        targets=[t.model_dump() for t in a.targets],
        summary=a.summary,
    )
