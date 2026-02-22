# RingLedger MVP Traceability Matrix

Date initialized: 2026-02-16  
Last updated: 2026-02-22  
Purpose: enforce requirement -> implementation -> tests -> docs linkage from first increment.

## Status Legend

- `planned`: implementation target defined but not coded yet.
- `in_progress`: slice active.
- `done`: implemented, tested, documented.

## Requirement Traceability

| Req ID | Requirement Summary | Planned Implementation Targets | Planned Test Targets | Documentation Targets | Status |
|---|---|---|---|---|---|
| R-01 | Fixed stack and integration boundaries | `backend/app/main.py`, `backend/app/api/router.py`, `backend/app/db/session.py`, `.github/workflows/ci-cd.yml`, `frontend/src/main.tsx` (pending), XRPL/Xaman integrations (pending) | `backend/tests/integration/test_stack_bootstrap.py` | `docs/requirements-matrix.md`, `docs/state-machines.md`, `backend/README.md`, `docs/ci-cd.md` | in_progress |
| R-02 | Email/password + JWT auth only | `backend/app/api/auth.py`, `backend/app/services/auth_service.py`, `backend/app/models/user.py`, `backend/app/core/security.py` | `backend/tests/unit/test_security.py`, `backend/tests/contract/test_auth_api_contract.py`, `backend/tests/security/test_auth_mode_contract.py` | `docs/requirements-matrix.md`, `docs/api-spec.md` | done |
| R-03 | Drops integer-only money model | `backend/app/domain/money.py`, `backend/app/models/bout.py`, `backend/app/models/escrow.py`, `backend/sql/001_init_schema.sql` | `backend/tests/unit/test_money.py`, `backend/tests/property/test_money_properties.py`, `backend/tests/migration/test_schema_sql_contract.py` | `docs/schema-doc.md`, `docs/requirements-matrix.md` | done |
| R-04 | 1v1 with 4 escrow model | `backend/app/models/escrow.py`, `backend/app/services/bout_service.py`, `backend/app/models/bout.py` | `backend/tests/unit/test_bout_escrow_planning.py`, `backend/tests/integration/test_bout_create_flow.py` | `docs/state-machines.md`, `docs/schema-doc.md` | done |
| R-05 | Platform controls bonus fulfillment | `backend/app/crypto_conditions/fulfillment.py`, `backend/app/services/bout_service.py`, `backend/app/services/payout_service.py` | `backend/tests/unit/test_crypto_conditions.py`, `backend/tests/unit/test_xrpl_escrow_service.py`, `backend/tests/integration/test_payout_flow.py` | `docs/state-machines.md`, `docs/api-spec.md`, `docs/schema-doc.md` | done |
| R-06 | Promoter signs via Xaman only | backend Xaman sign-request integration (`backend/app/integrations/xaman_service.py`, `backend/app/api/bouts.py`) + frontend signing UX modules (pending) | `backend/tests/unit/test_xaman_service.py`, `backend/tests/integration/test_escrow_confirm_flow.py`, `backend/tests/integration/test_payout_flow.py`, `tests/e2e/test_promoter_signing_flow.py` (pending) | `docs/xaman-signing-contract.md`, runbook + frontend flow docs (pending) | in_progress |
| R-07 | Fixed finish/cancel timing rules | `backend/app/domain/time_rules.py`, `backend/app/services/bout_service.py` | `backend/tests/unit/test_time_rules.py`, `backend/tests/property/test_time_rules_properties.py`, `backend/tests/integration/test_timing_guards.py` | `docs/state-machines.md` | done |
| R-08 | Ledger-validated transitions only | `backend/app/api/bouts.py`, `backend/app/services/escrow_service.py`, `backend/app/services/payout_service.py`, `backend/app/services/xrpl_escrow_service.py` | `backend/tests/unit/test_xrpl_escrow_service.py`, `backend/tests/integration/test_escrow_confirm_flow.py`, `backend/tests/integration/test_payout_flow.py` | `docs/state-machines.md`, `docs/api-spec.md` | done |
| R-09 | Confirm endpoint idempotency | `backend/app/middleware/idempotency.py`, `backend/app/services/idempotency_service.py`, `backend/app/models/idempotency_key.py`, `backend/app/api/bouts.py` | `backend/tests/unit/test_idempotency_service.py`, `backend/tests/integration/test_escrow_confirm_flow.py`, `backend/tests/integration/test_payout_flow.py`, `backend/tests/security/test_confirm_idempotency_contract.py` | `docs/api-spec.md`, `docs/traceability-matrix.md` | done |
| R-10 | Backend enforces invariants (frontend untrusted) | role-gated `backend/app/api/bouts.py` + lifecycle/ledger validation services + `.github/workflows/ci-cd.yml` secret scan gate | `backend/tests/security/test_bout_role_guards.py`, `backend/tests/security/test_confirm_idempotency_contract.py`, CI gitleaks job | `docs/api-spec.md`, `docs/ci-cd.md` | in_progress |
| R-11 | Explicit lifecycle state machines | transition guards in `backend/app/services/escrow_service.py` and `backend/app/services/payout_service.py` | `backend/tests/integration/test_escrow_confirm_flow.py`, `backend/tests/integration/test_payout_flow.py`, `backend/tests/contract/test_bout_escrow_api_contract.py` | `docs/state-machines.md`, `docs/api-spec.md` | done |
| R-12 | Explicit failure handling | `backend/app/services/escrow_service.py`, `backend/app/services/payout_service.py` (audit + failure classification for invalid confirmation) | `backend/tests/integration/test_escrow_confirm_flow.py`, `backend/tests/integration/test_payout_flow.py` | `docs/state-machines.md`, `docs/api-spec.md` | in_progress |

## Increment 0 Deliverables (Completed)

| Item | Evidence |
|---|---|
| Scope and acceptance baseline locked | `docs/requirements-matrix.md` |
| Authoritative state machine contract locked | `docs/state-machines.md` |
| Initial requirement traceability table created | `docs/traceability-matrix.md` |

## Increment 1 Deliverables (Completed)

| Item | Evidence |
|---|---|
| FastAPI backend scaffold and auth route surface | `backend/app/main.py`, `backend/app/api/auth.py` |
| Auth service + password/token primitives | `backend/app/services/auth_service.py`, `backend/app/core/security.py` |
| Core schema foundation with enums and BIGINT money columns | `backend/sql/001_init_schema.sql`, `backend/app/models/*.py` |
| Money/time domain utilities with repeatable property-style tests | `backend/app/domain/money.py`, `backend/app/domain/time_rules.py`, `backend/tests/unit/*`, `backend/tests/property/*` |
| Bout creation service and escrow planning invariants | `backend/app/services/bout_service.py`, `backend/tests/unit/test_bout_escrow_planning.py`, `backend/tests/integration/test_bout_create_flow.py` |
| Timing guard integration assertions | `backend/tests/integration/test_timing_guards.py` |
| App bootstrap/startup integration assertion | `backend/tests/integration/test_stack_bootstrap.py` |
| API and schema docs added | `docs/api-spec.md`, `docs/schema-doc.md` |
| CI/CD quality + secret scanning baseline | `.github/workflows/ci-cd.yml`, `pyproject.toml` (`ruff` config), `.gitignore` |
| Dependency update automation | `.github/dependabot.yml` |

## Increment 2 Deliverables (Completed)

| Item | Evidence |
|---|---|
| Escrow create API prepare/confirm routes | `backend/app/api/bouts.py`, `backend/app/api/router.py` |
| Typed request/response contracts for escrow flow | `backend/app/schemas/escrow.py` |
| XRPL EscrowCreate payload builder and validation checks | `backend/app/services/xrpl_escrow_service.py` |
| Escrow lifecycle confirm service with audit persistence | `backend/app/services/escrow_service.py` |
| Confirm endpoint idempotency guard + storage | `backend/app/middleware/idempotency.py`, `backend/app/services/idempotency_service.py`, `backend/app/models/idempotency_key.py` |
| Escrow API contract coverage | `backend/tests/contract/test_bout_escrow_api_contract.py` |
| Escrow integration coverage (prepare/confirm, replay, invalid confirmation) | `backend/tests/integration/test_escrow_confirm_flow.py` |
| Confirm idempotency security contract coverage | `backend/tests/security/test_confirm_idempotency_contract.py` |
| XRPL and idempotency unit coverage | `backend/tests/unit/test_xrpl_escrow_service.py`, `backend/tests/unit/test_idempotency_service.py` |

## Increment 3 Deliverables (Completed)

| Item | Evidence |
|---|---|
| Role-gated bout lifecycle routes (`promoter`/`admin`) | `backend/app/api/dependencies.py`, `backend/app/api/bouts.py` |
| Result entry endpoint and state guard (`escrows_created -> result_entered`) | `backend/app/api/bouts.py`, `backend/app/services/payout_service.py` |
| Payout prepare/confirm endpoints with idempotent replay/collision behavior | `backend/app/api/bouts.py`, `backend/app/services/idempotency_service.py` |
| XRPL payout tx builder/validator (`EscrowFinish`/`EscrowCancel`) | `backend/app/services/xrpl_escrow_service.py` |
| Platform-controlled bonus fulfillment generation + verification path | `backend/app/crypto_conditions/fulfillment.py`, `backend/app/services/bout_service.py`, `backend/app/services/payout_service.py` |
| Payout lifecycle integration coverage (closeout + replay + timing rejection) | `backend/tests/integration/test_payout_flow.py` |
| Authz/security coverage for protected bout routes | `backend/tests/security/test_bout_role_guards.py` |
| Lifespan startup migration from deprecated FastAPI startup hook | `backend/app/main.py`, `backend/tests/integration/test_stack_bootstrap.py` |

## Mandatory Pre-Closeout Architecture Hardening Slice (Completed)

Goal: enforce consistent transaction boundaries and selective persistence abstractions without changing API or lifecycle semantics.

| Focus Req IDs | Implemented Refactor Targets | Test Targets | Documentation Targets | Status |
|---|---|---|---|---|
| R-08, R-09 | Lightweight Unit of Work for write-path transaction ownership (`backend/app/db/uow.py`) and atomic confirm persistence in `backend/app/api/bouts.py` + `backend/app/api/auth.py` | Unit/integration regression for commit ownership, replay/collision idempotency parity, and rollback safety (`backend/tests/unit/test_uow.py`, `backend/tests/integration/test_escrow_confirm_flow.py`, `backend/tests/integration/test_payout_flow.py`) | `docs/clean-architecture-refactor-plan.md`, `docs/api-spec.md`, `docs/state-machines.md`, `backend/README.md` | done |
| R-10, R-11, R-12 | Selective repositories for `Bout`, `Escrow`, `IdempotencyKey`, `AuditLog` (`backend/app/repositories/*.py`) with service-layer adoption in `backend/app/services/*.py` | Unit/security/failure-path regression for behavior parity (`backend/tests/unit/test_persistence_repositories.py`, `backend/tests/security/test_bout_role_guards.py`, `backend/tests/security/test_confirm_idempotency_contract.py`) | `docs/clean-architecture-refactor-plan.md`, `docs/traceability-matrix.md`, `docs/state-machines.md` | done |

## Increment 3.5 Deliverables (Completed)

| Item | Evidence |
|---|---|
| Session-backed Unit of Work with explicit commit/rollback ownership | `backend/app/db/uow.py`, `backend/app/api/auth.py`, `backend/app/api/bouts.py` |
| Selective repositories for persistence duplication reduction | `backend/app/repositories/bout_repository.py`, `backend/app/repositories/escrow_repository.py`, `backend/app/repositories/idempotency_key_repository.py`, `backend/app/repositories/audit_log_repository.py` |
| Service refactor to repository-backed data access and external transaction boundaries | `backend/app/services/bout_service.py`, `backend/app/services/escrow_service.py`, `backend/app/services/payout_service.py`, `backend/app/services/idempotency_service.py`, `backend/app/services/auth_service.py` |
| UoW/repository regression coverage | `backend/tests/unit/test_uow.py`, `backend/tests/unit/test_persistence_repositories.py`, `backend/tests/unit/test_bout_escrow_planning.py` |
| Lifecycle/idempotency parity verification | `backend/tests/integration/test_escrow_confirm_flow.py`, `backend/tests/integration/test_payout_flow.py`, `backend/tests/security/test_confirm_idempotency_contract.py` |

## Mandatory Pre-Closeout Migration Auth Modernization Slice (Completed)

Goal: enforce Alembic migration authority and proven auth-library adoption without changing locked auth/state contracts.

| Focus Req IDs | Implemented Modernization Targets | Test Targets | Documentation Targets | Status |
|---|---|---|---|---|
| R-01, R-08, R-09, R-11 | Alembic adopted as authoritative migration system with deterministic baseline revision and startup/runtime safety policy (no implicit production startup migrations) | Migration governance regression and offline upgrade/downgrade SQL compile coverage (`backend/tests/migration/test_alembic_baseline_contract.py`, `backend/tests/unit/test_db_init.py`) plus full backend regression suite (`backend/tests`) | `docs/alembic-adoption-plan.md`, `docs/schema-doc.md`, `docs/ci-cd.md`, `docs/traceability-matrix.md` | done |
| R-02, R-10, R-12 | Bespoke auth primitives replaced with proven maintained libraries (`passlib`, `PyJWT`) while preserving email/password plus JWT and forbidding wallet-login routes | Auth unit/contract/security regression (`backend/tests/unit/test_security.py`, `backend/tests/unit/test_api_dependencies_auth.py`, `backend/tests/contract/test_auth_api_contract.py`, `backend/tests/security/test_auth_mode_contract.py`) plus full backend regression suite (`backend/tests`) | `docs/auth-library-adoption-plan.md`, `docs/api-spec.md`, `docs/ci-cd.md`, `backend/README.md` | done |

## Increment 3.6 Deliverables (Completed)

| Item | Evidence |
|---|---|
| Alembic authority package with revision naming and rollback governance | `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/202602220000_baseline_schema.py`, `docs/alembic-adoption-plan.md`, `docs/schema-doc.md` |
| Auth-library adoption package with objective criteria and parity safeguards | `backend/app/core/security.py`, `pyproject.toml`, `docs/auth-library-adoption-plan.md` |
| Runtime migration safety policy enforcement | `backend/app/db/init_db.py`, `backend/tests/unit/test_db_init.py` |
| Migration validation evidence (forward/rollback compile path) | `backend/tests/migration/test_alembic_baseline_contract.py` |
| CI/CD and verification gate updates for migration/auth modernization | `docs/ci-cd.md` |
| Contract stability statement for modernization step | `docs/api-spec.md`, `docs/state-machines.md` |
| Milestone acceptance memo with residual risk statement | `docs/m3.6-modernization-acceptance-memo.md` |

## Increment 4 Slice A Deliverables (In Progress)

| Item | Evidence |
|---|---|
| Non-custodial Xaman integration boundary added | `backend/app/integrations/xaman_service.py` |
| Prepare endpoints emit Xaman sign-request metadata | `backend/app/api/bouts.py`, `backend/app/schemas/escrow.py`, `backend/app/schemas/payout.py`, `backend/app/schemas/xaman.py` |
| Failure-path handling for sign-request creation errors (`502`) | `backend/tests/integration/test_escrow_confirm_flow.py`, `backend/tests/integration/test_payout_flow.py` |
| Unit validation for stub/api Xaman service behavior | `backend/tests/unit/test_xaman_service.py` |
| M4 slice contract documentation | `docs/xaman-signing-contract.md`, `docs/api-spec.md`, `backend/README.md`, `README.md` |

## Test Evidence (Current)

| Command | Result | Notes |
|---|---|---|
| `.\venv\Scripts\python.exe -m compileall backend/app backend/tests` | pass | Syntax validation completed for all backend and test modules. |
| `.\venv\Scripts\python.exe -m ruff check backend` | pass | Lint gate is clean across backend sources/tests. |
| `.\venv\Scripts\python.exe -m ruff format --check backend` | pass | Formatting gate is clean. |
| `.\venv\Scripts\python.exe -m pytest backend/tests -q` | pass (`61 passed`) | Includes migration/auth modernization regression plus M4 Xaman integration coverage (`test_xaman_service`, prepare-flow sign-request/failure-path integration assertions). |
| `.\venv\Scripts\python.exe -m alembic -c backend/alembic.ini history` | pass | Confirms deterministic baseline revision head: `202602220000_baseline_schema`. |
| GitHub Actions quality/secret-scan/delivery jobs | configured | Enforced in `.github/workflows/ci-cd.yml`; executes on PR/push in GitHub runtime. |
| Dependabot weekly update streams | configured | Enforced in `.github/dependabot.yml` for `pip` and `github-actions`. |

## Next Implementation Slice (M4)

Target: hardening for operational readiness and residual risk reduction.

- M3.6 modernization is complete and accepted (see `docs/m3.6-modernization-acceptance-memo.md`).
- Continue Xaman integration hardening after initial backend sign-request contract delivery (`R-06`).
- Add failure taxonomy coverage for declined signing, `tec/tem`, and timeout outcomes (`R-12`).
- Add remaining frontend + e2e journey coverage for MVP critical paths (`R-01`, `R-10`).
- Add regression/performance suites and operational runbooks aligned to gate thresholds.
