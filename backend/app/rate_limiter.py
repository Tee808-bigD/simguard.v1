"""Rate limiting with auth lockout."""
import time
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request, HTTPException, status
from app.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"], storage_uri="memory://")

_auth_attempts = {}


def check_auth_attempts(request: Request) -> None:
    ip = get_remote_address(request)
    rec = _auth_attempts.get(ip)
    if rec:
        if rec["locked_until"] and time.time() < rec["locked_until"]:
            remaining = int(rec["locked_until"] - time.time())
            raise HTTPException(status_code=429, detail=f"Too many failed attempts. Locked out for {remaining}s.")
        if rec["locked_until"] and time.time() >= rec["locked_until"]:
            _auth_attempts[ip] = {"count": 0, "locked_until": None}


def record_failed_auth(request: Request) -> None:
    ip = get_remote_address(request)
    rec = _auth_attempts.get(ip, {"count": 0, "locked_until": None})
    rec["count"] += 1
    if rec["count"] >= settings.auth_max_attempts:
        rec["locked_until"] = time.time() + (settings.auth_lockout_minutes * 60)
    _auth_attempts[ip] = rec


def reset_auth_attempts(request: Request) -> None:
    ip = get_remote_address(request)
    _auth_attempts.pop(ip, None)
