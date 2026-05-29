"""Audit & compliance logic (Phase 7, V7.4).

Pure state-machine helpers: closing a finding stamps it closed; closing an audit
is validated — it can only close once every finding is closed. Callers commit.
"""

from __future__ import annotations

from app.core.utils import utc_now
from app.models.audit import Audit, AuditFinding
from app.models.enums import AuditStatus, FindingStatus


def open_findings(audit: Audit) -> list[AuditFinding]:
    return [f for f in audit.findings if f.status != FindingStatus.closed]


def close_finding(finding: AuditFinding) -> None:
    finding.status = FindingStatus.closed
    finding.closed_at = utc_now()


def validate_closure(audit: Audit) -> None:
    """Raise if the audit can't be closed yet."""
    if audit.status == AuditStatus.closed:
        raise ValueError("audit is already closed")
    remaining = open_findings(audit)
    if remaining:
        raise ValueError(
            f"cannot close audit: {len(remaining)} finding(s) still open"
        )


def close_audit(audit: Audit) -> None:
    validate_closure(audit)
    audit.status = AuditStatus.closed
