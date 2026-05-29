import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import VendorStatus, VendorTier


class VendorBase(BaseModel):
    name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    payment_terms: str | None = None
    status: VendorStatus = VendorStatus.active
    category: str | None = None
    industry: str | None = None
    tier: VendorTier | None = None
    website: str | None = None
    diverse_owned: bool = False
    diversity_categories: list[str] | None = None
    diversity_certified: bool = False
    certification_body: str | None = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    payment_terms: str | None = None
    status: VendorStatus | None = None
    category: str | None = None
    industry: str | None = None
    tier: VendorTier | None = None
    website: str | None = None
    diverse_owned: bool | None = None
    diversity_categories: list[str] | None = None
    diversity_certified: bool | None = None
    certification_body: str | None = None


class VendorRead(VendorBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    enrichment: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class VendorList(BaseModel):
    items: list[VendorRead]
    total: int


class FacetCount(BaseModel):
    value: str
    count: int


class VendorFacets(BaseModel):
    """Aggregate counts powering the directory's filter facets (V3.3/V3.4)."""

    status: list[FacetCount]
    category: list[FacetCount]
    tier: list[FacetCount]
    industry: list[FacetCount]
    total: int
