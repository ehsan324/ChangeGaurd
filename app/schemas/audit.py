from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: UUID
    actor: str
    action: str
    resource_type: str
    resource_id: str
    metadata_json: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
