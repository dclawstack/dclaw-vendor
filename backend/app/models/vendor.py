import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from typing import Any

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base
from app.models.enums import VendorStatus, VendorTier

if TYPE_CHECKING:
    from app.models.purchase_order import PurchaseOrder


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(500))
    payment_terms: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[VendorStatus] = mapped_column(
        Enum(VendorStatus, native_enum=False, length=20),
        default=VendorStatus.active,
        nullable=False,
    )

    # --- Directory: AI classification + web enrichment (Phase 3) ---------
    category: Mapped[str | None] = mapped_column(String(120), index=True)
    industry: Mapped[str | None] = mapped_column(String(120), index=True)
    tier: Mapped[VendorTier | None] = mapped_column(
        Enum(VendorTier, native_enum=False, length=20), index=True
    )
    website: Mapped[str | None] = mapped_column(String(255))
    # Enriched profile + provenance, e.g.
    # {"company_size": "...", "founded_year": 1998, "headquarters": "...",
    #  "description": "...", "source": "web"|"inferred", "fetched_url": "...",
    #  "enriched_at": "<iso>"}
    enrichment: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # --- Diversity tracking (Phase 7, V7.1) ------------------------------
    diverse_owned: Mapped[bool] = mapped_column(default=False, nullable=False)
    # e.g. ["minority_owned", "women_owned", "veteran_owned", "lgbtq_owned",
    #       "disability_owned", "small_business"]
    diversity_categories: Mapped[list[str] | None] = mapped_column(JSONB)
    diversity_certified: Mapped[bool] = mapped_column(default=False, nullable=False)
    certification_body: Mapped[str | None] = mapped_column(String(120))

    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(
        back_populates="vendor", lazy="selectin"
    )
