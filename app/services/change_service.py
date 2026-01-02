from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Change, ChangeItem, ChangeStatus
from app.services.audit_service import AuditService


class ChangeService:
    @staticmethod
    async def create_change(db: AsyncSession, *, data) -> Change:
        change = Change(
            title=data.title,
            description=data.description,
            environment=data.environment,
            status=ChangeStatus.draft,
            created_by=data.created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # items
        change.items = [
            ChangeItem(
                key=item.key,
                old_value=item.old_value,
                new_value=item.new_value,
            )
            for item in data.items
        ]

        db.add(change)

        await db.flush()

        await AuditService.write(
            db,
            actor=data.created_by,
            action="create_change",
            resource_type="change",
            resource_id=str(change.id),
            metadata={"environment": change.environment, "items_count": len(change.items)},
        )

        await db.commit()
        return await ChangeService.get_change(db, change_id=change.id)

    @staticmethod
    async def get_change(db: AsyncSession, change_id: UUID) -> Change:
        stmt = (
            select(Change)
            .where(Change.id == change_id)
            .options(selectinload(Change.items))
        )
        result = await db.execute(stmt)
        change = result.scalar_one_or_none()
        if not change:
            raise HTTPException(status_code=404, detail="Change not found")
        return change

    @staticmethod
    async def approve_change(db: AsyncSession, *, change_id: UUID, actor: str) -> Change:
        change = await ChangeService.get_change(db, change_id)

        if change.status != ChangeStatus.draft:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot approve change in status '{change.status}'. Expected 'draft'.",
            )

        change.status = ChangeStatus.approved
        change.updated_at = datetime.utcnow()

        await AuditService.write(
            db,
            actor=actor,
            action="approve_change",
            resource_type="change",
            resource_id=str(change.id),
            metadata={"from": "draft", "to": "approved"},
        )

        await db.commit()
        return await ChangeService.get_change(db, change_id=change.id)

