"""Contract management logic (Phase 6, V6.2).

AI key-term extraction plus deterministic renewal/status helpers. ``derive_status``
keeps a contract's status in sync with its dates (active → expiring within the
window → expired) without overriding a manual draft/terminated state.
"""

from __future__ import annotations

from datetime import date

from app.models.contract import Contract
from app.models.enums import ContractStatus
from app.schemas.contract import ExtractedTerms
from app.services.llm import LLMService

EXPIRING_WINDOW_DAYS = 60

_SYSTEM = (
    "You extract key commercial terms from a contract. Use only what the text "
    "supports; leave a field null if it isn't present. Keep each value to a short "
    "phrase."
)


async def extract_terms(llm: LLMService, text: str) -> ExtractedTerms:
    return await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Extract key terms:\n\n{text[:6000]}"},
        ],
        ExtractedTerms,
    )


def days_to_expiry(contract: Contract, today: date) -> int | None:
    if contract.end_date is None:
        return None
    return (contract.end_date - today).days


def derive_status(contract: Contract, today: date) -> ContractStatus:
    """Status implied by dates; manual draft/terminated states are preserved."""
    if contract.status in (ContractStatus.draft, ContractStatus.terminated):
        return contract.status
    dte = days_to_expiry(contract, today)
    if dte is None:
        return ContractStatus.active
    if dte < 0:
        return ContractStatus.expired
    if dte <= EXPIRING_WINDOW_DAYS:
        return ContractStatus.expiring
    return ContractStatus.active
