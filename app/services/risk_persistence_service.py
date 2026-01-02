import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RiskAssessment
from app.services.risk_service import RiskResult


class RiskPersistenceService:
    @staticmethod
    async def save(db: AsyncSession, *, change_id, result: RiskResult) -> RiskAssessment:
        ra = RiskAssessment(
            change_id=change_id,
            score=result.score,
            level=result.level,
            blast_radius_json=json.dumps(result.blast_radius),
            reasoning_json=json.dumps(result.reasons),
        )
        db.add(ra)
        await db.flush()
        return ra
