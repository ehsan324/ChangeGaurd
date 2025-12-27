# ChangeGuard

Production outages are often caused not only by bugs, but by unsafe configuration changes.
**ChangeGuard** is an internal service for managing configuration/feature changes with:
- risk assessment (blast radius + scoring)
- dry-run simulation
- safe rollout (canary/gradual)
- audit logging and observability

## What problem does it solve?
Teams frequently change values like timeouts, rate limits, cache TTLs, and feature flags.
Without disciplined change management, a small change can cause broad impact.

ChangeGuard introduces a workflow:
1) Create a change (draft)
2) Approve it
3) Assess risk + blast radius
4) Simulate expected impact
5) Apply via staged rollout
6) Roll back safely if needed
7) Keep a full audit trail

## MVP scope
- Async FastAPI API + PostgreSQL + Redis + Celery worker
- Change lifecycle state machine
- Rule-based risk scoring
- Simulation against sample traffic logs (in-repo)
- Rollout steps (e.g., 5% → 25% → 100%)
- Idempotency + concurrency locks
- Structured logs + Prometheus metrics

## Quick demo (target)
```bash
# create change
curl -X POST ... /changes

# approve
curl -X POST ... /changes/{id}/approve

# assess
curl -X POST ... /changes/{id}/assess

# simulate
curl -X POST ... /changes/{id}/simulate

# apply
curl -X POST ... /changes/{id}/apply -H "Idempotency-Key: ..."

# rollback
curl -X POST ... /changes/{id}/rollback
