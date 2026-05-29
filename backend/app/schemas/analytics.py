"""Schemas for spend analytics (Phase 6, V6.3)."""

from pydantic import BaseModel, Field


class SpendBucket(BaseModel):
    key: str
    spend: float
    count: int


class SpendSummary(BaseModel):
    total_spend: float
    po_count: int
    by_status: list[SpendBucket]
    by_category: list[SpendBucket]
    by_vendor: list[SpendBucket]  # top vendors by spend
    by_month: list[SpendBucket]  # chronological


class SavingsOpportunity(BaseModel):
    title: str = Field(description="short opportunity name")
    category: str | None = Field(default=None, description="affected spend category, if any")
    rationale: str = Field(description="why this saves money")
    estimated_savings: float = Field(description="estimated annual savings in USD")


class ConsolidationSuggestion(BaseModel):
    category: str
    vendors: list[str] = Field(description="vendor names that could be consolidated")
    rationale: str


class SpendInsightsAI(BaseModel):
    """The LLM-produced part of the insights (totals are computed, not generated)."""

    opportunities: list[SavingsOpportunity]
    consolidation: list[ConsolidationSuggestion]
    summary: str


class SpendInsights(SpendInsightsAI):
    """AI output plus computed totals: ~10% savings target."""

    total_spend: float
    target_savings: float  # ~10% of total spend
