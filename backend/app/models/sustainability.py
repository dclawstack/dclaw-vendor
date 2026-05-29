"""Vendor sustainability scoring model (Phase 7, V7.2).

An ESG scorecard for a vendor in a period: estimated carbon footprint plus
environmental / social / governance subscores and an overall composite, with
AI-suggested reduction targets. Kept historically for benchmarking + trend.
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


class SustainabilityScore(Base):
    __tablename__ = "sustainability_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    carbon_footprint: Mapped[float] = mapped_column(Float, nullable=False)  # tonnes CO2e/yr (est.)
    environmental_score: Mapped[float] = mapped_column(Float, nullable=False)
    social_score: Mapped[float] = mapped_column(Float, nullable=False)
    governance_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    # [{"target": "Cut Scope 1 emissions 10%", "by": "2027"}]
    targets: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    summary: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    vendor: Mapped["Vendor"] = relationship(lazy="selectin")
