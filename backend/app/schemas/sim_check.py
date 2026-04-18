"""Sim check schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SimSwapStatusResponse(BaseModel):
    phone_number: str
    sim_swap_detected: bool
    swap_date: Optional[str]
    checked_at: datetime


class DeviceSwapStatusResponse(BaseModel):
    phone_number: str
    device_swap_detected: bool
    device_swap_date: Optional[str]
    checked_at: datetime
