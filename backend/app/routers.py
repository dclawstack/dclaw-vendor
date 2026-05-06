from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import uuid, random
from app.database import get_db

router = APIRouter()

class CreateEvaluationRequest(BaseModel):
    vendor_name: str
    category: str

class VendorEvaluation(BaseModel):
    id: str
    vendor_name: str
    category: str
    overall_score: float
    risk_rating: str
    performance_history: list[str]
    renewal_recommendation: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/evaluations", response_model=VendorEvaluation)
def create_evaluation(req: CreateEvaluationRequest, db: Session = Depends(get_db)):
    return VendorEvaluation(
        id=str(uuid.uuid4()),
        vendor_name=req.vendor_name,
        category=req.category,
        overall_score=round(random.uniform(60, 95), 1),
        risk_rating="Medium",
        performance_history=["On-time delivery 94%"],
        renewal_recommendation="Renew with 5% discount negotiation",
        created_at=datetime.utcnow(),
    )

@router.get("/evaluations/{id}/alternatives")
def get_alternatives(id: str, db: Session = Depends(get_db)):
    return [
        {"name": "Alternative Vendor A", "score": round(random.uniform(70, 95), 1), "risk": "Low"},
        {"name": "Alternative Vendor B", "score": round(random.uniform(65, 90), 1), "risk": "Medium"},
    ]
