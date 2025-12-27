# Architecture

## Components
- **API (FastAPI, async)**: handles requests, enforces state machine, stores records, enqueues jobs.
- **PostgreSQL**: source of truth (changes, items, simulations, rollouts, audit logs).
- **Redis**: Celery broker + distributed locks.
- **Celery worker**: runs simulations and rollout steps asynchronously.

## Change lifecycle (high level)
draft → approved → simulated → applying → applied
                       ↘
                     rolled_back

## Key engineering properties
- **State machine**: disallow invalid transitions.
- **Idempotency**: `apply` is safe to retry via Idempotency-Key.
- **Concurrency control**: Redis lock prevents simultaneous apply for a change.
- **Auditability**: every action emits an immutable audit log record.
- **Observability**: structured logs + Prometheus metrics for critical operations.

## Flows
### Create & Approve
(Describe Flow A)

### Assess & Simulate
(Describe Flow B)

### Apply (Rollout)
(Describe Flow C)

### Rollback
(Describe Flow D)
