"""Onboarding workflow logic (Phase 4).

Two concerns live here:

- **AI (V4.3):** generate a tailored document checklist for a vendor, and validate
  an uploaded document against its expected type — both via the LLM's structured
  output helper.
- **Approval state machine (V4.4):** a case carries an ordered chain of
  ``ApprovalStep`` rows. Submitting moves a case to ``pending_approval``; deciding
  the current step advances the chain; all-approved → ``approved``; any rejection
  → ``rejected``; activation flips the vendor to ``active`` and the case to
  ``activated``. The functions mutate ORM objects in place — the caller commits.
"""

from __future__ import annotations

from app.core.utils import utc_now
from app.models.enums import (
    ApprovalStatus,
    DocumentStatus,
    OnboardingStatus,
    VendorStatus,
)
from app.models.onboarding import ApprovalStep, OnboardingCase, OnboardingDocument
from app.models.vendor import Vendor
from app.schemas.onboarding import DocumentValidation, GeneratedChecklist
from app.services.llm import LLMService

DEFAULT_STEPS: list[tuple[str, str]] = [
    ("Compliance review", "compliance"),
    ("Finance approval", "finance"),
]

_CHECKLIST_SYSTEM = (
    "You are a vendor-onboarding specialist. Produce the list of documents and "
    "information a new vendor must provide before they can be approved. Tailor it "
    "to the vendor's category/industry when known. Keep it to the essentials "
    "(tax form, banking details, insurance/compliance certs, references)."
)

_VALIDATION_SYSTEM = (
    "You validate onboarding documents. Given the expected document type and the "
    "extracted text of an uploaded file, decide whether the content matches the "
    "expected type and list any problems (wrong type, missing fields, illegible)."
)


# --- AI (V4.3) ----------------------------------------------------------


async def generate_checklist(llm: LLMService, vendor: Vendor) -> GeneratedChecklist:
    context = (
        f"Vendor: {vendor.name}\n"
        f"Category: {vendor.category or 'unknown'}\n"
        f"Industry: {vendor.industry or 'unknown'}\n"
        f"Tier: {vendor.tier.value if vendor.tier else 'unclassified'}"
    )
    return await llm.structured(
        [
            {"role": "system", "content": _CHECKLIST_SYSTEM},
            {"role": "user", "content": f"Onboarding checklist for:\n{context}"},
        ],
        GeneratedChecklist,
    )


async def validate_document(
    llm: LLMService, doc_type: str, content_text: str
) -> DocumentValidation:
    snippet = content_text[:4000] if content_text else "(no extractable text)"
    return await llm.structured(
        [
            {"role": "system", "content": _VALIDATION_SYSTEM},
            {
                "role": "user",
                "content": f"Expected type: {doc_type}\n\nExtracted text:\n{snippet}",
            },
        ],
        DocumentValidation,
    )


def apply_validation(doc: OnboardingDocument, result: DocumentValidation) -> None:
    doc.validation = result.model_dump()
    doc.status = DocumentStatus.validated if result.valid else DocumentStatus.rejected


# --- Approval state machine (V4.4) --------------------------------------


def build_steps(names_roles: list[tuple[str, str | None]]) -> list[ApprovalStep]:
    return [
        ApprovalStep(step_order=i, name=name, approver_role=role)
        for i, (name, role) in enumerate(names_roles)
    ]


def submit_case(case: OnboardingCase) -> None:
    """Move a case into the approval chain. Idempotent-ish: only from draft/collecting."""
    if case.status not in (OnboardingStatus.draft, OnboardingStatus.collecting):
        raise ValueError(f"cannot submit a case in status '{case.status.value}'")
    if not case.steps:
        raise ValueError("case has no approval steps")
    case.status = OnboardingStatus.pending_approval


def current_step(case: OnboardingCase) -> ApprovalStep | None:
    """The first still-pending step in order, or None if the chain is complete."""
    for step in sorted(case.steps, key=lambda s: s.step_order):
        if step.status == ApprovalStatus.pending:
            return step
    return None


def decide_step(
    case: OnboardingCase,
    step: ApprovalStep,
    *,
    approve: bool,
    decided_by: str | None,
    comment: str | None,
) -> None:
    if case.status != OnboardingStatus.pending_approval:
        raise ValueError("case is not pending approval")
    active = current_step(case)
    if active is None or active.id != step.id:
        raise ValueError("steps must be decided in order")

    step.decided_by = decided_by
    step.decided_at = utc_now()
    step.comment = comment

    if not approve:
        step.status = ApprovalStatus.rejected
        case.status = OnboardingStatus.rejected
        return

    step.status = ApprovalStatus.approved
    if current_step(case) is None:  # no more pending steps
        case.status = OnboardingStatus.approved


def activate_case(case: OnboardingCase) -> None:
    if case.status != OnboardingStatus.approved:
        raise ValueError("only an approved case can be activated")
    case.status = OnboardingStatus.activated
    case.vendor.status = VendorStatus.active
