import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditLog

class AuditService:
    @staticmethod
    async def write(
            db: AsyncSession,
            *,
            actor: str,
            action: str,
            resource_type: str,
            resource_id: str,
            metadata: dict | None = None,
    ) -> None:
        entry = AuditLog(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=json.dumps(metadata) if metadata else None,

        )
        db.add(entry)