## Why

The MVP role journeys still depend on manual database setup for fighter profiles and bout drafts. Adding the planned management endpoints closes that product gap so operators can create and inspect lifecycle-ready bouts through the API instead of test fixtures.

## What Changes

- Add authenticated fighter profile upsert for `PUT /fighters/me`.
- Add promoter-only bout draft creation for `POST /bouts` using the existing four-escrow planning service.
- Add authenticated bout list/detail reads for `GET /bouts` and `GET /bouts/{id}` with role-scoped visibility.
- Update API, traceability, README, and frontend-facing client contracts to remove the stale "planned next endpoints" gap.
- Add backend and frontend contract coverage for the new management surface.

## Capabilities

### New Capabilities
- `mvp-management-endpoints`: fighter profile management and role-scoped bout create/read APIs for the MVP lifecycle.

### Modified Capabilities
- `operator-console-interface`: expose the new profile and bout management calls through the operator workspace while preserving existing lifecycle controls.

## Impact

- Backend API routes, schemas, services, and repositories for fighter profiles and bout reads.
- Backend contract/security/integration tests covering authz, validation, four-escrow planning, and role-scoped reads.
- Frontend API client, workflow state, operator UI controls, unit tests, and browser journey coverage.
- Documentation and traceability status for M4 closeout readiness.
