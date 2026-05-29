"""Vendor risk assessment (Phase 6, V6.1).

The LLM assesses a vendor against a catalog of 20 risk types and returns the
applicable factors with severities plus an overall band/score. ``diff_factors``
powers continuous-monitoring change alerts by comparing the two most recent
assessments.
"""

from __future__ import annotations

from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.schemas.risk import RiskAnalysis, RiskChange
from app.services.llm import LLMService

# The 20 risk types the analyst considers (P1.1).
RISK_TYPES: list[str] = [
    "financial",
    "operational",
    "compliance",
    "regulatory",
    "reputational",
    "geographic",
    "geopolitical",
    "cybersecurity",
    "data_privacy",
    "supply_chain",
    "concentration",
    "quality",
    "delivery",
    "contractual",
    "legal",
    "esg",
    "sanctions",
    "fraud",
    "business_continuity",
    "single_source",
]

_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}

_SYSTEM = (
    "You are a third-party risk analyst. Assess the vendor against this risk catalog:\n"
    + ", ".join(RISK_TYPES)
    + ".\nReturn ONLY the risk types that materially apply, each with a severity "
    "(low/medium/high) and a one-sentence justification. Then give an overall risk "
    "level and a 0–100 score (higher = riskier). Blacklisted/inactive vendors, long "
    "payment terms, order cancellations and single-source dependence raise risk."
)


def _context(vendor: Vendor, pos: list[PurchaseOrder]) -> str:
    cancelled = sum(1 for p in pos if p.status.value == "cancelled")
    return (
        f"Vendor: {vendor.name}\n"
        f"Status: {vendor.status.value}\n"
        f"Tier: {vendor.tier.value if vendor.tier else 'unclassified'}\n"
        f"Category: {vendor.category or 'unknown'}\n"
        f"Payment terms: {vendor.payment_terms or 'unspecified'}\n"
        f"Purchase orders: {len(pos)} ({cancelled} cancelled)"
    )


async def assess_vendor(
    llm: LLMService, vendor: Vendor, pos: list[PurchaseOrder]
) -> RiskAnalysis:
    return await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Assess risk for:\n\n{_context(vendor, pos)}"},
        ],
        RiskAnalysis,
    )


def diff_factors(
    previous: list[dict] | None, current: list[dict]
) -> list[RiskChange]:
    """Compare two factor lists (each {type, severity, ...}) → change alerts."""
    prev = {f["type"]: f.get("severity", "low") for f in (previous or [])}
    cur = {f["type"]: f.get("severity", "low") for f in current}
    changes: list[RiskChange] = []
    for t, sev in cur.items():
        if t not in prev:
            changes.append(RiskChange(type=t, change="new", to_severity=sev))
        elif _SEVERITY_RANK[sev] > _SEVERITY_RANK[prev[t]]:
            changes.append(
                RiskChange(type=t, change="increased", from_severity=prev[t], to_severity=sev)
            )
        elif _SEVERITY_RANK[sev] < _SEVERITY_RANK[prev[t]]:
            changes.append(
                RiskChange(type=t, change="decreased", from_severity=prev[t], to_severity=sev)
            )
    for t, sev in prev.items():
        if t not in cur:
            changes.append(RiskChange(type=t, change="resolved", from_severity=sev))
    return changes
