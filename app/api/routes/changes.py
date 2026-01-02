from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.change import ChangeCreate, ChangeRead, ApproveRequest
from app.services.change_service import ChangeService

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
