"""Vendor performance scoring model (Phase 5, V5.1).

A ``PerformanceScore`` is a point-in-time scorecard for a vendor in a given
period. It stores the 10 individual KPI subscores (0–100, in ``kpis``) plus the
four rolled-up dimension scores and an overall composite, so trends and
peer benchmarks can be queried directly.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class PerformanceScore(Base):
    __tablename__ = "performance_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Rolled-up dimension scores (0–100) + composite.
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_score: Mapped[float] = mapped_column(Float, nullable=False)
    cost_score: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    # The 10 individual KPI subscores, e.g. {"defect_rate": 92.0, ...}
    kpis: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    vendor: Mapped["Vendor"] = relationship(lazy="selectin")
