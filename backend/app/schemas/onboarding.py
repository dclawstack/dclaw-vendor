"""Schemas for the onboarding workflow (Phase 4)."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApprovalStatus, DocumentStatus, OnboardingStatus


# --- AI structured outputs (V4.3) ---------------------------------------


class ChecklistItem(BaseModel):
    item: str = Field(description="what the vendor must provide")
    doc_type: str = Field(description="short slug, e.g. 'w9', 'insurance', 'banking'")
    required: bool = True


class GeneratedChecklist(BaseModel):
    items: list[ChecklistItem]


class DocumentValidation(BaseModel):
    valid: bool = Field(description="whether the document satisfies its expected type")
    doc_type_detected: str = Field(description="the document type the content looks like")
    issues: list[str] = Field(
        default_factory=list, description="problems found, empty if valid"
    )


# --- API I/O ------------------------------------------------------------


class StepCreate(BaseModel):
    name: str
    approver_role: str | None = None


class OnboardingCaseCreate(BaseModel):
    vendor_id: uuid.UUID
    notes: str | None = None
    # Optional custom approval chain; defaults to Compliance → Finance.
    steps: list[StepCreate] | None = None


class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject"]
    decided_by: str | None = None
    comment: str | None = None


class ApprovalStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    step_order: int
    name: str
    approver_role: str | None
    status: ApprovalStatus
    decided_by: str | None
    decided_at: datetime | None
    comment: str | None


class OnboardingDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    doc_type: str
    filename: str
    content_type: str | None
    size: int | None
    status: DocumentStatus
    validation: dict[str, Any] | None
    uploaded_at: datetime


class OnboardingCaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    status: OnboardingStatus
    checklist: list[dict[str, Any]] | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    documents: list[OnboardingDocumentRead] = []
    steps: list[ApprovalStepRead] = []


class OnboardingCaseList(BaseModel):
    items: list[OnboardingCaseRead]
    total: int
