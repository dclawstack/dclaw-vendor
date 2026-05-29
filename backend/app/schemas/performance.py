"""Schemas for vendor performance scoring (Phase 5)."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PerformanceKPIs(BaseModel):
    """The 10 KPI subscores (0–100) the LLM assesses, across 4 dimensions."""

    # quality
    defect_rate: float = Field(ge=0, le=100, description="inverse defect rate, higher is better")
    return_rate: float = Field(ge=0, le=100, description="inverse return rate")
    quality_audit: float = Field(ge=0, le=100, description="quality audit results")
    # delivery
    on_time_delivery: float = Field(ge=0, le=100)
    lead_time_adherence: float = Field(ge=0, le=100)
    # cost
    price_competitiveness: float = Field(ge=0, le=100)
    cost_savings: float = Field(ge=0, le=100, description="realised cost savings vs baseline")
    # compliance
    documentation: float = Field(ge=0, le=100, description="documentation completeness")
    certifications: float = Field(ge=0, le=100)
    responsiveness: float = Field(ge=0, le=100)


class ScoredAssessment(BaseModel):
    """LLM output: KPI subscores + a short narrative."""

    kpis: PerformanceKPIs
    summary: str = Field(description="2-3 sentence performance assessment")


class ScoreRequest(BaseModel):
    period: str | None = None  # e.g. "2026-Q2"; defaults to the current quarter


class PerformanceScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    period: str
    quality_score: float
    delivery_score: float
    cost_score: float
    compliance_score: float
    overall_score: float
    kpis: dict[str, Any]
    summary: str | None
    created_at: datetime


class PerformanceScoreList(BaseModel):
    items: list[PerformanceScoreRead]
    total: int


class TrendPoint(BaseModel):
    period: str
    overall_score: float
    created_at: datetime


class BenchmarkResult(BaseModel):
    vendor_id: uuid.UUID
    vendor_overall: float | None
    peer_group: str  # "category:IT Services" or "all vendors"
    peer_count: int
    peer_average: float | None
    percentile: float | None  # vendor's percentile within the peer group (0–100)
