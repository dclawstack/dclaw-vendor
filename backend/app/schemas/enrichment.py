"""Schemas for web data enrichment of vendor profiles (V3.2)."""

import uuid

from pydantic import BaseModel, Field


class EnrichedProfile(BaseModel):
    """Structured facts extracted about a vendor (from web page text or inferred)."""

    company_size: str | None = Field(
        default=None, description="employee headcount band, e.g. '51-200'"
    )
    founded_year: int | None = Field(default=None, description="year the company was founded")
    headquarters: str | None = Field(default=None, description="HQ city/country")
    industry: str | None = Field(default=None, description="primary industry")
    description: str | None = Field(
        default=None, description="one-sentence description of what the vendor does"
    )


class VendorEnrichmentResult(BaseModel):
    vendor_id: uuid.UUID
    vendor_name: str
    # The persisted enrichment blob (profile fields + provenance), or None on failure.
    enrichment: dict | None = None
    error: str | None = None
