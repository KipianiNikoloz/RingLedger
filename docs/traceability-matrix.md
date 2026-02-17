# RingLedger MVP Traceability Matrix

Date initialized: 2026-02-16  
Last updated: 2026-02-17  
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
| R-05 | Platform controls bonus fulfillment | `backend/app/crypto_conditions/*`, `backend/app/services/payout_service.py` | `tests/unit/test_crypto_conditions.py`, `tests/integration/test_bonus_finish_flow.py`, `tests/security/test_preimage_controls.py` | `docs/state-machines.md`, security docs | planned |
| R-06 | Promoter signs via Xaman only | `backend/app/integrations/xaman_service.py`, frontend signing UX modules | `tests/integration/test_xaman_prepare_confirm.py`, `tests/e2e/test_promoter_signing_flow.py` | runbook + frontend flow docs | planned |
| R-07 | Fixed finish/cancel timing rules | `backend/app/domain/time_rules.py`, `backend/app/services/bout_service.py` | `backend/tests/unit/test_time_rules.py`, `backend/tests/property/test_time_rules_properties.py`, `backend/tests/integration/test_timing_guards.py` | `docs/state-machines.md` | done |
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

## Increment 1 Test Evidence (Current)

| Command | Result | Notes |
|---|---|---|
| `.\venv\Scripts\python.exe -m compileall backend/app backend/tests` | pass | Syntax validation completed for all backend and test modules. |
| `.\venv\Scripts\python.exe -m ruff check backend` | pass | Lint gate is clean across backend sources/tests. |
| `.\venv\Scripts\python.exe -m ruff format --check backend` | pass | Formatting gate is clean. |
| `.\venv\Scripts\python.exe -m unittest discover -s backend/tests -p "test_*.py"` | pass (`19` run, `0` skipped) | Includes concrete coverage for stack bootstrap, bout create flow, timing guards, and escrow planning. |
| GitHub Actions quality/secret-scan/delivery jobs | configured | Enforced in `.github/workflows/ci-cd.yml`; executes on PR/push in GitHub runtime. |
| Dependabot weekly update streams | configured | Enforced in `.github/dependabot.yml` for `pip` and `github-actions`. |

## Next Implementation Slice (M2)

Target: implement escrow create prepare/confirm with validated XRPL confirmation and replay-safe idempotency.

- Implement escrow prepare/confirm endpoint contracts and typed schemas (`R-08`, `R-09`).
- Implement XRPL create transaction builder + validated-ledger confirmation service (`R-08`).
- Implement idempotency middleware/storage behavior for confirm endpoints (`R-09`).
- Add integration/security/failure tests for replay, invalid confirmation, and non-validated ledger outcomes (`R-08`, `R-09`, `R-12`).
- Update API/state-machine/traceability docs with M2 evidence in the same increment.
