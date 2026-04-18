"""FraudAlert model."""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, nullable=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(30), nullable=False)
    risk_level = Column(String(20), nullable=False)
    risk_score = Column(Integer, nullable=False)
    camara_checks = Column(JSON, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    action_taken = Column(String(20), nullable=True)
    explanation = Column(Text, nullable=True)
    recommended_actions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
