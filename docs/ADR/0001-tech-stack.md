# ADR-0001: Technology stack

## Context
We need a small internal service that exposes an API, persists change history,
runs long-running jobs (simulation/rollout), and provides observability.

## Decision
- FastAPI (async) for the API layer
- PostgreSQL as the system of record
- Redis for Celery broker and distributed locks
- Celery worker for asynchronous jobs
- Prometheus metrics + structured JSON logging
- pytest for testing

## Rationale
- Async API improves I/O concurrency for DB and external calls.
- PostgreSQL provides strong consistency and reliable query capabilities.
- Celery isolates long-running tasks from request/response lifecycle.
- Redis is a pragmatic choice for both broker and locks.

## Consequences
- We introduce an extra process (worker) and operational complexity (compose),
  but gain production-like separation of concerns.
