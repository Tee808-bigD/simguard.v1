"""CAMARA API — SIM Swap + Device Swap. Credentials from env only."""
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)
SWAP_OCCURRED = "+99999991000"
NO_SWAP = "+99999991001"


class CamaraService:
    def __init__(self):
        self.api_key = settings.nac_api_key
        self.api_host = settings.nac_api_host
        self.base_url = f"https://{self.api_host}"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host,
            "Content-Type": "application/json",
        }

    async def check_sim_swap(self, phone_number: str, max_age_hours: int = 24) -> dict:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.base_url}/sim-swap/v0.1/check",
                    json={"phone_number": phone_number, "max_age_hours": max_age_hours},
                    headers=self.headers,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"sim_swap_detected": data.get("sim_swap_detected", False), "swap_date": data.get("last_swap_date"), "raw_response": data}
                logger.warning(f"SIM swap API {resp.status_code}")
                return self._demo_sim(phone_number)
        except Exception as e:
            logger.error(f"SIM swap error: {e}")
            return self._demo_sim(phone_number)

    async def check_device_swap(self, phone_number: str, max_age_hours: int = 240) -> dict:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.base_url}/device-swap/v0.1/check",
                    json={"phone_number": phone_number, "max_age_hours": max_age_hours},
                    headers=self.headers,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"device_swap_detected": data.get("device_swap_detected", False), "device_swap_date": data.get("last_swap_date"), "raw_response": data}
                logger.warning(f"Device swap API {resp.status_code}")
                return self._demo_device(phone_number)
        except Exception as e:
            logger.error(f"Device swap error: {e}")
            return self._demo_device(phone_number)

    def _demo_sim(self, phone: str) -> dict:
        if phone == SWAP_OCCURRED:
            return {"sim_swap_detected": True, "swap_date": "2025-04-28T14:30:00Z", "demo_mode": True}
        return {"sim_swap_detected": False, "swap_date": None, "demo_mode": True}

    def _demo_device(self, phone: str) -> dict:
        if phone == SWAP_OCCURRED:
            return {"device_swap_detected": True, "device_swap_date": "2025-04-28T14:35:00Z", "demo_mode": True}
        return {"device_swap_detected": False, "device_swap_date": None, "demo_mode": True}


camara_service = CamaraService()
