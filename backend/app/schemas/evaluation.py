import uuid
from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["low", "medium", "high"]
Recommendation = Literal["approve", "monitor", "review", "avoid"]


class VendorEvaluation(BaseModel):
    """AI-generated assessment of a single vendor (V2.2)."""

    risk_level: RiskLevel = Field(description="overall procurement risk")
    risk_flags: list[str] = Field(
        default_factory=list, description="specific risk factors identified"
    )
    performance_outlook: str = Field(
        description="one-sentence prediction of future performance"
    )
    summary: str = Field(description="2-3 sentence overall assessment")
    recommendation: Recommendation = Field(description="suggested next action")


class VendorEvaluationResult(BaseModel):
    """An evaluation tagged with its vendor (used in single + batch responses)."""

    vendor_id: uuid.UUID
    vendor_name: str
    evaluation: VendorEvaluation | None = None
    error: str | None = None


class BatchEvaluationResponse(BaseModel):
    results: list[VendorEvaluationResult]
    evaluated: int
    failed: int
