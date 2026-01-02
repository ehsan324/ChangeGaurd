from uuid import UUID

from sqlalchemy import select, desc
from app.schemas.simulation_history import SimulationHistoryItem
from app.db.models import SimulationRun

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.change import ChangeCreate, ChangeRead, ApproveRequest, ChangeStatus
from app.services.change_service import ChangeService

from fastapi import HTTPException

from app.schemas.risk import RiskAssessmentRead, BlastRadius
from app.services.risk_service import RiskService
from app.services.risk_persistence_service import RiskPersistenceService
from app.services.audit_service import AuditService

import json
from datetime import datetime
from app.db.models import SimulationRun, SimulationStatus, ChangeStatus
from app.schemas.simulation import SimulationRunRead
from app.worker.tasks import run_simulation

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


@router.post("/{change_id}/simulate", status_code=202)
async def simulate_change(change_id: UUID, db: AsyncSession = Depends(get_db)):
    change = await ChangeService.get_change(db, change_id=change_id)

    if change.status != ChangeStatus.approved:
        raise HTTPException(status_code=409, detail="Change must be approved before simulation")

    sim = SimulationRun(change_id=change.id, status=SimulationStatus.queued, created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow())
    db.add(sim)
    await db.flush()

    await AuditService.write(
        db,
        actor=change.created_by,
        action="queue_simulation",
        resource_type="change",
        resource_id=str(change.id),
        metadata={"simulation_id": str(sim.id)},
    )

    await db.commit()

    run_simulation.delay(str(change.id), str(sim.id))

    return {"status": "queued", "simulation_id": str(sim.id)}


from sqlalchemy import select, desc

@router.get("/{change_id}/simulation", response_model=SimulationRunRead)
async def get_latest_simulation(change_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(SimulationRun)
        .where(SimulationRun.change_id == change_id)
        .order_by(desc(SimulationRun.created_at))
        .limit(1)
    )
    res = await db.execute(stmt)
    sim = res.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="No simulation found for this change")

    report = json.loads(sim.report_json) if sim.report_json else None
    return SimulationRunRead(
        id=sim.id,
        change_id=sim.change_id,
        status=sim.status,
        report=report,
        error_message=sim.error_message,
        created_at=sim.created_at,
        updated_at=sim.updated_at,
    )


@router.get("/{change_id}/simulations", response_model=list[SimulationHistoryItem])
async def list_simulations(change_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(SimulationRun)
        .where(SimulationRun.change_id == change_id)
        .order_by(desc(SimulationRun.created_at))
    )
    res = await db.execute(stmt)
    sims = res.scalars().all()

    return [
        SimulationHistoryItem(
            id=s.id,
            status=s.status,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sims
    ]
