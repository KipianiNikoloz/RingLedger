# RingLedger Clean Architecture Refactor Plan (Mandatory Pre-M4 Closeout)

Last updated: 2026-02-21

## Status

- Implemented.
- Verified with lint, formatting, unit, integration, and security suite parity checks.

## Purpose

Define the mandatory persistence-architecture hardening increment that must complete before M4 closeout.

This is a maintainability/safety refactor. It is not a feature expansion.

## Scope

- Standardize transaction ownership with a lightweight Unit of Work.
- Apply Unit of Work boundaries to transactional backend flows:
  - bout draft creation
  - result entry
  - escrow create confirm
  - payout confirm
- Introduce selective repositories only where duplicated data-access logic is reduced:
  - `Bout`
  - `Escrow`
  - `IdempotencyKey`
  - `AuditLog`
- Keep persistence of transition + audit + idempotency artifact atomic in confirm flows.

## Non-Goals

- No API endpoint additions, removals, or path changes.
- No request/response schema changes.
- No lifecycle state-machine semantic changes.
- No changes to MVP constraints (`R-01`..`R-12`).
- No generic repository-per-table CRUD abstraction.

## Context Driving This Refactor

- Transaction ownership was split across layers (pre-refactor):
  - service-level commits in `backend/app/services/auth_service.py` and `backend/app/services/bout_service.py`
  - route-level commits in `backend/app/api/bouts.py`
- `backend/app/api/bouts.py` carried duplicated confirm orchestration, idempotency, and commit logic.
- Query/state-loading logic was repeated across:
  - `backend/app/services/escrow_service.py`
  - `backend/app/services/payout_service.py`

## Implementation Sequence

1. Define Unit of Work contract and ownership boundaries for create/result/confirm use cases.
2. Centralize transaction handling under Unit of Work where currently split across router/services.
3. Extract selective repositories for duplicated data-access paths (`Bout`, `Escrow`, `IdempotencyKey`, `AuditLog`).
4. Preserve behavior parity with regression, failure-path, and idempotency consistency tests.
5. Update documentation and traceability artifacts in the same increment.

## Acceptance Evidence

- Unit tests for Unit of Work ownership and selective repository contracts.
- Integration tests proving atomic transition + audit + idempotency persistence.
- Regression/security/failure-path tests proving no guard or state-machine drift.
- API spec and state-machine docs explicitly unchanged in semantics.
- Traceability matrix updated with requirement links and evidence.

## Required Gates Before Closeout

- `agents/14-clean-code-architecture/QUALITY_GATES.md` is green.
- Program orchestrator closeout gate confirms mandatory architecture step completion.
- Backend/database/testing owners accept handoff completeness.
