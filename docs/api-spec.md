# RingLedger API Spec (M1 Foundation)

Last updated: 2026-02-16

## Scope

This document captures currently implemented API surface for M1 foundation.

## Base Behavior

- Content type: `application/json`
- Auth mode: JWT bearer token (email/password login only)
- Money fields: drops (`integer`) only

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

## Explicit Non-Supported Auth Routes

- No wallet login endpoint exists in MVP.
- No XRPL address login is accepted.

## Planned Next Endpoints (Not Implemented Yet)

- `PUT /fighters/me`
- `POST /bouts`
- `GET /bouts`
- `GET /bouts/{id}`
- `POST /bouts/{id}/escrows/prepare`
- `POST /bouts/{id}/escrows/confirm`
- `POST /bouts/{id}/result`
- `POST /bouts/{id}/payouts/prepare`
- `POST /bouts/{id}/payouts/confirm`
