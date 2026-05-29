"""Vendor risk assessment model (Phase 6, V6.1).

A ``RiskAssessment`` is a point-in-time evaluation of a vendor against the risk
catalog (see ``app.services.risk.RISK_TYPES``). Assessments are kept historically
so the monitoring endpoint can diff the latest two and surface change alerts.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base
from app.models.enums import RiskLevel

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    overall_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, native_enum=False, length=10), nullable=False
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0–100, higher = riskier
    # [{"type": "financial", "severity": "high", "note": "..."}]
    factors: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    vendor: Mapped["Vendor"] = relationship(lazy="selectin")
