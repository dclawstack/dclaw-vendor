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


class VendorTier(str, enum.Enum):
    """Strategic importance of a vendor (set by AI classification, V3.1)."""

    strategic = "strategic"
    preferred = "preferred"
    approved = "approved"
    transactional = "transactional"
