"""Rule-based fraud scoring."""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
HIGH_VALUE = 500.0
VERY_HIGH_VALUE = 1000.0


def calculate_risk_score(transaction: Dict[str, Any], camara: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    flags = []
    breakdown = {}

    if camara.get("sim_swap", {}).get("sim_swap_detected"):
        score += 60; flags.append("SIM_SWAP_24H")
    breakdown["sim_swap_24h"] = 60 if "SIM_SWAP_24H" in flags else 0

    if camara.get("device_swap", {}).get("device_swap_detected"):
        score += 30; flags.append("DEVICE_SWAP")
    breakdown["device_swap"] = 30 if "DEVICE_SWAP" in flags else 0

    nv = camara.get("number_verification", {})
    if nv and not nv.get("verified"):
        score += 25; flags.append("NUMBER_MISMATCH")
    breakdown["number_mismatch"] = 25 if "NUMBER_MISMATCH" in flags else 0

    amount = transaction.get("amount", 0)
    if amount > VERY_HIGH_VALUE:
        score += 30; flags.append("VERY_HIGH_VALUE")
    elif amount > HIGH_VALUE:
        score += 20; flags.append("HIGH_VALUE")
    breakdown["high_value"] = 30 if "VERY_HIGH_VALUE" in flags else (20 if "HIGH_VALUE" in flags else 0)

    if transaction.get("is_new_recipient"):
        score += 15; flags.append("NEW_RECIPIENT")
    breakdown["new_recipient"] = 15 if "NEW_RECIPIENT" in flags else 0

    if "SIM_SWAP_24H" in flags and amount > HIGH_VALUE:
        score += 25; flags.append("SIM_SWAP_PLUS_HIGH_VALUE")
    if "SIM_SWAP_24H" in flags and "NEW_RECIPIENT" in flags:
        score += 20; flags.append("SIM_SWAP_PLUS_NEW_RECIPIENT")
    if "DEVICE_SWAP" in flags and "NUMBER_MISMATCH" in flags:
        score += 20; flags.append("DEVICE_PLUS_NUMBER_MISMATCH")
    if "SIM_SWAP_24H" in flags and "DEVICE_SWAP" in flags:
        score += 15; flags.append("FULL_TAKEOVER")

    if score >= 80:
        level, decision = "critical", "BLOCK"
    elif score >= 60:
        level, decision = "high", "FLAG"
    elif score >= 35:
        level, decision = "medium", "FLAG"
    else:
        level, decision = "low", "APPROVE"

    return {"score": score, "risk_level": level, "flags": flags, "breakdown": breakdown, "preliminary_decision": decision}


def get_alert_type(flags: list) -> str:
    if "FULL_TAKEOVER" in flags or "SIM_SWAP_PLUS_HIGH_VALUE" in flags:
        return "composite"
    if "SIM_SWAP_24H" in flags:
        return "sim_swap"
    if "DEVICE_SWAP" in flags:
        return "device_swap"
    if "NUMBER_MISMATCH" in flags:
        return "number_mismatch"
    return "sim_swap"
