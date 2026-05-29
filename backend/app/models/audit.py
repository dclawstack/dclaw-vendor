"""Vendor audit + compliance models (Phase 7, V7.4).

An ``Audit`` is scheduled against a vendor and accumulates ``AuditFinding`` rows.
Closure is validated by the service: an audit can only be closed once every
finding is closed. Findings cascade-delete with their audit.
"""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base
from app.models.enums import AuditStatus, FindingSeverity, FindingStatus

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[AuditStatus] = mapped_column(
        Enum(AuditStatus, native_enum=False, length=20),
        default=AuditStatus.scheduled,
        nullable=False,
    )
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    auditor: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    vendor: Mapped["Vendor"] = relationship(lazy="selectin")
    findings: Mapped[list["AuditFinding"]] = relationship(
        back_populates="audit",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="AuditFinding.created_at",
    )


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[FindingSeverity] = mapped_column(
        Enum(FindingSeverity, native_enum=False, length=20),
        default=FindingSeverity.medium,
        nullable=False,
    )
    status: Mapped[FindingStatus] = mapped_column(
        Enum(FindingStatus, native_enum=False, length=20),
        default=FindingStatus.open,
        nullable=False,
    )
    remediation: Mapped[str | None] = mapped_column(Text)
    closed_at: Mapped[datetime | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    audit: Mapped["Audit"] = relationship(back_populates="findings")
