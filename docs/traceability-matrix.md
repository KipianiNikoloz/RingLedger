# FightPurse MVP Traceability Matrix

Date initialized: 2026-02-16  
Purpose: enforce requirement -> implementation -> tests -> docs linkage from first increment.

## Status Legend

- `planned`: implementation target defined but not coded yet.
- `in_progress`: slice active.
- `done`: implemented, tested, documented.

## Requirement Traceability

| Req ID | Requirement Summary | Planned Implementation Targets | Planned Test Targets | Documentation Targets | Status |
|---|---|---|---|---|---|
| R-01 | Fixed stack and integration boundaries | `backend/app/main.py`, `backend/app/api/router.py`, `backend/app/db/session.py`, `.github/workflows/ci-cd.yml`, `frontend/src/main.tsx` (pending), XRPL/Xaman integrations (pending) | `backend/tests/integration/test_stack_bootstrap.py` (pending) | `docs/requirements-matrix.md`, `docs/state-machines.md`, `backend/README.md`, `docs/ci-cd.md` | in_progress |
| R-02 | Email/password + JWT auth only | `backend/app/api/auth.py`, `backend/app/services/auth_service.py`, `backend/app/models/user.py`, `backend/app/core/security.py` | `backend/tests/unit/test_security.py`, `backend/tests/contract/test_auth_api_contract.py`, `backend/tests/security/test_auth_mode_contract.py` | `docs/requirements-matrix.md`, `docs/api-spec.md` | in_progress |
| R-03 | Drops integer-only money model | `backend/app/domain/money.py`, `backend/app/models/bout.py`, `backend/app/models/escrow.py`, `backend/sql/001_init_schema.sql` | `backend/tests/unit/test_money.py`, `backend/tests/property/test_money_properties.py`, `backend/tests/migration/test_schema_sql_contract.py` | `docs/schema-doc.md`, `docs/requirements-matrix.md` | in_progress |
| R-04 | 1v1 with 4 escrow model | `backend/app/models/escrow.py`, `backend/app/services/bout_service.py`, `backend/app/models/bout.py` | `backend/tests/unit/test_bout_escrow_planning.py` (pending), `backend/tests/integration/test_bout_create_flow.py` (pending) | `docs/state-machines.md`, `docs/schema-doc.md` | in_progress |
| R-05 | Platform controls bonus fulfillment | `backend/app/crypto_conditions/*`, `backend/app/services/payout_service.py` | `tests/unit/test_crypto_conditions.py`, `tests/integration/test_bonus_finish_flow.py`, `tests/security/test_preimage_controls.py` | `docs/state-machines.md`, security docs | planned |
| R-06 | Promoter signs via Xaman only | `backend/app/integrations/xaman_service.py`, frontend signing UX modules | `tests/integration/test_xaman_prepare_confirm.py`, `tests/e2e/test_promoter_signing_flow.py` | runbook + frontend flow docs | planned |
| R-07 | Fixed finish/cancel timing rules | `backend/app/domain/time_rules.py`, `backend/app/services/bout_service.py` | `backend/tests/unit/test_time_rules.py`, `backend/tests/property/test_time_rules_properties.py`, `backend/tests/integration/test_timing_guards.py` (pending) | `docs/state-machines.md` | in_progress |
| R-08 | Ledger-validated transitions only | confirm handlers in `backend/app/api/bouts_confirm.py`, XRPL validation services | `tests/integration/test_confirm_requires_validated_success.py`, `tests/failure/test_invalid_confirmation.py` | `docs/state-machines.md`, runbook | planned |
| R-09 | Confirm endpoint idempotency | `backend/app/middleware/idempotency.py`, `backend/app/models/idempotency_key.py` | `tests/unit/test_idempotency_store.py`, `tests/integration/test_confirm_idempotency.py`, `tests/security/test_replay.py` | API spec + ops docs | planned |
| R-10 | Backend enforces invariants (frontend untrusted) | all critical backend services + policy guards, `.github/workflows/ci-cd.yml` secret scan gate | `tests/security/test_backend_invariant_enforcement.py`, `tests/e2e/test_client_tamper_rejection.py`, CI gitleaks job | security model docs, `docs/ci-cd.md` | in_progress |
| R-11 | Explicit lifecycle state machines | domain state machine modules and transition guards | `tests/unit/test_state_machine_rules.py`, `tests/property/test_state_transition_properties.py`, `tests/regression/test_illegal_transition_rejections.py` | `docs/state-machines.md` | planned |
| R-12 | Explicit failure handling | error taxonomy + audit logging + retry policy modules | `tests/failure/test_decline_tec_tem_timeout_paths.py`, `tests/integration/test_audit_failure_logging.py` | runbooks + changelog entries | planned |

## Increment 0 Deliverables (Completed)

| Item | Evidence |
|---|---|
| Scope and acceptance baseline locked | `docs/requirements-matrix.md` |
| Authoritative state machine contract locked | `docs/state-machines.md` |
| Initial requirement traceability table created | `docs/traceability-matrix.md` |

## Increment 1 Deliverables (In Progress)

| Item | Evidence |
|---|---|
| FastAPI backend scaffold and auth route surface | `backend/app/main.py`, `backend/app/api/auth.py` |
| Auth service + password/token primitives | `backend/app/services/auth_service.py`, `backend/app/core/security.py` |
| Core schema foundation with enums and BIGINT money columns | `backend/sql/001_init_schema.sql`, `backend/app/models/*.py` |
| Money/time domain utilities with repeatable property-style tests | `backend/app/domain/money.py`, `backend/app/domain/time_rules.py`, `backend/tests/unit/*`, `backend/tests/property/*` |
| API and schema docs added | `docs/api-spec.md`, `docs/schema-doc.md` |
| CI/CD quality + secret scanning baseline | `.github/workflows/ci-cd.yml`, `pyproject.toml` (`ruff` config), `.gitignore` |
| Dependency update automation | `.github/dependabot.yml` |

## Increment 1 Test Evidence (Current)

| Command | Result | Notes |
|---|---|---|
| `python -m compileall backend/app backend/tests` | pass | Syntax validation completed for all backend and test modules. |
| `python -m unittest discover -s backend/tests -p "test_*.py"` | pass (`18` run, `6` skipped) | Skipped tests are dependency/integration gated and marked with explicit reasons. |
| GitHub Actions quality/secret-scan/delivery jobs | configured | Enforced in `.github/workflows/ci-cd.yml`; executes on PR/push in GitHub runtime. |
| Dependabot weekly update streams | configured | Enforced in `.github/dependabot.yml` for `pip` and `github-actions`. |

## Next Implementation Slice (M1)

Target: complete backend and database foundation with no XRPL side effects yet.

- Implement auth models and endpoints (`R-02`).
- Implement core schema and enums with BIGINT drops (`R-03`, `R-04`).
- Implement money/time utility contracts with property tests (`R-03`, `R-07`).
- Add pending integration tests (`stack bootstrap`, `bout create flow`, `timing guards`).
- Install dependencies and run full test suites in CI/local dev.
