# RingLedger Auth Library Adoption Plan (Mandatory Pre-M4 Closeout)

Last updated: 2026-02-21

## Purpose

Define the mandatory auth modernization step to replace bespoke auth primitives with a proven maintained library.

This is maintainability/safety hardening, not feature expansion.

## Scope

- Migrate from bespoke auth token/password primitives to a proven maintained auth library.
- Preserve locked auth constraints:
  - email/password plus JWT only.
  - wallet login remains forbidden.
- Preserve role-guard, idempotency, and lifecycle behavior contracts.
- Define objective selection criteria and acceptance evidence for the library decision.

## Non-Goals

- No auth mode expansion beyond email/password plus JWT.
- No API contract changes unless explicitly versioned and documented.
- No lifecycle semantic changes.
- No changes to custody, ledger, or idempotency invariants.

## Current-State Baseline

- Auth implementation is currently bespoke in:
  - `backend/app/core/security.py`
  - `backend/app/services/auth_service.py`
  - `backend/app/api/auth.py`
- Existing endpoint behavior and role-guard contracts are already test-covered and must be preserved.

## Objective Library Selection Criteria

- Maintenance cadence: active release history and maintainers with recent updates.
- Security posture: disclosed vulnerability handling process and acceptable CVE history.
- Framework compatibility: FastAPI/Pydantic ecosystem compatibility and JWT support.
- Password security quality: strong hashing defaults and migration support.
- Testability: straightforward integration with unit/integration/security test suites.
- Migration safety: low-risk transition path preserving existing API/auth contracts.

## Sequence

1. Baseline existing auth contracts and security controls.
2. Evaluate candidate libraries using objective criteria scorecard.
3. Select library and define migration plan with parity safeguards.
4. Define regression/security test matrix for auth behavior parity.
5. Update CI/CD and traceability documentation with acceptance evidence.

## Acceptance Evidence

- Candidate evaluation matrix and selected-library rationale.
- Auth regression coverage for register/login/token/role guards/failure cases.
- Security regression coverage for authz/replay/secret leakage behavior.
- API contract stability statement and traceability updates.
- Residual risk statement with owner.

## Rollback Strategy

- Technical rollback: revert to prior auth implementation path behind controlled release rollback procedure.
- Operational rollback: halt rollout, revoke affected tokens per runbook, restore last known good auth path.
- Documentation rollback: record rollback trigger, impact, and corrective actions in traceability and security records.

