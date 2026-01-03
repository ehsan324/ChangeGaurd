import hashlib
import json
from typing import Any

from fastapi import Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IdempotencyRecord


async def check_idempotency(
    request: Request,
    db: AsyncSession,
) -> IdempotencyRecord | dict[str, str] | None:

    idempotency_key = request.headers.get("Idempotency-Key")

    if not idempotency_key:
        return None

    endpoint = request.url.path

    body_bytes = await request.body()
    request_hash = hashlib.sha256(body_bytes).hexdigest()

    stmt = select(IdempotencyRecord).where(
        IdempotencyRecord.key == idempotency_key,
        IdempotencyRecord.endpoint == endpoint,
    )
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if record:
        if record.request_hash != request_hash:
            raise HTTPException(
                status_code=409,
                detail="Idempotency-Key was reused with a different request body",
            )
        return record

    return {"key": idempotency_key, "endpoint": endpoint, "request_hash": request_hash}


async def store_idempotency_response(
    db: AsyncSession,
    *,
    key: str,
    endpoint: str,
    request_hash: str,
    response_payload: dict[str, Any],
    status_code: int,
) -> None:
    record = IdempotencyRecord(
        key=key,
        endpoint=endpoint,
        request_hash=request_hash,
        response_json=json.dumps(response_payload),
        status_code=status_code,
    )
    db.add(record)
