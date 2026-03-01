# RingLedger Operational Flow (M4)

Last updated: 2026-03-01

## Purpose

Define the operator-facing sequence for secure MVP lifecycle execution and failure-safe recovery.

This flow reflects implemented endpoints and current state-machine constraints.

## Actor Roles

- promoter: signs escrow/payout transactions via Xaman and confirms ledger outcomes
- admin: sets winner
- backend: authoritative validator and state-transition gate

## End-to-End Flow

### 1. Auth and Role Setup

1. Register/login users with email/password.
2. Issue JWT bearer tokens for `promoter` and `admin`.
3. Verify role permissions before lifecycle actions.

### 2. Escrow Creation Phase

1. Promoter calls `POST /bouts/{bout_id}/escrows/prepare`.
2. Backend returns unsigned `EscrowCreate` payloads with `xaman_sign_request`.
3. Promoter signs in Xaman.
4. Optional: promoter calls `POST /bouts/{bout_id}/escrows/signing/reconcile` to persist observed signing outcome.
5. Promoter calls `POST /bouts/{bout_id}/escrows/confirm` with `Idempotency-Key` and ledger evidence.
6. Backend validates `tesSUCCESS` and invariants, then transitions escrow `planned -> created`.
7. When all 4 escrows are `created`, bout transitions `draft -> escrows_created`.

### 3. Result Entry Phase

1. Admin calls `POST /bouts/{bout_id}/result` with winner `A` or `B`.
2. Backend validates admin role and state guard.
3. Bout transitions `escrows_created -> result_entered`.

### 4. Payout Phase

1. Promoter calls `POST /bouts/{bout_id}/payouts/prepare`.
2. Backend returns unsigned `EscrowFinish`/`EscrowCancel` payloads with `xaman_sign_request`.
3. Promoter signs in Xaman.
4. Optional: promoter calls `POST /bouts/{bout_id}/payouts/signing/reconcile`.
5. Promoter calls `POST /bouts/{bout_id}/payouts/confirm` with `Idempotency-Key` and ledger evidence.
6. Backend validates lifecycle/timing/ledger invariants and applies payout transitions.
7. Bout advances to `payouts_in_progress` and eventually `closed` when completion criteria are met.

## Failure-Safe Branches

### Signing Outcome Branches

- `open`: keep escrow state unchanged; retry reconciliation or continue waiting.
- `signed`: continue to confirm with validated ledger payload.
- `declined`: persist `signing_declined`; no lifecycle transition.
- `expired`: persist `signing_expired`; no lifecycle transition.

### Confirm Failure Branches

- `confirmation_timeout`: no transition, retry with validated evidence.
- `ledger_tec_tem`: no transition, investigate ledger rejection.
- `invalid_confirmation`: reject payload, regenerate from canonical prepare output.
- idempotency collision (`409`): reject replay with mismatched request body.

## Guardrails

- No state transition without validated ledger success where ledger activity applies.
- Confirm endpoints require idempotency keys and deterministic replay behavior.
- Frontend remains untrusted; backend validates role/state/timing/invariants on every critical action.
- Backend never stores promoter private keys.

## Operator Decision Rules

1. If response is `502` from prepare/reconcile: treat as integration issue and retry after dependency checks.
2. If response is `422` from confirm: follow failure-code-specific retry path; do not force state changes.
3. If response is `409` with idempotency collision: preserve original request contract; use a new key only for a new intent.
4. If response is `403`/`401`: correct token/role before retry.

## Verification Checkpoints

At each phase boundary, verify:

- expected bout state
- expected escrow state(s)
- failure code only when applicable
- audit entries for critical transitions/failures

Reference:

- `docs/state-machines.md`
- `docs/xaman-signing-contract.md`
- `docs/operations-runbook.md`

