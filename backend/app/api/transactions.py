"""Transaction endpoints — rate limited, sanitized."""
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.transaction import Transaction
from app.models.fraud_alert import FraudAlert
from app.models.sim_check import SimCheck
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionListResponse
from app.services.camara import camara_service
from app.services.number_verification import number_verification_service
from app.services.fraud_detector import calculate_risk_score, get_alert_type
from app.services.ai_engine import ai_engine
from app.websocket import broadcast_alert
from app.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=201)
@limiter.limit("30/minute")
async def create_transaction(request: Request, data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    start = time.time()
    sim_result = await camara_service.check_sim_swap(data.phone_number)
    dev_result = await camara_service.check_device_swap(data.phone_number)
    nv_result = await number_verification_service.verify_number(data.phone_number)
    camara_results = {"sim_swap": sim_result, "device_swap": dev_result, "number_verification": nv_result}
    tx_dict = data.model_dump()
    risk = calculate_risk_score(tx_dict, camara_results)
    ai = await ai_engine.analyze(tx_dict, camara_results, risk)
    decision = ai.get("decision", "APPROVE")
    status_map = {"BLOCK": "blocked", "APPROVE": "approved", "FLAG": "flagged"}
    final_status = status_map.get(decision, "flagged")
    ms = int((time.time() - start) * 1000)

    sim_check = SimCheck(
        phone_number=data.phone_number, sim_swap_detected=sim_result.get("sim_swap_detected", False),
        swap_date=sim_result.get("swap_date"), device_swap_detected=dev_result.get("device_swap_detected", False),
        device_swap_date=dev_result.get("device_swap_date"), number_verified=nv_result.get("verified"),
        check_results=camara_results,
    )
    db.add(sim_check)
    await db.flush()

    fraud_alert = None
    if final_status != "approved":
        fraud_alert = FraudAlert(
            phone_number=data.phone_number, alert_type=get_alert_type(risk["flags"]),
            risk_level=risk["risk_level"], risk_score=risk["score"], camara_checks=camara_results,
            ai_analysis=ai, action_taken=final_status,
            explanation=ai.get("explanation", ""), recommended_actions=ai.get("recommended_actions", []),
        )
        db.add(fraud_alert)
        await db.flush()

    txn = Transaction(
        phone_number=data.phone_number, amount=data.amount, currency=data.currency,
        transaction_type=data.transaction_type, recipient=data.recipient,
        recipient_name=data.recipient_name, is_new_recipient=1 if data.is_new_recipient else 0,
        status=final_status, risk_score=risk["score"],
        fraud_alert_id=fraud_alert.id if fraud_alert else None,
        ai_decision=decision, ai_explanation=ai.get("explanation", ""),
        ai_confidence=ai.get("confidence", 0.0), response_time_ms=ms,
    )
    db.add(txn)
    await db.flush()

    if fraud_alert:
        await broadcast_alert({
            "id": fraud_alert.id, "phone_number": fraud_alert.phone_number,
            "alert_type": fraud_alert.alert_type, "risk_level": fraud_alert.risk_level,
            "risk_score": fraud_alert.risk_score, "action_taken": fraud_alert.action_taken,
            "explanation": fraud_alert.explanation,
            "recommended_actions": fraud_alert.recommended_actions,
            "transaction_id": txn.id, "amount": data.amount, "currency": data.currency,
        })

    await db.refresh(txn)
    logger.info(f"TX {txn.id}: {data.phone_number} {data.currency}{data.amount} -> {decision} ({ms}ms)")
    return txn


@router.get("", response_model=TransactionListResponse)
@limiter.limit("60/minute")
async def list_transactions(request: Request, status: str = Query(None), currency: str = Query(None),
                             limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
                             db: AsyncSession = Depends(get_db)):
    q = select(Transaction)
    cq = select(func.count(Transaction.id))
    if status:
        q = q.where(Transaction.status == status); cq = cq.where(Transaction.status == status)
    if currency:
        q = q.where(Transaction.currency == currency.upper()); cq = cq.where(Transaction.currency == currency.upper())
    total = (await db.execute(cq)).scalar()
    rows = (await db.execute(q.order_by(desc(Transaction.created_at)).offset(offset).limit(limit))).scalars().all()
    return TransactionListResponse(total=total, transactions=rows)


@router.get("/{transaction_id}", response_model=TransactionResponse)
@limiter.limit("60/minute")
async def get_transaction(request: Request, transaction_id: int, db: AsyncSession = Depends(get_db)):
    txn = (await db.execute(select(Transaction).where(Transaction.id == transaction_id))).scalar_one_or_none()
    if not txn:
        raise HTTPException(404, "Transaction not found")
    return txn
