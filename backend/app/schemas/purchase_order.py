import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import POStatus
from app.schemas.po_line_item import POLineItemNestedCreate, POLineItemRead


class PurchaseOrderBase(BaseModel):
    vendor_id: uuid.UUID | None = None
    status: POStatus = POStatus.draft
    expected_delivery: date | None = None
    notes: str | None = None


class PurchaseOrderCreate(PurchaseOrderBase):
    # total is derived from line items, not client-supplied
    line_items: list[POLineItemNestedCreate] = []


class PurchaseOrderUpdate(BaseModel):
    vendor_id: uuid.UUID | None = None
    status: POStatus | None = None
    expected_delivery: date | None = None
    notes: str | None = None


class PurchaseOrderRead(PurchaseOrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    total: float
    created_at: datetime
    updated_at: datetime
    line_items: list[POLineItemRead] = []


class PurchaseOrderList(BaseModel):
    items: list[PurchaseOrderRead]
    total: int
