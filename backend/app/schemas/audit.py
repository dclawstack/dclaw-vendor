"""Schemas for vendor audit + compliance (Phase 7, V7.4)."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AuditStatus, FindingSeverity, FindingStatus


class AuditFindingCreate(BaseModel):
    description: str
    severity: FindingSeverity = FindingSeverity.medium
    remediation: str | None = None


class AuditFindingUpdate(BaseModel):
    description: str | None = None
    severity: FindingSeverity | None = None
    status: FindingStatus | None = None
    remediation: str | None = None


class AuditFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    audit_id: uuid.UUID
    description: str
    severity: FindingSeverity
    status: FindingStatus
    remediation: str | None
    closed_at: datetime | None
    created_at: datetime


class AuditCreate(BaseModel):
    vendor_id: uuid.UUID
    title: str
    scheduled_date: date | None = None
    auditor: str | None = None
    notes: str | None = None


class AuditUpdate(BaseModel):
    title: str | None = None
    status: AuditStatus | None = None
    scheduled_date: date | None = None
    auditor: str | None = None
    notes: str | None = None


class AuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    title: str
    status: AuditStatus
    scheduled_date: date | None
    auditor: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    findings: list[AuditFindingRead] = []


class AuditList(BaseModel):
    items: list[AuditRead]
    total: int
