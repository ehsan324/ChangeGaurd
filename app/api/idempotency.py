import hashlib
import json
from fastapi import Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IdempotencyRecord

async def check_idempotency(
    request: Request,
    db: AsyncSession,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if not idempotency_key:
        return None

    endpoint = request.url.path

    body = await request.body()
    request_hash = hashlib.sha256(body).hexdigest()

    stmt = select(IdempotencyRecord).where(
        IdempotencyRecord.key == idempotency_key,
        IdempotencyRecord.endpoint == endpoint,
    )
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if record:
        # same key used before; ensure body matches
        if record.request_hash != request_hash:
            raise HTTPException(status_code=409, detail="Idempotency key reuse with different payload")
        return record

    return {"key": idempotency_key, "endpoint": endpoint, "request_hash": request_hash}

async def store_idempotency_response(
    db: AsyncSession,
    *,
    key: str,
    endpoint: str,
    request_hash: str,
    response_json: dict,
    status_code: int,
):
    record = IdempotencyRecord(
        key=key,
        endpoint=endpoint,
        request_hash=request_hash,
        response_json=json.dumps(response_json),
        status_code=status_code,
    )
    db.add(record)
