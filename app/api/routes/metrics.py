from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import SimulationRun, SimulationStatus

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count()).select_from(SimulationRun))
    success = await db.scalar(
        select(func.count()).where(SimulationRun.status == SimulationStatus.success)
    )
    failed = await db.scalar(
        select(func.count()).where(SimulationRun.status == SimulationStatus.failed)
    )

    return {
        "simulations_total": total or 0,
        "simulations_success": success or 0,
        "simulations_failed": failed or 0,
    }
