"""Schemas for vendor contract management (Phase 6, V6.2)."""

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ContractStatus


class ContractBase(BaseModel):
    title: str
    start_date: date | None = None
    end_date: date | None = None
    value: float | None = None
    auto_renew: bool = False
    notes: str | None = None


class ContractCreate(ContractBase):
    vendor_id: uuid.UUID


class ContractUpdate(BaseModel):
    title: str | None = None
    status: ContractStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    value: float | None = None
    auto_renew: bool | None = None
    notes: str | None = None


class ContractRead(ContractBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    status: ContractStatus
    key_terms: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class ContractList(BaseModel):
    items: list[ContractRead]
    total: int


# --- AI term extraction (V6.2) ------------------------------------------


class ExtractRequest(BaseModel):
    text: str = Field(description="raw contract text to extract terms from")


class ExtractedTerms(BaseModel):
    payment_terms: str | None = None
    sla: str | None = None
    termination_clause: str | None = None
    renewal_terms: str | None = None
    liability: str | None = None
    pricing: str | None = None


class RenewalItem(BaseModel):
    contract_id: uuid.UUID
    vendor_id: uuid.UUID
    title: str
    end_date: date | None
    days_to_expiry: int | None
    auto_renew: bool
    status: ContractStatus
