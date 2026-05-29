import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class POLineItemNestedCreate(BaseModel):
    """Line item supplied inline when creating a purchase order (no po_id)."""

    product_name: str
    description: str | None = None
    quantity: int = 1
    unit_price: float = 0.0
    received_qty: int = 0


class POLineItemCreate(POLineItemNestedCreate):
    po_id: uuid.UUID


class POLineItemUpdate(BaseModel):
    product_name: str | None = None
    description: str | None = None
    quantity: int | None = None
    unit_price: float | None = None
    received_qty: int | None = None


class POLineItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_id: uuid.UUID
    product_name: str
    description: str | None
    quantity: int
    unit_price: float
    received_qty: int
    created_at: datetime
    updated_at: datetime


class POLineItemList(BaseModel):
    items: list[POLineItemRead]
    total: int
