"""Agentic AI — Claude via Anthropic. Key from env only."""
import json
import logging
from typing import Dict, Any
from anthropic import Anthropic
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are SimGuard AI, a fraud detection agent for African mobile money. "
    "Analyze transaction data and CAMARA API results. "
    'Respond with ONLY valid JSON (no markdown, no code fences): '
    '{"decision":"BLOCK"|"FLAG"|"APPROVE","confidence":0.0-1.0,'
    '"explanation":"1-2 sentences for the agent",'
    '"recommended_actions":["action1"],"risk_factors":["factor1"],'
    '"urgency":"immediate"|"high"|"normal"} '
    "Rules: BLOCK if SIM swap + high value OR score >= 80. "
    "FLAG if score 35-79. APPROVE if score < 35. "
    "Consider African mobile money fraud patterns. "
    "When uncertain, FLAG rather than APPROVE."
)


class AIEngine:
    def __init__(self):
        self.client = None
        if settings.anthropic_api_key and settings.anthropic_api_key.startswith("sk-ant-"):
            try:
                self.client = Anthropic(api_key=settings.anthropic_api_key)
            except Exception as e:
                logger.error(f"Claude init failed: {e}")

    async def analyze(self, transaction: Dict, camara: Dict, risk: Dict) -> Dict:
        if not self.client:
            return self._fallback(risk)

        prompt = (
            f"Transaction: {transaction.get('phone_number')} "
            f"{transaction.get('currency', 'USD')}{transaction.get('amount', 0):.2f} "
            f"type={transaction.get('transaction_type')} "
            f"recipient={transaction.get('recipient', 'N/A')} "
            f"new_recipient={transaction.get('is_new_recipient')} "
            f"CAMARA: SIM_swap={'DETECTED' if camara.get('sim_swap', {}).get('sim_swap_detected') else 'none'} "
            f"swap_date={camara.get('sim_swap', {}).get('swap_date', 'N/A')} "
            f"Device_swap={'DETECTED' if camara.get('device_swap', {}).get('device_swap_detected') else 'none'} "
            f"Number_verified={camara.get('number_verification', {}).get('verified', True)} "
            f"Rule score: {risk['score']}/100+ level={risk['risk_level']} "
            f"flags={','.join(risk['flags']) if risk['flags'] else 'none'}"
        )

        try:
            resp = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text.strip()
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:])
            if raw.endswith("```"):
                raw = raw[:-3]
            result = json.loads(raw.strip())
            result.setdefault("decision", risk["preliminary_decision"])
            result.setdefault("confidence", 0.7)
            result.setdefault("explanation", "Analysis complete.")
            result.setdefault("recommended_actions", [])
            result.setdefault("risk_factors", risk["flags"])
            result.setdefault("urgency", "normal")
            result["decision"] = result["decision"].upper()
            if result["decision"] not in ("BLOCK", "APPROVE", "FLAG"):
                result["decision"] = risk["preliminary_decision"]
            result["ai_model"] = "claude-sonnet-4"
            return result
        except Exception as e:
            logger.error(f"AI error: {e}")
            return self._fallback(risk)

    def _fallback(self, risk: Dict) -> Dict:
        lvl = risk["risk_level"]
        exps = {
            "critical": f"CRITICAL ({risk['score']}). Multiple fraud indicators. Block immediately.",
            "high": f"HIGH ({risk['score']}). Suspicious patterns. Verification required.",
            "medium": f"MEDIUM ({risk['score']}). Some concerns. Verify identity.",
            "low": f"LOW ({risk['score']}). No significant indicators. Safe to process.",
        }
        recs = {
            "critical": ["Do NOT process", "Contact customer via known number", "Report to fraud team"],
            "high": ["Call customer on known number", "Request in-person ID verification"],
            "medium": ["Ask customer to verify identity", "Confirm recipient details"],
            "low": ["Proceed with standard processing"],
        }
        return {
            "decision": risk["preliminary_decision"],
            "confidence": 0.8,
            "explanation": exps.get(lvl, exps["low"]),
            "recommended_actions": recs.get(lvl, recs["low"]),
            "risk_factors": risk["flags"],
            "urgency": "immediate" if lvl in ("critical", "high") else "normal",
            "ai_model": "rule-based-fallback",
            "fallback": True,
        }


ai_engine = AIEngine()
