import enum


class VendorStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    blacklisted = "blacklisted"


class POStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    partial = "partial"
    received = "received"
    cancelled = "cancelled"
