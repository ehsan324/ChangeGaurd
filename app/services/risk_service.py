import json
from dataclasses import dataclass
from typing import Any

from app.db.models import Change


@dataclass
class RiskResult:
    score: int
    level: str
    blast_radius: dict[str, Any]
    reasons: list[str]


class RiskService:
    @staticmethod
    def assess(change: Change) -> RiskResult:
        score = 0
        reasons: list[str] = []

        affected_components: set[str] = set()
        affected_endpoints: set[str] = set()
        notes: list[str] = []

        if change.environment == "prod":
            score += 20
            reasons.append("environment: prod (+20)")

        for item in change.items:
            key = item.key.upper()

            if key.startswith("LOGIN_") or "AUTH" in key:
                affected_components.add("auth")
                affected_endpoints.add("/login")
                score += 40
                reasons.append(f"{item.key} affects auth/login (+40)")

            if "PAYMENT" in key:
                affected_components.add("payments")
                affected_endpoints.add("/payments")
                score += 45
                reasons.append(f"{item.key} affects payments (+45)")

            if "TIMEOUT" in key:
                affected_components.add("performance")
                score += 15
                reasons.append(f"{item.key} changes timeout (+15)")

            if "RATE_LIMIT" in key or "RATELIMIT" in key:
                affected_components.add("rate-limiting")
                score += 20
                reasons.append(f"{item.key} changes rate limiting (+20)")

            mag_score, mag_reason = RiskService._magnitude_score(item.old_value, item.new_value)
            if mag_score:
                score += mag_score
                reasons.append(mag_reason)
        if len(change.items) >= 3:
            score += 10
            reasons.append("Change includes 3+ items (+10)")

        score = max(0, min(score, 100))

        level = "LOW"
        if score >= 70:
            level = "HIGH"
        elif score >= 40:
            level = "MEDIUM"

        blast_radius = {
            "affected_components": sorted(affected_components),
            "affected_endpoints": sorted(affected_endpoints),
            "notes": notes,
        }

        return RiskResult(score=score, level=level, blast_radius=blast_radius, reasons=reasons)

    @staticmethod
    def _magnitude_score(old: str, new: str) -> tuple[int, str]:
        try:
            old_num = float(old)
            new_num = float(new)
        except ValueError:
            return 0, ""

        # percent change
        if old_num == 0:
            return 5, f"Magnitude changed from 0 to {new_num} (+5)"

        delta = abs(new_num - old_num) / abs(old_num)

        if delta >= 0.5:
            return 25, f"Magnitude change is large ({old_num}→{new_num}) (+25)"
        if delta >= 0.2:
            return 15, f"Magnitude change is moderate ({old_num}→{new_num}) (+15)"
        if delta >= 0.1:
            return 8, f"Magnitude change is small ({old_num}→{new_num}) (+8)"
        return 0, ""
