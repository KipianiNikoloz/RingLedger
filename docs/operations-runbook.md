# RingLedger Operations Runbook (M4 Hardening)

Last updated: 2026-03-01

## Purpose

Provide operational procedures for MVP lifecycle flows, with focus on M4 hardening requirements:

- non-custodial Xaman signing reliability (`R-06`)
- explicit failure handling and safe retries (`R-12`)
- backend-authoritative lifecycle invariants (`R-08`, `R-10`, `R-11`)

This runbook is for day-2 operations and incident response, not feature development.

## Scope

Covered:

- escrow prepare/sign/reconcile/confirm flow operations
- payout prepare/sign/reconcile/confirm flow operations
- degraded-mode procedures for signing and confirmation failures
- release, rollback, and evidence capture checklist

Not covered:

- requirement or state-machine changes
- wallet-login expansion (explicitly out of MVP)

## Runtime Modes and Required Configuration

- `XAMAN_MODE=stub` for deterministic local/CI behavior
- `XAMAN_MODE=api` for live Xaman API integration
- `XAMAN_API_KEY` and `XAMAN_API_SECRET` required when `XAMAN_MODE=api`
- `JWT_SECRET_KEY` must be strong and environment-managed in non-local environments

Reference:

- `docs/xaman-signing-contract.md`
- `docs/state-machines.md`

## Operational Flow Reference

Use `docs/operational-flow.md` as the canonical step-by-step lifecycle sequence.

Operators should always confirm that observed actions are valid for the current lifecycle state before any retry or recovery action.

## Pre-Deploy Checklist

1. Confirm migration head is deterministic:
   - `.\venv\Scripts\python.exe -m alembic -c backend/alembic.ini history`
2. Run backend quality gates:
   - `.\venv\Scripts\python.exe -m compileall backend/app backend/tests`
   - `.\venv\Scripts\python.exe -m ruff check backend`
   - `.\venv\Scripts\python.exe -m ruff format --check backend docs`
   - `.\venv\Scripts\python.exe -m pytest backend/tests -q`
3. Run targeted M4 regression/performance suites:
   - `.\venv\Scripts\python.exe -m pytest backend/tests/regression backend/tests/performance -q`
4. Confirm CI `quality`, `frontend-quality`, and `secret-scan` jobs are green for the merge commit.

## Incident Classification Matrix

| Signal | Typical Surface | Classification | Immediate Action |
|---|---|---|---|
| `502` on `*/prepare` | Xaman sign-request generation | signing integration degradation | Validate Xaman credentials/mode, retry after service check, keep state unchanged |
| `502` on `*/signing/reconcile` | Xaman status query | signing reconciliation degradation | Verify payload ID and Xaman reachability, retry reconcile |
| `422` with decline/timeout/`tec`/`tem` message | `*/confirm` | deterministic confirm failure | Keep lifecycle unchanged, follow retry path for that failure code |
| `409` idempotency collision | `*/confirm` | request replay mismatch | Stop client retries with mutated body, issue deterministic operator guidance |
| unexpected state conflict | result/payout/confirm routes | lifecycle guard conflict | Re-check bout + escrow state against state machine before retry |

## Recovery Procedures

### 1. Xaman Integration Degradation (`502`)

1. Confirm mode and credentials:
   - local/CI should use `XAMAN_MODE=stub`
   - environments using `api` must have non-empty `XAMAN_API_KEY`/`XAMAN_API_SECRET`
2. Verify endpoint currently failing (`escrows/prepare`, `payouts/prepare`, or signing reconcile endpoints).
3. Retry after dependency health check.
4. If persistent in `api` mode, temporarily route operators to controlled retry windows while preserving no-transition behavior.
5. Do not force lifecycle transitions; confirm endpoints remain authoritative.

### 2. Deterministic Confirm Failure (`422`)

1. Read failure message and mapped `failure_code` from response/audit.
2. Apply handling:
   - `signing_declined`: request new promoter signing action.
   - `signing_expired`: create a new signing attempt and reconcile again.
   - `confirmation_timeout`: retry confirmation only with validated ledger evidence.
   - `ledger_tec_tem`: stop automatic retries; investigate ledger rejection reason.
   - `invalid_confirmation`: reject payload and rebuild from canonical prepare contract.
3. Confirm no unauthorized state transition occurred.

### 3. Idempotency Mismatch (`409`)

1. Identify `(scope, idempotency-key)` tuple.
2. Compare request body hash/fields with original request.
3. Enforce same-body replay only; never mutate a request and reuse the same key.
4. If client behavior is buggy, require a new idempotency key and a fresh confirmed request intent.

## Rollback Procedure

1. Freeze rollout and stop further deploys.
2. Capture failing revision and exact error class.
3. If schema rollback is required, execute controlled Alembic downgrade to last accepted revision and verify API boot.
4. Re-run smoke gates:
   - `GET /healthz`
   - auth login
   - escrow prepare
   - payout prepare
5. Record rollback event and corrective actions in traceability documentation.

## Evidence Capture Checklist

Capture all of the following for any P1/P2 incident:

- failing request path and status code
- actor role and bout/escrow identifiers
- returned deterministic error message
- relevant audit entries (`failure_code`, `failure_reason`)
- idempotency key and replay behavior outcome
- Xaman mode and payload identifiers (no secrets)
- remediation steps and final verification command output summary

## Exit Criteria for Incident Closure

An incident is closed only when:

1. failing path is reproducibly healthy
2. no lifecycle correctness drift is observed
3. replay/idempotency behavior remains deterministic
4. postmortem notes are linked to docs/traceability updates

