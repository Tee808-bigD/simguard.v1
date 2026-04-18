"""Transaction schemas — all inputs validated."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re
from app.config import settings

VALID_TX_TYPES = {"transfer", "withdrawal", "payment", "bill_payment"}


class TransactionCreate(BaseModel):
    phone_number: str = Field(..., min_length=1, max_length=20)
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    transaction_type: str = Field(default="transfer")
    recipient: Optional[str] = Field(None, max_length=20)
    recipient_name: Optional[str] = Field(None, max_length=settings.max_name_length)
    is_new_recipient: bool = Field(default=False)

    @field_validator("phone_number")
    @classmethod
    def v_phone(cls, v):
        c = re.sub(r"[\s\-\(\)\.]", "", v.strip())
        if not re.match(r"^\+\d{7,15}$", c):
            raise ValueError("Invalid phone. Use E.164 (+27821234567)")
        return c

    @field_validator("amount")
    @classmethod
    def v_amount(cls, v):
        if v > settings.max_transaction_amount:
            raise ValueError(f"Amount exceeds max (${settings.max_transaction_amount:,.0f})")
        if round(v, 2) != v:
            raise ValueError("Max 2 decimal places")
        return round(v, 2)

    @field_validator("currency")
    @classmethod
    def v_curr(cls, v):
        if not re.match(r"^[A-Za-z]{3}$", v.strip()):
            raise ValueError("Use ISO 4217 (USD, ZAR, KES)")
        return v.strip().upper()

    @field_validator("transaction_type")
    @classmethod
    def v_type(cls, v):
        if v.lower() not in VALID_TX_TYPES:
            raise ValueError(f"Must be: {', '.join(VALID_TX_TYPES)}")
        return v.lower()

    @field_validator("recipient")
    @classmethod
    def v_recip(cls, v):
        if v:
            c = re.sub(r"[\s\-\(\)\.]", "", v.strip())
            if not re.match(r"^\+\d{7,15}$", c):
                raise ValueError("Invalid recipient phone")
            return c
        return v

    @field_validator("recipient_name")
    @classmethod
    def v_name(cls, v):
        if v:
            c = re.sub(r"[^a-zA-Z\s\-'\.]", "", v.strip())
            if not c:
                raise ValueError("Name has invalid characters")
            return c[:settings.max_name_length]
        return v


class TransactionResponse(BaseModel):
    id: int
    phone_number: str
    amount: float
    currency: str
    transaction_type: str
    recipient: Optional[str]
    recipient_name: Optional[str]
    is_new_recipient: bool
    status: str
    risk_score: int
    ai_decision: Optional[str]
    ai_explanation: Optional[str]
    ai_confidence: Optional[float]
    response_time_ms: Optional[int]
    created_at: datetime
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    total: int
    transactions: List[TransactionResponse]
