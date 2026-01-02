from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.change import ChangeCreate, ChangeRead, ApproveRequest, ChangeStatus
from app.services.change_service import ChangeService

import json
from fastapi import HTTPException

from app.schemas.risk import RiskAssessmentRead, BlastRadius
from app.services.risk_service import RiskService
from app.services.risk_persistence_service import RiskPersistenceService
from app.services.audit_service import AuditService


router = APIRouter(prefix="/changes", tags=["changes"])


@router.post("/", response_model=ChangeRead, status_code=201)
async def create_change(payload: ChangeCreate, db: AsyncSession = Depends(get_db)):
    change = await ChangeService.create_change(db, data=payload)
    return change


@router.get("/{change_id}", response_model=ChangeRead)
async def get_change(change_id: UUID, db: AsyncSession = Depends(get_db)):
    change = await ChangeService.get_change(db, change_id=change_id)
    return change


@router.post("/{change_id}/approve", response_model=ChangeRead)
async def approve_change(
        change_id: UUID,
        payload: ApproveRequest,
        db: AsyncSession = Depends(get_db),
):
    change = await ChangeService.approve_change(db, change_id=change_id, actor=payload.actor)
    return change


@router.post("/{change_id}/assess", response_model=RiskAssessmentRead)
async def assess_change(change_id: UUID, db: AsyncSession = Depends(get_db)):
    change = await ChangeService.get_change(db, change_id=change_id)

    if change.status not in (ChangeStatus.approved, ChangeStatus.draft):
        raise HTTPException(status_code=409, detail=f"Cannot assess in status {change.status}")

    result = RiskService.assess(change)

    ra = await RiskPersistenceService.save(db, change_id=change.id, result=result)

    await AuditService.write(
        db,
        actor=change.created_by,
        action="assess_risk",
        resource_type="change",
        resource_id=str(change.id),
        metadata={"score": result.score, "level": result.level},
    )

    await db.commit()

    return RiskAssessmentRead(
        id=ra.id,
        change_id=ra.change_id,
        score=ra.score,
        level=ra.level,
        blast_radius=BlastRadius(**json.loads(ra.blast_radius_json)),
        reasoning=json.loads(ra.reasoning_json),
        created_at=ra.created_at,
    )
