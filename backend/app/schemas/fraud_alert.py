"""Fraud alert schemas."""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class FraudAlertResponse(BaseModel):
    id: int
    transaction_id: Optional[int]
    phone_number: str
    alert_type: str
    risk_level: str
    risk_score: int
    camara_checks: Optional[Any]
    ai_analysis: Optional[Any]
    action_taken: Optional[str]
    explanation: Optional[str]
    recommended_actions: Optional[Any]
    created_at: datetime
    class Config:
        from_attributes = True


class FraudAlertListResponse(BaseModel):
    total: int
    alerts: List[FraudAlertResponse]


class FraudCheckRequest(BaseModel):
    phone_number: str
    amount: float
    currency: str = "USD"
    is_new_recipient: bool = False


class FraudCheckResponse(BaseModel):
    risk_score: int
    risk_level: str
    decision: str
    explanation: str
    confidence: float
    checks_performed: dict
    recommended_actions: list
