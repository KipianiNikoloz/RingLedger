## Why

M4 hardening is complete for the locked MVP/Testnet scope, but the project still needs a release-readiness slice that proves the documented local and CI evidence can be carried into an operator-run XRPL Testnet deployment. This change creates the release evidence, smoke-validation procedure, and bounded readiness criteria needed before treating the MVP as deployable.

## What Changes

- Add a Testnet release-readiness capability covering preflight evidence, live Xaman/API-mode validation, XRPL Testnet smoke expectations, and release scope boundaries.
- Update operational documentation with a concrete Testnet release checklist and evidence capture expectations.
- Capture current verification evidence for backend, frontend, OpenSpec, and release-smoke gates without expanding the locked MVP feature scope.
- Preserve deterministic local/CI behavior by keeping stub-mode Xaman checks separate from live release smoke validation.

## Capabilities

### New Capabilities

- `testnet-release-readiness`: Defines the documentation, gate, and smoke-validation evidence required to mark the locked MVP ready for XRPL Testnet release.

### Modified Capabilities

- None.

## Impact

- Documentation: `README.md`, `docs/operations-runbook.md`, `docs/traceability-matrix.md`, and a release readiness memo.
- OpenSpec: new change artifacts and a new `testnet-release-readiness` capability spec.
- Validation: existing backend/frontend/OpenSpec gates plus a documented manual live-smoke path for Xaman API mode and XRPL Testnet confirmation evidence.
- No API, schema, state-machine, dependency, or product-scope changes are intended.
