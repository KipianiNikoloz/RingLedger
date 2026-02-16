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
| R-01 | Fixed stack and integration boundaries | `backend/app/main.py`, `frontend/src/main.tsx`, `backend/app/integrations/xaman_service.py`, `backend/app/integrations/xrpl_service.py`, `infra/*` | `tests/integration/test_stack_bootstrap.py` | `docs/requirements-matrix.md`, `docs/state-machines.md` | planned |
| R-02 | Email/password + JWT auth only | `backend/app/api/auth.py`, `backend/app/services/auth_service.py`, `backend/app/models/user.py` | `tests/unit/test_auth_service.py`, `tests/contract/test_auth_api.py`, `tests/security/test_authn_authz.py` | `docs/requirements-matrix.md`, API spec | planned |
| R-03 | Drops integer-only money model | `backend/app/domain/money.py`, `backend/app/models/bout.py`, DB BIGINT columns | `tests/unit/test_money_conversions.py`, `tests/property/test_money_properties.py`, `tests/migration/test_money_bigint.py` | schema docs, `docs/requirements-matrix.md` | planned |
| R-04 | 1v1 with 4 escrow model | `backend/app/models/escrow.py`, `backend/app/services/bout_service.py`, bout creation flow | `tests/unit/test_bout_escrow_planning.py`, `tests/integration/test_bout_create_flow.py` | `docs/state-machines.md`, schema docs | planned |
| R-05 | Platform controls bonus fulfillment | `backend/app/crypto_conditions/*`, `backend/app/services/payout_service.py` | `tests/unit/test_crypto_conditions.py`, `tests/integration/test_bonus_finish_flow.py`, `tests/security/test_preimage_controls.py` | `docs/state-machines.md`, security docs | planned |
| R-06 | Promoter signs via Xaman only | `backend/app/integrations/xaman_service.py`, frontend signing UX modules | `tests/integration/test_xaman_prepare_confirm.py`, `tests/e2e/test_promoter_signing_flow.py` | runbook + frontend flow docs | planned |
| R-07 | Fixed finish/cancel timing rules | `backend/app/domain/time_rules.py`, escrow builder logic | `tests/unit/test_time_rules.py`, `tests/property/test_ripple_epoch_properties.py`, `tests/integration/test_timing_guards.py` | `docs/state-machines.md` | planned |
| R-08 | Ledger-validated transitions only | confirm handlers in `backend/app/api/bouts_confirm.py`, XRPL validation services | `tests/integration/test_confirm_requires_validated_success.py`, `tests/failure/test_invalid_confirmation.py` | `docs/state-machines.md`, runbook | planned |
| R-09 | Confirm endpoint idempotency | `backend/app/middleware/idempotency.py`, `backend/app/models/idempotency_key.py` | `tests/unit/test_idempotency_store.py`, `tests/integration/test_confirm_idempotency.py`, `tests/security/test_replay.py` | API spec + ops docs | planned |
| R-10 | Backend enforces invariants (frontend untrusted) | all critical backend services + policy guards | `tests/security/test_backend_invariant_enforcement.py`, `tests/e2e/test_client_tamper_rejection.py` | security model docs | planned |
| R-11 | Explicit lifecycle state machines | domain state machine modules and transition guards | `tests/unit/test_state_machine_rules.py`, `tests/property/test_state_transition_properties.py`, `tests/regression/test_illegal_transition_rejections.py` | `docs/state-machines.md` | planned |
| R-12 | Explicit failure handling | error taxonomy + audit logging + retry policy modules | `tests/failure/test_decline_tec_tem_timeout_paths.py`, `tests/integration/test_audit_failure_logging.py` | runbooks + changelog entries | planned |

## Increment 0 Deliverables (Completed)

| Item | Evidence |
|---|---|
| Scope and acceptance baseline locked | `docs/requirements-matrix.md` |
| Authoritative state machine contract locked | `docs/state-machines.md` |
| Initial requirement traceability table created | `docs/traceability-matrix.md` |

## Next Implementation Slice (M1)

Target: backend and database foundation with no XRPL side effects yet.

- Implement auth models and endpoints (`R-02`).
- Implement core schema and enums with BIGINT drops (`R-03`, `R-04`).
- Implement money/time utility contracts with property tests (`R-03`, `R-07`).
- Add API/schema docs and update this matrix statuses from `planned` to `in_progress`/`done` per merged slice.
