"""Schemas for AI vendor classification (V3.1)."""

import uuid

from pydantic import BaseModel, Field

from app.models.enums import VendorTier


class VendorClassification(BaseModel):
    """LLM-produced classification of a vendor into the directory taxonomy."""

    category: str = Field(
        description="procurement spend category, e.g. 'Raw Materials', 'IT Services', 'Logistics'"
    )
    industry: str = Field(description="the vendor's primary industry")
    tier: VendorTier = Field(
        description="strategic importance: strategic > preferred > approved > transactional"
    )
    rationale: str = Field(description="one sentence explaining the classification")


class VendorClassificationResult(BaseModel):
    vendor_id: uuid.UUID
    vendor_name: str
    classification: VendorClassification | None = None
    error: str | None = None


class BatchClassificationResponse(BaseModel):
    results: list[VendorClassificationResult]
    classified: int
    failed: int
