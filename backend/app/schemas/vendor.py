import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import VendorStatus


class VendorBase(BaseModel):
    name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    payment_terms: str | None = None
    status: VendorStatus = VendorStatus.active


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    payment_terms: str | None = None
    status: VendorStatus | None = None


class VendorRead(VendorBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class VendorList(BaseModel):
    items: list[VendorRead]
    total: int
