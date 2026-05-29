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


class OnboardingStatus(str, enum.Enum):
    """Lifecycle of a vendor onboarding case (Phase 4)."""

    draft = "draft"
    collecting = "collecting"
    pending_approval = "pending_approval"
    approved = "approved"
    rejected = "rejected"
    activated = "activated"


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class DocumentStatus(str, enum.Enum):
    uploaded = "uploaded"
    validated = "validated"
    rejected = "rejected"
