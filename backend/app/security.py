"""Security utilities — input sanitization, payload validation."""
import re
from fastapi import Request, HTTPException
from app.config import settings


def sanitize_phone(phone: str) -> str:
    if not phone:
        raise HTTPException(status_code=422, detail="Phone number is required")
    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone.strip())
    if not re.match(r"^\+\d{7,15}$", cleaned):
        raise HTTPException(status_code=422, detail="Invalid phone number. Use E.164 format (e.g. +27821234567)")
    if len(cleaned) > settings.max_phone_length:
        raise HTTPException(status_code=422, detail=f"Phone number too long (max {settings.max_phone_length})")
    return cleaned


def validate_amount(amount: float) -> float:
    if amount is None or amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be greater than zero")
    if amount > settings.max_transaction_amount:
        raise HTTPException(status_code=422, detail=f"Amount exceeds maximum (${settings.max_transaction_amount:,.0f})")
    if round(amount, 2) != amount:
        raise HTTPException(status_code=422, detail="Amount can have at most 2 decimal places")
    return round(amount, 2)


def validate_currency(currency: str) -> str:
    if not currency or not re.match(r"^[A-Z]{3}$", currency.strip()):
        raise HTTPException(status_code=422, detail="Invalid currency code. Use ISO 4217 (e.g. USD, ZAR, KES)")
    return currency.strip().upper()


async def check_payload_size(request: Request):
    cl = request.headers.get("content-length")
    if cl and int(cl) > settings.max_payload_bytes:
        raise HTTPException(status_code=413, detail=f"Payload too large (max {settings.max_payload_bytes} bytes)")


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "Pragma": "no-cache",
}
