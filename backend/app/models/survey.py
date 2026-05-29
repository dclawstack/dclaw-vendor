"""Stakeholder survey + feedback models (Phase 7, V7.3).

A ``Survey`` collects ``SurveyResponse`` rows about a vendor; each response carries
a rating and an optional comment, with an AI sentiment label/score attached on
analysis. Responses cascade-delete with their survey.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class Survey(Base):
    __tablename__ = "surveys"

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
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    vendor: Mapped["Vendor"] = relationship(lazy="selectin")
    responses: Mapped[list["SurveyResponse"]] = relationship(
        back_populates="survey",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="SurveyResponse.created_at",
    )


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("surveys.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    respondent: Mapped[str | None] = mapped_column(String(120))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–5
    comment: Mapped[str | None] = mapped_column(Text)
    # AI sentiment (set on analysis): "positive" | "neutral" | "negative"
    sentiment: Mapped[str | None] = mapped_column(String(20))
    sentiment_score: Mapped[float | None] = mapped_column(Float)  # -1.0 … 1.0

    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    survey: Mapped["Survey"] = relationship(back_populates="responses")
