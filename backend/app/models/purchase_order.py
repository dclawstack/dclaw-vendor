import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base
from app.models.enums import POStatus

if TYPE_CHECKING:
    from app.models.po_line_item import POLineItem
    from app.models.vendor import Vendor


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="SET NULL"),
        index=True,
    )
    status: Mapped[POStatus] = mapped_column(
        Enum(POStatus, native_enum=False, length=20),
        default=POStatus.draft,
        nullable=False,
    )
    total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    expected_delivery: Mapped[date | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    vendor: Mapped["Vendor | None"] = relationship(
        back_populates="purchase_orders", lazy="selectin"
    )
    line_items: Mapped[list["POLineItem"]] = relationship(
        back_populates="purchase_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
