"""Schemas for stakeholder surveys + feedback (Phase 7, V7.3)."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SentimentResult(BaseModel):
    """LLM output for a single comment."""

    sentiment: Literal["positive", "neutral", "negative"]
    score: float = Field(ge=-1.0, le=1.0, description="-1 very negative … 1 very positive")


class SurveyResponseCreate(BaseModel):
    respondent: str | None = None
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class SurveyResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    survey_id: uuid.UUID
    respondent: str | None
    rating: int
    comment: str | None
    sentiment: str | None
    sentiment_score: float | None
    created_at: datetime


class SurveyCreate(BaseModel):
    vendor_id: uuid.UUID
    title: str


class SurveyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    title: str
    created_at: datetime
    responses: list[SurveyResponseRead] = []


class SurveyList(BaseModel):
    items: list[SurveyRead]
    total: int


class VendorSentiment(BaseModel):
    """Aggregate feedback for a vendor (V7.3 sentiment + trend)."""

    vendor_id: uuid.UUID
    response_count: int
    average_rating: float | None
    average_sentiment: float | None
    positive: int
    neutral: int
    negative: int
    trend: list["SentimentTrendPoint"]


class SentimentTrendPoint(BaseModel):
    period: str  # YYYY-MM
    average_rating: float
    average_sentiment: float | None
    count: int
