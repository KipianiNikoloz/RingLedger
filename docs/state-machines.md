# RingLedger MVP State Machines

Date locked: 2026-02-16

## Global Invariants

- Transition authority is backend only.
- Transition trigger requires validated XRPL transaction success (`tesSUCCESS`) where on-ledger activity is involved.
- Frontend state is advisory; backend performs final state-guard checks.
- Illegal transitions must return deterministic errors and emit audit events.

## Bout Lifecycle

### States

- `draft`: bout created, escrows planned but not yet ledger-created.
- `escrows_created`: all four escrows (`show_a`, `show_b`, `bonus_a`, `bonus_b`) validated as created on ledger.
- `result_entered`: admin entered winner (`A` or `B`).
- `payouts_in_progress`: at least one validated payout/cancel operation has started.
- `closed`: required payout completion criteria satisfied.

### Allowed Transitions

| From | To | Trigger | Guards | Side Effects |
|---|---|---|---|---|
| `draft` | `escrows_created` | Escrow create confirm flow completes | All 4 escrows validated created with `tesSUCCESS`; expected fields match; idempotency checks pass | Persist `offer_sequence`, tx hashes, escrow statuses |
| `escrows_created` | `result_entered` | Admin sets winner | Caller role is admin; winner in `{A,B}`; no payout started yet | Persist immutable winner intent for payout phase |
| `result_entered` | `payouts_in_progress` | First payout/cancel confirm succeeds | Confirm endpoint validated; source escrow state allows operation | Mark bout payout phase active |
| `payouts_in_progress` | `closed` | Required completion criteria reached | `show_a` finished, `show_b` finished, winner bonus finished (all validated) | Mark bout closed and final audit entry |

### Rejected Bout Transitions (Examples)

- `draft -> result_entered`
- `draft -> payouts_in_progress`
- `escrows_created -> closed`
- `result_entered -> draft`
- `closed -> any`

## Escrow Lifecycle

### States

- `planned`
- `created`
- `finished`
- `cancelled` (bonus escrows only)
- `failed` (terminal for persistent/invalid operation outcome)

### Allowed Transitions by Escrow Kind

| Escrow Kind | From | To | Trigger | Guards |
|---|---|---|---|---|
| `show_a`, `show_b`, `bonus_a`, `bonus_b` | `planned` | `created` | EscrowCreate confirmed | Ledger tx validated `tesSUCCESS`; tx fields match expected account/destination/amount/time/condition rules |
| `show_a`, `show_b` | `created` | `finished` | EscrowFinish confirmed | Current time >= `FinishAfter`; validated `tesSUCCESS`; owner/offer sequence match |
| winner bonus (`bonus_a` or `bonus_b`) | `created` | `finished` | EscrowFinish confirmed | Current time >= `FinishAfter`; valid fulfillment from platform preimage; validated `tesSUCCESS`; owner/offer sequence match |
| loser bonus (`bonus_a` or `bonus_b`) | `created` | `cancelled` | EscrowCancel confirmed | Current time >= `CancelAfter`; validated `tesSUCCESS`; owner/offer sequence match |
| any | `*` | `failed` | Terminal error classification | Persistent on-ledger failure, invalid confirmation mismatch, or security validation failure |

### Rejected Escrow Transitions (Examples)

- `planned -> finished`
- `planned -> cancelled`
- `created -> planned`
- `finished -> any`
- `cancelled -> any`

## Timing Guard Contract

- `FinishAfter` for all escrows: `event_datetime_utc + 2 hours`.
- `CancelAfter` for bonus escrows only: `event_datetime_utc + 7 days`.
- Backend computes and persists canonical UTC values and enforces them on confirm operations.

## Endpoint-to-State Mapping

| Endpoint | Primary State Effects | Notes |
|---|---|---|
| `POST /bouts` | creates bout in `draft`; creates 4 escrows in `planned` | No ledger transition yet |
| `POST /bouts/{id}/escrows/prepare` | no state transition | Generates unsigned tx payloads |
| `POST /bouts/{id}/escrows/confirm` | escrow `planned -> created`; bout `draft -> escrows_created` when all 4 done | Requires idempotency and ledger validation |
| `POST /bouts/{id}/result` | bout `escrows_created -> result_entered` | Admin only |
| `POST /bouts/{id}/payouts/prepare` | no state transition | Generates unsigned finish/cancel payloads |
| `POST /bouts/{id}/payouts/confirm` | escrow `created -> finished/cancelled`; bout enters `payouts_in_progress`; may reach `closed` | Requires idempotency and ledger validation |

## Failure Path Contract

- Signing declined: no transition; audited as non-fatal retryable action.
- `tec/tem`: no transition; persisted failure classification; manual or gated retry.
- Confirmation timeout: no optimistic transition; remains safe prior state with retry path.
- Invalid confirmation/field mismatch: reject, audit, and classify as security/integrity failure.
