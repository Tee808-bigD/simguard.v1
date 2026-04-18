"""Verification endpoints — rate limited."""
from datetime import datetime
from fastapi import APIRouter, Request
from app.schemas.sim_check import SimSwapStatusResponse, DeviceSwapStatusResponse
from app.services.camara import camara_service
from app.services.number_verification import number_verification_service
from app.rate_limiter import limiter

router = APIRouter(prefix="/api/verification", tags=["Verification"])


@router.get("/sim-status/{phone_number}", response_model=SimSwapStatusResponse)
@limiter.limit("30/minute")
async def sim_status(request: Request, phone_number: str):
    r = await camara_service.check_sim_swap(phone_number)
    return SimSwapStatusResponse(phone_number=phone_number, sim_swap_detected=r.get("sim_swap_detected", False), swap_date=r.get("swap_date"), checked_at=datetime.utcnow())


@router.get("/device-status/{phone_number}", response_model=DeviceSwapStatusResponse)
@limiter.limit("30/minute")
async def device_status(request: Request, phone_number: str):
    r = await camara_service.check_device_swap(phone_number)
    return DeviceSwapStatusResponse(phone_number=phone_number, device_swap_detected=r.get("device_swap_detected", False), device_swap_date=r.get("device_swap_date"), checked_at=datetime.utcnow())


@router.post("/verify-number")
@limiter.limit("20/minute")
async def verify(request: Request, phone_number: str):
    r = await number_verification_service.verify_number(phone_number)
    return {"phone_number": phone_number, "verified": r.get("verified", False), "match": r.get("match", False)}
