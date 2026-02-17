# RingLedger API Spec (M2 Escrow Create Flow)

Last updated: 2026-02-17

## Scope

This document captures currently implemented API surface through M2 escrow-create prepare/confirm.

## Base Behavior

- Content type: `application/json`
- Auth mode: JWT bearer token (email/password login only)
- Money fields: drops (`integer`) only
- Confirm idempotency: `Idempotency-Key` header required on `POST /bouts/{bout_id}/escrows/confirm`

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
- Request body:

```json
{
  "email": "fighter@example.com",
  "password": "minimum-eight-chars",
  "role": "fighter"
}
```

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
- Request body:

```json
{
  "email": "fighter@example.com",
  "password": "minimum-eight-chars"
}
```

- Response `200`:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

- Error `401`: invalid credentials.

### `POST /bouts/{bout_id}/escrows/prepare`

- Purpose: generate unsigned XRPL `EscrowCreate` payloads for the bout escrow set.
- Response `200`:

```json
{
  "bout_id": "uuid",
  "escrows": [
    {
      "escrow_id": "uuid",
      "escrow_kind": "show_a",
      "unsigned_tx": {
        "TransactionType": "EscrowCreate",
        "Account": "rPromoter...",
        "Destination": "rFighter...",
        "Amount": "1000000",
        "FinishAfter": 823000000
      }
    }
  ]
}
```

- Error `404`: bout not found.
- Error `409`: prepare not allowed in current state.
- Error `422`: escrow planning set invalid.

### `POST /bouts/{bout_id}/escrows/confirm`

- Purpose: validate confirmed EscrowCreate result and apply `planned -> created` transition.
- Required header: `Idempotency-Key: <client-generated-key>`
- Request body:

```json
{
  "escrow_kind": "show_a",
  "tx_hash": "TX00000001",
  "offer_sequence": 1001,
  "validated": true,
  "engine_result": "tesSUCCESS",
  "owner_address": "rPromoter...",
  "destination_address": "rFighter...",
  "amount_drops": 1000000,
  "finish_after_ripple": 823000000,
  "cancel_after_ripple": null,
  "condition_hex": null
}
```

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
- Error `404`: bout or escrow not found.
- Error `409`: state conflict, or idempotency key reused with different payload.
- Error `422`: ledger confirmation failed validation (not validated, non-`tesSUCCESS`, or field mismatch).

#### Confirm Idempotency Contract

- First request with a new `(scope, Idempotency-Key)` persists both operation result and response payload.
- Replay with same key and identical request body returns stored status/body.
- Replay with same key and different request body is rejected deterministically with `409`.

## Explicit Non-Supported Auth Routes

- No wallet login endpoint exists in MVP.
- No XRPL address login is accepted.

## Planned Next Endpoints (Not Implemented Yet)

- `PUT /fighters/me`
- `POST /bouts`
- `GET /bouts`
- `GET /bouts/{id}`
- `POST /bouts/{id}/result`
- `POST /bouts/{id}/payouts/prepare`
- `POST /bouts/{id}/payouts/confirm`
