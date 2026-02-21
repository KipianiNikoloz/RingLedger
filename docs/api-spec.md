# RingLedger API Spec (M3 Result + Payout Flow)

Last updated: 2026-02-21

## Scope

This document captures the implemented API surface through M3:

- Auth: register/login (email/password -> JWT)
- Escrow create prepare/confirm
- Result entry
- Payout prepare/confirm

## Mandatory Architecture Hardening Note (Pre-M4 Closeout)

- Implemented refactor scope: internal persistence-boundary hardening with lightweight Unit of Work and selective repositories.
- No API contract changes were introduced by this step:
  - no endpoint path changes
  - no request/response schema changes
  - no status-code contract changes
- Any contract change is out of scope for this refactor and requires explicit docs/traceability updates.

## Mandatory Migration Auth Modernization Note (Pre-M4 Closeout)

- Planned modernization scope: Alembic migration authority and proven auth-library adoption.
- Contract stability expectations during this step:
  - no endpoint path changes
  - no request/response schema changes
  - no auth mode expansion beyond email/password plus JWT
  - no wallet-login route additions
- Any API contract change remains out of scope unless explicitly versioned and documented.

## Base Behavior

- Content type: `application/json`
- Auth mode: JWT bearer token (email/password login only)
- Money fields: drops (`integer`) only
- Protected routes: all `POST /bouts/*` routes require `Authorization: Bearer <jwt>`
- Role guards:
  - `POST /bouts/{bout_id}/result` requires `admin`
  - all other `POST /bouts/*` routes require `promoter`
- Confirm idempotency:
  - `POST /bouts/{bout_id}/escrows/confirm` requires `Idempotency-Key`
  - `POST /bouts/{bout_id}/payouts/confirm` requires `Idempotency-Key`

## Endpoints

### `GET /healthz`

- Purpose: service health probe.
- Response `200`:

```json
{
  "status": "ok"
}
```

### `POST /auth/register`

- Purpose: create user account with role.
- Response `201`:

```json
{
  "user_id": "uuid",
  "email": "fighter@example.com",
  "role": "fighter"
}
```

- Error `409`: email already exists.

### `POST /auth/login`

- Purpose: issue access token.
- Response `200`:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

- Error `401`: invalid credentials.

### `POST /bouts/{bout_id}/escrows/prepare`

- Purpose: generate unsigned XRPL `EscrowCreate` payloads for all 4 escrows.
- Response `200`:

```json
{
  "bout_id": "uuid",
  "escrows": [
    {
      "escrow_id": "uuid",
      "escrow_kind": "bonus_a",
      "unsigned_tx": {
        "TransactionType": "EscrowCreate",
        "Account": "rPromoter...",
        "Destination": "rFighter...",
        "Amount": "250000",
        "FinishAfter": 823000000,
        "CancelAfter": 823604800,
        "Condition": "ABCDEF..."
      }
    }
  ]
}
```

- Error `401`: missing/invalid bearer token.
- Error `403`: caller role is not promoter.
- Error `404`: bout not found.
- Error `409`: prepare not allowed in current state.
- Error `422`: escrow plan invalid.

### `POST /bouts/{bout_id}/escrows/confirm`

- Purpose: validate confirmed `EscrowCreate` result and apply `planned -> created`.
- Required header: `Idempotency-Key: <client-generated-key>`
- Response `200`:

```json
{
  "bout_id": "uuid",
  "escrow_id": "uuid",
  "escrow_kind": "show_a",
  "escrow_status": "created",
  "bout_status": "draft",
  "tx_hash": "TX00000001",
  "offer_sequence": 1001
}
```

- Error `400`: missing idempotency header or malformed request.
- Error `401`: missing/invalid bearer token.
- Error `403`: caller role is not promoter.
- Error `404`: bout or escrow not found.
- Error `409`: state conflict, or idempotency key reused with different payload.
- Error `422`: ledger confirmation failed validation.

### `POST /bouts/{bout_id}/result`

- Purpose: set winner (`A`/`B`) and move `escrows_created -> result_entered`.
- Role: admin only.
- Request body:

```json
{
  "winner": "A"
}
```

- Response `200`:

```json
{
  "bout_id": "uuid",
  "bout_status": "result_entered",
  "winner": "A"
}
```

- Error `401`: missing/invalid bearer token.
- Error `403`: caller role is not admin.
- Error `404`: bout not found.
- Error `409`: result entry not allowed in current state.

### `POST /bouts/{bout_id}/payouts/prepare`

- Purpose: generate unsigned payout payloads for outstanding escrows:
  - `EscrowFinish` for `show_a` and `show_b`
  - `EscrowFinish` for winner bonus (with platform fulfillment)
  - `EscrowCancel` for loser bonus
- Role: promoter.
- Response `200`:

```json
{
  "bout_id": "uuid",
  "bout_status": "result_entered",
  "escrows": [
    {
      "escrow_id": "uuid",
      "escrow_kind": "bonus_a",
      "action": "finish",
      "unsigned_tx": {
        "TransactionType": "EscrowFinish",
        "Account": "rPromoter...",
        "Owner": "rPromoter...",
        "OfferSequence": 6003,
        "Fulfillment": "A1B2..."
      }
    },
    {
      "escrow_id": "uuid",
      "escrow_kind": "bonus_b",
      "action": "cancel",
      "unsigned_tx": {
        "TransactionType": "EscrowCancel",
        "Account": "rPromoter...",
        "Owner": "rPromoter...",
        "OfferSequence": 6004
      }
    }
  ]
}
```

- Error `401`: missing/invalid bearer token.
- Error `403`: caller role is not promoter.
- Error `404`: bout not found.
- Error `409`: payout prepare not allowed in current state.
- Error `422`: payout setup invalid.

### `POST /bouts/{bout_id}/payouts/confirm`

- Purpose: validate confirmed payout tx and apply escrow close transition:
  - `created -> finished` for show/winner bonus
  - `created -> cancelled` for loser bonus
- Required header: `Idempotency-Key: <client-generated-key>`
- Role: promoter.
- Request body (finish example):

```json
{
  "escrow_kind": "bonus_a",
  "tx_hash": "TXPAYOUT0003",
  "validated": true,
  "engine_result": "tesSUCCESS",
  "transaction_type": "EscrowFinish",
  "owner_address": "rPromoter...",
  "offer_sequence": 6003,
  "close_time_ripple": 823000100,
  "fulfillment_hex": "A1B2..."
}
```

- Response `200`:

```json
{
  "bout_id": "uuid",
  "escrow_id": "uuid",
  "escrow_kind": "bonus_a",
  "escrow_status": "finished",
  "bout_status": "closed",
  "tx_hash": "TXPAYOUT0003"
}
```

- Error `400`: missing idempotency header or malformed request.
- Error `401`: missing/invalid bearer token.
- Error `403`: caller role is not promoter.
- Error `404`: bout or escrow not found.
- Error `409`: state conflict, or idempotency key reused with different payload.
- Error `422`: ledger confirmation failed validation (timing, tx type, offer sequence, fulfillment, or `tesSUCCESS` mismatch).

## Confirm Idempotency Contract

- First request with a new `(scope, Idempotency-Key)` persists operation result and response payload.
- Replay with same key and identical request body returns stored status/body.
- Replay with same key and different request body is rejected deterministically with `409`.
- Implemented scopes:
  - `escrow_create_confirm:{bout_id}`
  - `payout_confirm:{bout_id}`

## Explicit Non-Supported Auth Routes

- No wallet login endpoint exists in MVP.
- No XRPL address login endpoint exists.

## Planned Next Endpoints (Not Implemented Yet)

- `PUT /fighters/me`
- `POST /bouts`
- `GET /bouts`
- `GET /bouts/{id}`
