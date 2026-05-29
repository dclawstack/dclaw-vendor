"""Onboarding workflow models (Phase 4).

An ``OnboardingCase`` tracks a vendor through document collection, AI validation,
and a multi-step approval chain before the vendor is activated. Documents and
approval steps belong to a case and cascade-delete with it.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base
from app.models.enums import ApprovalStatus, DocumentStatus, OnboardingStatus

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class OnboardingCase(Base):
    __tablename__ = "onboarding_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[OnboardingStatus] = mapped_column(
        Enum(OnboardingStatus, native_enum=False, length=20),
        default=OnboardingStatus.draft,
        nullable=False,
    )
    # AI-generated checklist: [{"item": "...", "required": true, "doc_type": "W9"}]
    checklist: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    vendor: Mapped["Vendor"] = relationship(lazy="selectin")
    documents: Mapped[list["OnboardingDocument"]] = relationship(
        back_populates="case",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="OnboardingDocument.uploaded_at",
    )
    steps: Mapped[list["ApprovalStep"]] = relationship(
        back_populates="case",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ApprovalStep.step_order",
    )


class OnboardingDocument(Base):
    __tablename__ = "onboarding_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("onboarding_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doc_type: Mapped[str] = mapped_column(String(80), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120))
    size: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, native_enum=False, length=20),
        default=DocumentStatus.uploaded,
        nullable=False,
    )
    # AI validation result: {"valid": bool, "issues": [...], "doc_type_detected": "..."}
    validation: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    uploaded_at: Mapped[datetime] = mapped_column(default=utc_now)

    case: Mapped["OnboardingCase"] = relationship(back_populates="documents")


class ApprovalStep(Base):
    __tablename__ = "approval_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("onboarding_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    approver_role: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, native_enum=False, length=20),
        default=ApprovalStatus.pending,
        nullable=False,
    )
    decided_by: Mapped[str | None] = mapped_column(String(120))
    decided_at: Mapped[datetime | None] = mapped_column()
    comment: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    case: Mapped["OnboardingCase"] = relationship(back_populates="steps")
