# RingLedger

Escrow-based fighter purse settlement on XRPL Testnet, with promoter signing via Xaman and backend-enforced lifecycle/security invariants.

## Status

- Baseline product and technical documentation are in place.
- Backend/database M1 foundation is complete with executable unit/integration/property/contract/security/migration tests.
- M2 escrow create prepare/confirm flow is implemented with validated XRPL confirmation checks and confirm-endpoint idempotency.
- M3 result entry + payout prepare/confirm flow is implemented with JWT role guards, payout idempotency, timing guards, and winner-bonus fulfillment validation.
- Mandatory pre-closeout architecture hardening is implemented: lightweight Unit of Work + selective repositories, with no API/state-machine semantic changes.
- Mandatory pre-closeout modernization is implemented: Alembic migration authority + proven auth-library adoption, with no unapproved contract drift.
- M4 hardening has started with backend Xaman sign-request integration for non-custodial promoter signing flows.

## MVP Scope (Locked)

- Stack: FastAPI (Python), PostgreSQL, React, XRPL Testnet, Xaman.
- Auth: email/password + JWT only (no wallet login).
- Money: XRP only, amounts in drops (integers), DB `BIGINT`.
- Bout model: 1v1 with 4 escrows: `show_a`, `show_b`, `bonus_a`, `bonus_b`.
- Custody split: platform controls bonus preimage/fulfillment; promoter controls signatures.
- Signing: promoter signs in Xaman; backend never stores promoter private keys.
- Timing: `FinishAfter = event_datetime_utc + 2h`; `CancelAfter = event_datetime_utc + 7d` (bonus only).
- Ledger truth: state transitions only after validated XRPL `tesSUCCESS`.
- Idempotency: required on confirm endpoints.
- Security: frontend untrusted, backend authoritative for all invariants.

## Core Docs

- Requirements baseline: `docs/requirements-matrix.md`
- Lifecycle contract: `docs/state-machines.md`
- Requirement traceability: `docs/traceability-matrix.md`
- CI/CD and dependency automation: `docs/ci-cd.md`
- Clean architecture refactor plan: `docs/clean-architecture-refactor-plan.md`
- Alembic adoption plan: `docs/alembic-adoption-plan.md`
- Auth-library adoption plan: `docs/auth-library-adoption-plan.md`
- M3.6 modernization acceptance memo: `docs/m3.6-modernization-acceptance-memo.md`
- Xaman signing contract: `docs/xaman-signing-contract.md`

## Repository Layout

- `backend/`: FastAPI service scaffold, domain modules, SQL schema, and initial test suite.
- `docs/`: locked requirements, state machines, and implementation traceability.
- `.github/`: CI/CD workflow and Dependabot automation.

## Implementation Roadmap (Current)

1. M1: backend + database foundation (`R-02`, `R-03`, `R-04`, `R-07`) - complete.
2. M2: escrow create prepare/confirm with XRPL validation + idempotency - complete.
3. M3: result entry and payout prepare/confirm with bonus fulfillment logic - complete.
4. M3.5 (mandatory): clean architecture hardening of persistence boundaries (Unit of Work + selective repositories) with behavior parity proof - complete.
5. M3.6 (mandatory): migration/auth modernization (Alembic authority + proven auth library) with parity proof - complete.
6. M4: hardening closeout (security, failure paths, regression/performance, operational readiness) - in progress.

## Delivery Rules

- Implement in small vertical slices with atomic commits.
- Every code/config/schema change must include matching tests and documentation updates.
- Maintain traceability: requirement -> implementation -> tests -> docs.

## Automation

- CI/CD workflow enforces compile checks, formatting, linting, tests, and secret scanning.
- Delivery artifact is generated on successful pushes to `main`/`master`.
- Dependabot opens weekly PRs for GitHub Actions and Python dependency updates.
