"""Schemas for vendor risk assessment (Phase 6, V6.1)."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RiskLevel


class RiskFactor(BaseModel):
    type: str = Field(description="risk type slug from the catalog, e.g. 'financial'")
    severity: Literal["low", "medium", "high"]
    note: str = Field(description="one concise sentence on why this risk applies")


class RiskAnalysis(BaseModel):
    """LLM output: identified risk factors + overall band/score + summary."""

    overall_level: RiskLevel
    overall_score: float = Field(ge=0, le=100, description="0=safe, 100=highest risk")
    factors: list[RiskFactor] = Field(default_factory=list)
    summary: str = Field(description="2-3 sentence risk summary")


class RiskAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    overall_level: RiskLevel
    overall_score: float
    factors: list[dict[str, Any]]
    summary: str | None
    created_at: datetime


class RiskAssessmentList(BaseModel):
    items: list[RiskAssessmentRead]
    total: int


class RiskChange(BaseModel):
    type: str
    change: Literal["new", "increased", "decreased", "resolved"]
    from_severity: str | None = None
    to_severity: str | None = None


class RiskMonitorResult(BaseModel):
    """A fresh assessment plus what changed vs the previous one (V6.1 monitoring)."""

    assessment: RiskAssessmentRead
    changes: list[RiskChange]
