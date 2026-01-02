from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class BlastRadius(BaseModel):
    affected_components: list[str]
    affected_endpoints: list[str]
    notes: list[str]


class RiskAssessmentRead(BaseModel):
    id: UUID
    change_id: UUID
    score: int
    level: str
    blast_radius: BlastRadius
    reasoning: list[str]
    created_at: datetime
