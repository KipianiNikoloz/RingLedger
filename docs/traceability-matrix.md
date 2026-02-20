# RingLedger MVP Traceability Matrix

Date initialized: 2026-02-16  
Last updated: 2026-02-18  
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
| R-06 | Promoter signs via Xaman only | `backend/app/integrations/xaman_service.py`, frontend signing UX modules | `tests/integration/test_xaman_prepare_confirm.py`, `tests/e2e/test_promoter_signing_flow.py` | runbook + frontend flow docs | planned |
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

## Test Evidence (Current)

| Command | Result | Notes |
|---|---|---|
| `.\venv\Scripts\python.exe -m compileall backend/app backend/tests` | pass | Syntax validation completed for all backend and test modules. |
| `.\venv\Scripts\python.exe -m ruff check backend` | pass | Lint gate is clean across backend sources/tests. |
| `.\venv\Scripts\python.exe -m ruff format --check backend` | pass | Formatting gate is clean. |
| `.\venv\Scripts\python.exe -m unittest discover -s backend/tests -p "test_*.py"` | pass (`44` run, `0` skipped) | Includes escrow create + payout prepare/confirm lifecycle flows, idempotency replay/collision, role guards, crypto-condition handling, and invalid-confirmation failure-path coverage. |
| GitHub Actions quality/secret-scan/delivery jobs | configured | Enforced in `.github/workflows/ci-cd.yml`; executes on PR/push in GitHub runtime. |
| Dependabot weekly update streams | configured | Enforced in `.github/dependabot.yml` for `pip` and `github-actions`. |

## Next Implementation Slice (M4)

Target: hardening for operational readiness and residual risk reduction.

- Implement Xaman integration and non-custodial signing handoff completion (`R-06`).
- Add failure taxonomy coverage for declined signing, `tec/tem`, and timeout outcomes (`R-12`).
- Add remaining frontend + e2e journey coverage for MVP critical paths (`R-01`, `R-10`).
- Add regression/performance suites and operational runbooks aligned to gate thresholds.
