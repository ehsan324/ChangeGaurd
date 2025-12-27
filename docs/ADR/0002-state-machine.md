# ADR-0002: Change state machine

## Context
A change must follow a safe workflow. Invalid transitions (e.g., applying an unapproved change)
should be prevented at the system level to guarantee correctness.

## Decision
We model Change as a state machine with allowed transitions:
- draft → approved
- approved → simulated
- simulated → applying
- applying → applied
- applied → rolled_back
Additionally, rejected is allowed from draft/approved if needed.

## Rationale
- Encodes business rules explicitly and prevents inconsistent states.
- Simplifies reasoning for operators and reviewers.
- Makes audit logs and metrics easier to interpret.

## Consequences
- Some flows become stricter (must approve before simulate/apply),
  but the system becomes safer and easier to operate.
