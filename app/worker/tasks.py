import asyncio
import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.worker.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.db.models import Change, SimulationRun, SimulationStatus

SAMPLE_LOG_PATH = "sample_data/traffic.jsonl"

def _load_sample_traffic() -> list[dict]:
    rows = []
    try:
        with open(SAMPLE_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    except FileNotFoundError:
        rows = [
            {"endpoint": "/login", "status": 200, "latency_ms": 120},
            {"endpoint": "/login", "status": 200, "latency_ms": 110},
            {"endpoint": "/login", "status": 429, "latency_ms": 80},
        ]
    return rows

def _simulate(change: Change, traffic: list[dict]) -> dict:

    base_total = len(traffic)
    base_fail = sum(1 for r in traffic if int(r["status"]) >= 400)
    base_fail_rate = base_fail / base_total if base_total else 0.0

    predicted_fail_rate = base_fail_rate
    latency_delta = 0

    for item in change.items:
        k = item.key.upper()
        if "RATE_LIMIT" in k or "RATELIMIT" in k:
            try:
                old = float(item.old_value)
                new = float(item.new_value)
                if new < old:
                    predicted_fail_rate += 0.05
            except ValueError:
                predicted_fail_rate += 0.02

        if "TIMEOUT" in k:
            try:
                old = float(item.old_value)
                new = float(item.new_value)
                if new < old:
                    predicted_fail_rate += 0.03
            except ValueError:
                predicted_fail_rate += 0.01

    predicted_fail_rate = min(predicted_fail_rate, 1.0)

    return {
        "base_fail_rate": round(base_fail_rate, 4),
        "predicted_fail_rate": round(predicted_fail_rate, 4),
        "predicted_latency_delta_ms": latency_delta,
        "sample_size": base_total,
        "assumptions": [
            "Rule-based simulation using in-repo sample traffic",
            "RATE_LIMIT tightening increases 429 probability",
            "TIMEOUT reduction increases 5xx probability",
        ],
    }

async def _run_simulation_async(change_id: UUID, sim_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        sim = await db.get(SimulationRun, sim_id)
        sim.status = SimulationStatus.running
        sim.updated_at = datetime.utcnow()
        await db.commit()

        stmt = select(Change).where(Change.id == change_id).options(selectinload(Change.items))
        res = await db.execute(stmt)
        change = res.scalar_one()

        traffic = _load_sample_traffic()
        report = _simulate(change, traffic)

        sim.report_json = json.dumps(report)
        sim.status = SimulationStatus.success
        sim.updated_at = datetime.utcnow()
        await db.commit()

@celery_app.task(name="run_simulation")
def run_simulation(change_id: str, sim_id: str) -> None:
    try:
        asyncio.run(_run_simulation_async(UUID(change_id), UUID(sim_id)))
    except Exception as e:

        async def _mark_failed():
            async with AsyncSessionLocal() as db:
                sim = await db.get(SimulationRun, UUID(sim_id))
                sim.status = SimulationStatus.failed
                sim.error_message = str(e)
                sim.updated_at = datetime.utcnow()
                await db.commit()
        asyncio.run(_mark_failed())
        raise
