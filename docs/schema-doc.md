# RingLedger Schema Docs (M3 Lifecycle)

Last updated: 2026-02-18  
Schema SQL file: `backend/sql/001_init_schema.sql`

## Enums

- `user_role`: `promoter`, `fighter`, `management`, `admin`
- `bout_status`: `draft`, `ready_for_escrow`, `escrows_created`, `result_entered`, `payouts_in_progress`, `closed`
- `escrow_kind`: `show_a`, `show_b`, `bonus_a`, `bonus_b`
- `escrow_status`: `planned`, `created`, `finished`, `cancelled`, `failed`
- `bout_winner`: `A`, `B`

## Tables

### `users`

- Purpose: auth identity and role.
- Key columns:
  - `id UUID PK`
  - `email VARCHAR(320) UNIQUE NOT NULL`
  - `password_hash VARCHAR(512) NOT NULL`
  - `role user_role NOT NULL`

### `fighter_profiles`

- Purpose: fighter display data and XRPL destination address.
- Key columns:
  - `user_id UUID UNIQUE FK users(id)`
  - `display_name VARCHAR(120) NOT NULL`
  - `xrpl_address VARCHAR(64) UNIQUE NOT NULL`

### `bouts`

- Purpose: 1v1 bout configuration and lifecycle state.
- Key columns:
  - `promoter_user_id UUID FK users(id)`
  - `fighter_a_user_id UUID FK users(id)`
  - `fighter_b_user_id UUID FK users(id)`
  - `event_datetime_utc TIMESTAMPTZ`
  - `finish_after_utc TIMESTAMPTZ`
  - `cancel_after_utc TIMESTAMPTZ`
  - `show_a_drops BIGINT`
  - `show_b_drops BIGINT`
  - `bonus_a_drops BIGINT`
  - `bonus_b_drops BIGINT`
  - `status bout_status`
  - `winner bout_winner NULL`

### `escrows`

- Purpose: on-ledger escrow references and lifecycle state.
- Key columns:
  - `bout_id UUID FK bouts(id)`
  - `kind escrow_kind`
  - `status escrow_status`
  - `owner_address VARCHAR(64)`
  - `destination_address VARCHAR(64)`
  - `amount_drops BIGINT`
  - `finish_after_ripple INTEGER`
  - `cancel_after_ripple INTEGER NULL`
  - `condition_hex VARCHAR(1024) NULL`
  - `encrypted_preimage_hex VARCHAR(4096) NULL`
  - `offer_sequence INTEGER NULL`
  - `create_tx_hash VARCHAR(128) NULL`
  - `close_tx_hash VARCHAR(128) NULL`

- Constraints:
  - one escrow per (`bout_id`, `kind`)
  - non-negative `amount_drops`
  - bonus escrows store platform-generated `condition_hex` and fulfillment secret (`encrypted_preimage_hex`) for winner payout validation

### `audit_log`

- Purpose: append-only event record for critical actions.

### `idempotency_keys`

- Purpose: replay-safe deduplication for confirm endpoints.
- Constraint: unique (`scope`, `idempotency_key`)

## Indexes

- `bouts`: promoter, event date, status
- `escrows`: bout, status, owner+offer_sequence
- `fighter_profiles`: xrpl_address

## Money Model Contract

- All money fields use `BIGINT`.
- No floating-point currency storage.
- All amounts are drops (`1 XRP = 1,000,000 drops`).
