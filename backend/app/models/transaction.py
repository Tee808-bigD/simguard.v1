"""Transaction model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    transaction_type = Column(String(20), nullable=False, default="transfer")
    recipient = Column(String(20), nullable=True)
    recipient_name = Column(String(100), nullable=True)
    is_new_recipient = Column(Integer, default=0)
    status = Column(String(20), nullable=False, default="pending")
    risk_score = Column(Integer, default=0)
    fraud_alert_id = Column(Integer, ForeignKey("fraud_alerts.id"), nullable=True)
    ai_decision = Column(String(20), nullable=True)
    ai_explanation = Column(Text, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
