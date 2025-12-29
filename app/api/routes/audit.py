from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import AuditLog
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/changes/{change_id}", response_model=list[AuditLogRead])
async def list_change_audits(change_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(AuditLog)
        .where(AuditLog.resource_type == "change", AuditLog.resource_id == change_id)
        .order_by(AuditLog.created_at.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()
