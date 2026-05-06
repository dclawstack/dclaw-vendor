from sqlalchemy import Column, String, Float, DateTime, func
from app.database import Base

class VendorEvaluationDB(Base):
    __tablename__ = "vendor_evaluations"
    id = Column(String, primary_key=True)
    vendor_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    overall_score = Column(Float)
    risk_rating = Column(String)
    performance_history = Column(String)
    renewal_recommendation = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
