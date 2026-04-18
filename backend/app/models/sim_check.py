"""SimCheck model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base


class SimCheck(Base):
    __tablename__ = "sim_checks"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    sim_swap_detected = Column(Boolean, default=False)
    swap_date = Column(String(50), nullable=True)
    device_swap_detected = Column(Boolean, default=False)
    device_swap_date = Column(String(50), nullable=True)
    number_verified = Column(Boolean, nullable=True)
    check_results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
