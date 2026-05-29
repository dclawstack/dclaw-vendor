"""Schemas for sustainability scoring (Phase 7, V7.2)."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SustainabilityTarget(BaseModel):
    target: str = Field(description="a concrete ESG improvement target")
    by: str = Field(description="target year or timeframe")


class SustainabilityAssessment(BaseModel):
    """LLM output: ESG subscores (0–100), estimated carbon, targets, summary."""

    environmental_score: float = Field(ge=0, le=100)
    social_score: float = Field(ge=0, le=100)
    governance_score: float = Field(ge=0, le=100)
    carbon_footprint: float = Field(ge=0, description="estimated tonnes CO2e per year")
    targets: list[SustainabilityTarget] = Field(default_factory=list)
    summary: str


class ScoreRequest(BaseModel):
    period: str | None = None


class SustainabilityScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    period: str
    carbon_footprint: float
    environmental_score: float
    social_score: float
    governance_score: float
    overall_score: float
    targets: list[dict[str, Any]] | None
    summary: str | None
    created_at: datetime


class SustainabilityScoreList(BaseModel):
    items: list[SustainabilityScoreRead]
    total: int
