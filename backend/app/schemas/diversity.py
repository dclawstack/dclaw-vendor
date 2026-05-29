"""Schemas for diversity tracking + reporting (Phase 7, V7.1)."""

from pydantic import BaseModel


class DiversityCategorySpend(BaseModel):
    category: str  # diversity category, e.g. "women_owned"
    vendor_count: int
    spend: float


class DiversityReport(BaseModel):
    total_spend: float
    diverse_spend: float
    diverse_spend_pct: float
    vendor_count: int
    diverse_vendor_count: int
    certified_count: int
    by_category: list[DiversityCategorySpend]
