"""Dashboard endpoints — rate limited."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.database import get_db
from app.models.transaction import Transaction
from app.models.fraud_alert import FraudAlert
from app.rate_limiter import limiter

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
@limiter.limit("60/minute")
async def stats(request: Request, db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Transaction.id)))).scalar() or 0
    approved = (await db.execute(select(func.count(Transaction.id)).where(Transaction.status == "approved"))).scalar() or 0
    blocked = (await db.execute(select(func.count(Transaction.id)).where(Transaction.status == "blocked"))).scalar() or 0
    flagged = (await db.execute(select(func.count(Transaction.id)).where(Transaction.status == "flagged"))).scalar() or 0
    alerts_count = (await db.execute(select(func.count(FraudAlert.id)))).scalar() or 0
    total_amt = (await db.execute(select(func.coalesce(func.sum(Transaction.amount), 0)))).scalar() or 0
    blocked_amt = (await db.execute(select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.status == "blocked"))).scalar() or 0
    avg_ms = (await db.execute(select(func.coalesce(func.avg(Transaction.response_time_ms), 0)))).scalar() or 0

    curr_rows = (await db.execute(
        select(Transaction.currency, func.count(Transaction.id).label("count"),
               func.coalesce(func.sum(Transaction.amount), 0).label("total"))
        .group_by(Transaction.currency)
    )).all()
    by_currency = {r.currency: {"count": r.count, "total": round(r.total, 2)} for r in curr_rows}

    critical = (await db.execute(select(func.count(FraudAlert.id)).where(FraudAlert.risk_level == "critical"))).scalar() or 0
    high = (await db.execute(select(func.count(FraudAlert.id)).where(FraudAlert.risk_level == "high"))).scalar() or 0

    return {
        "total_transactions": total, "approved": approved, "blocked": blocked, "flagged": flagged,
        "total_alerts": alerts_count, "total_amount_processed": round(total_amt, 2),
        "total_amount_blocked": round(blocked_amt, 2), "avg_response_time_ms": round(avg_ms, 0),
        "fraud_prevention_rate": round((blocked / total * 100), 1) if total else 0,
        "approval_rate": round((approved / total * 100), 1) if total else 0,
        "critical_alerts": critical, "high_alerts": high, "by_currency": by_currency,
    }


@router.get("/timeline")
@limiter.limit("60/minute")
async def timeline(request: Request, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(func.date(Transaction.created_at).label("date"), func.count(Transaction.id).label("total"),
               func.sum(case((Transaction.status == "approved", 1), else_=0)).label("approved"),
               func.sum(case((Transaction.status == "blocked", 1), else_=0)).label("blocked"),
               func.sum(case((Transaction.status == "flagged", 1), else_=0)).label("flagged"),)
        .group_by(func.date(Transaction.created_at)).order_by(func.date(Transaction.created_at))
    )).all()
    return {"timeline": [{"date": str(r.date), "total": r.total, "approved": int(r.approved or 0), "blocked": int(r.blocked or 0), "flagged": int(r.flagged or 0)} for r in rows]}


@router.get("/risk-distribution")
@limiter.limit("60/minute")
async def risk_dist(request: Request, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(FraudAlert.risk_level, func.count(FraudAlert.id)).group_by(FraudAlert.risk_level))).all()
    return {r.risk_level: r.count for r in rows}
