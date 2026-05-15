# Bout Management

## Purpose

Bout management creates and exposes promoter-owned draft bouts with exactly two fighters and four planned escrows.

## Maintainer Map

- Routes: `backend/app/api/bouts.py`, `backend/app/api/bouts_routes/management_routes.py`
- Service: `backend/app/services/bout_service.py`
- Repository: `backend/app/repositories/bout_repository.py`
- Models/schemas: `backend/app/models/bout.py`, `backend/app/models/escrow.py`, `backend/app/schemas/bout.py`
- Frontend workflow: `frontend/src/hooks/useManagementWorkflow.ts`, `frontend/src/components/BoutWorkspacePanel.tsx`

## Runtime Flow

1. Promoter creates a draft bout through `POST /bouts`.
2. Backend verifies promoter role and both fighter profiles.
3. Backend plans four escrows: `show_a`, `show_b`, `bonus_a`, `bonus_b`.
4. Role-scoped list/detail endpoints expose only permitted bouts.

## Key Invariants

- Bout model is exactly 1v1.
- Each bout has exactly four planned escrows.
- Fighter A and Fighter B must be distinct fighter users.
- Draft creation must be atomic; invalid fighters or escrow planning must not leave partial records.

## Diagrams

```mermaid
flowchart TD
    promoter[Promoter JWT] --> create[POST /bouts]
    create --> fighters[Resolve fighter profiles]
    fighters --> plan[Plan four escrows]
    plan --> bout[(bouts: draft)]
    plan --> escrows[(escrows: planned x4)]
    bout --> list[GET /bouts]
    bout --> detail[GET /bouts/{id}]
```

## Tests

- `backend/tests/unit/test_bout_escrow_planning.py`
- `backend/tests/integration/test_bout_create_flow.py`
- `backend/tests/integration/test_management_endpoints.py`
- `frontend/src/App.test.tsx`
- `frontend/e2e/promoter-flow.spec.ts`

## Operational Notes

- Bout management is pre-ledger setup; no XRPL transaction is created by `POST /bouts`.
- Downstream escrow creation must still validate ledger evidence before changing lifecycle state.

## Canonical References

- `docs/api-spec.md`
- `docs/state-machines.md`
- `docs/schema-doc.md`
- `docs/requirements-matrix.md`
