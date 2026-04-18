"""Fraud check endpoints — rate limited."""
import logging
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.fraud_alert import FraudAlert
from app.schemas.fraud_alert import FraudCheckRequest, FraudCheckResponse, FraudAlertListResponse
from app.services.camara import camara_service
from app.services.number_verification import number_verification_service
from app.services.fraud_detector import calculate_risk_score
from app.services.ai_engine import ai_engine
from app.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/fraud", tags=["Fraud"])


@router.post("/check", response_model=FraudCheckResponse)
@limiter.limit("30/minute")
async def quick_check(request: Request, data: FraudCheckRequest):
    sim = await camara_service.check_sim_swap(data.phone_number)
    dev = await camara_service.check_device_swap(data.phone_number)
    nv = await number_verification_service.verify_number(data.phone_number)
    camara = {
        "sim_swap": {"sim_swap_detected": sim.get("sim_swap_detected"), "swap_date": sim.get("swap_date")},
        "device_swap": {"device_swap_detected": dev.get("device_swap_detected"), "device_swap_date": dev.get("device_swap_date")},
        "number_verification": {"verified": nv.get("verified")},
    }
    tx = {"phone_number": data.phone_number, "amount": data.amount, "currency": data.currency, "is_new_recipient": data.is_new_recipient}
    risk = calculate_risk_score(tx, camara)
    ai = await ai_engine.analyze(tx, camara, risk)
    return FraudCheckResponse(
        risk_score=risk["score"], risk_level=risk["risk_level"].upper(),
        decision=ai.get("decision", "FLAG"), explanation=ai.get("explanation", ""),
        confidence=ai.get("confidence", 0.0), checks_performed=camara,
        recommended_actions=ai.get("recommended_actions", []),
    )


@router.get("/alerts", response_model=FraudAlertListResponse)
@limiter.limit("60/minute")
async def list_alerts(request: Request, risk_level: str = Query(None),
                       limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db)):
    q = select(FraudAlert); cq = select(func.count(FraudAlert.id))
    if risk_level:
        q = q.where(FraudAlert.risk_level == risk_level); cq = cq.where(FraudAlert.risk_level == risk_level)
    total = (await db.execute(cq)).scalar()
    rows = (await db.execute(q.order_by(desc(FraudAlert.created_at)).offset(offset).limit(limit))).scalars().all()
    return FraudAlertListResponse(total=total, alerts=rows)
