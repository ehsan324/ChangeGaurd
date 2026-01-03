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
5) Keep a full audit trail

## MVP scope
- Async FastAPI API + PostgreSQL + Redis + Celery worker
- Change lifecycle state machine
- Rule-based risk scoring
- Simulation against sample traffic logs (in-repo)
- Idempotency + concurrency locks

## Quick demo (target)
```bash
# create change
curl -s -X POST http://localhost:8000/changes \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Tighten login rate limit",
    "description":"Reduce brute-force risk",
    "environment":"prod",
    "created_by":"cj",
    "items":[
      {"key":"LOGIN_RATE_LIMIT_PER_MINUTE","old_value":"10","new_value":"3"}
    ]
  }'


# approve
curl -s -X POST http://localhost:8000/changes/CHANGE_ID/approve \
  -H "Content-Type: application/json" \
  -d '{"actor":"cj"}'

# assess
curl -s -X POST http://localhost:8000/changes/CHANGE_ID/assess

# simulate
curl -s http://localhost:8000/changes/CHANGE_ID/simulation

# history
curl -s http://localhost:8000/changes/CHANGE_ID/simulations

```
## Observability & Operations

The system provides basic operational visibility out of the box:

- `/metrics` endpoint exposes system-level counters
- Structured JSON logs for all simulation lifecycle events
- Simulation history per change for traceability
- Audit logs for all state transitions

This design allows easy integration with monitoring systems such as
Prometheus, ELK stack, or cloud-native logging platforms.
