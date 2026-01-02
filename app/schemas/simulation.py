from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class SimulationRunRead(BaseModel):
    id: UUID
    change_id: UUID
    status: str
    report: dict | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
