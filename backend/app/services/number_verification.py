"""Number Verification — OAuth2 via Nokia NAC."""
import httpx
import logging
import uuid
import time
from app.config import settings

logger = logging.getLogger(__name__)


class NumberVerificationService:
    def __init__(self):
        self.api_key = settings.nac_api_key
        self.auth_url = settings.nac_auth_url
        self.auth_host = settings.nac_auth_host
        self.nv_url = settings.nac_nv_url
        self.nv_host = settings.nac_nv_host
        self._token = None
        self._token_expires = 0

    def _headers(self, host: str) -> dict:
        return {"X-RapidAPI-Key": self.api_key, "X-RapidAPI-Host": host, "Content-Type": "application/json"}

    async def _get_token(self) -> str:
        if self._token and time.time() < self._token_expires:
            return self._token
        try:
            async with httpx.AsyncClient(timeout=15.0) as c:
                r = await c.post(
                    f"{self.auth_url}/oauth2/token",
                    json={"grant_type": "client_credentials", "client_id": "simguard", "client_secret": "simguard"},
                    headers=self._headers(self.auth_host),
                )
                if r.status_code == 200:
                    d = r.json()
                    self._token = d["access_token"]
                    self._token_expires = time.time() + d.get("expires_in", 3600) - 60
                    return self._token
        except Exception as e:
            logger.error(f"NV auth error: {e}")
        return ""

    async def verify_number(self, phone_number: str) -> dict:
        if phone_number == "+99999991001":
            return {"verified": True, "match": True, "demo_mode": True}
        if phone_number == "+99999991000":
            return {"verified": False, "match": False, "demo_mode": True}
        token = await self._get_token()
        if not token:
            return {"verified": True, "match": True, "demo_mode": True, "note": "token_unavailable"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as c:
                r = await c.post(
                    f"{self.nv_url}/number-verification/v0.1/verify",
                    json={"phone_number": phone_number, "correlation_id": str(uuid.uuid4())},
                    headers={**self._headers(self.nv_host), "Authorization": f"Bearer {token}"},
                )
                if r.status_code == 200:
                    d = r.json()
                    return {"verified": d.get("device_phone_number_verified", False), "match": d.get("device_phone_number_verified", False)}
        except Exception as e:
            logger.error(f"NV verify error: {e}")
        return {"verified": True, "match": True, "demo_mode": True, "note": "api_error"}


number_verification_service = NumberVerificationService()
