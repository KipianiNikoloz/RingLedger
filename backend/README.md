# RingLedger Backend (M3 Result + Payout Flow)

## Current Scope

- FastAPI application bootstrap (`app/main.py`)
- Health endpoint (`GET /healthz`)
- Auth endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
- Protected bout lifecycle endpoints (`Authorization: Bearer <jwt>` required):
  - `POST /bouts/{bout_id}/escrows/prepare`
  - `POST /bouts/{bout_id}/escrows/confirm` (`Idempotency-Key` required)
  - `POST /bouts/{bout_id}/result` (admin-only)
  - `POST /bouts/{bout_id}/payouts/prepare`
  - `POST /bouts/{bout_id}/payouts/confirm` (`Idempotency-Key` required)
- Core domain utilities:
  - money conversion and drop validation
  - time rules and Ripple epoch conversion
- crypto-condition preimage/condition/fulfillment helpers for bonus escrow control
- XRPL transaction behavior:
  - unsigned `EscrowCreate`, `EscrowFinish`, and `EscrowCancel` payload generation
  - validated-ledger confirmation checks (`tesSUCCESS` + invariant/timing/offer-sequence matching)
- Replay-safe idempotency storage and mismatch rejection for confirm calls (`escrows/confirm` and `payouts/confirm`)
- Audit logging for escrow create/payout and bout lifecycle outcomes
- PostgreSQL schema foundation in `sql/001_init_schema.sql`

## Structure

- `app/api/`: route definitions
- `app/services/`: service-layer business logic
- `app/middleware/`: request guard helpers (idempotency header enforcement)
- `app/crypto_conditions/`: bonus preimage/condition/fulfillment helpers
- `app/models/`: SQLAlchemy models and enums
- `app/domain/`: pure domain utilities
- `app/core/`: config and security helpers
- `app/db/`: database session and init helpers
- `tests/`: unit/property/contract/security/migration tests

## Mandatory Pre-M4 Refactor (Implemented)

Implemented clean architecture hardening:

- Standardize transaction ownership with a lightweight Unit of Work for create/result/confirm flows.
- Introduce selective repositories only where duplicated query/state-loading logic is reduced:
  - `Bout`
  - `Escrow`
  - `IdempotencyKey`
  - `AuditLog`
- Preserve all API contracts, lifecycle semantics, and MVP invariants (`R-01`..`R-12`).
- Explicitly reject a generic repository-per-table CRUD abstraction.

## Mandatory Next Increment (Pre-M4 Closeout)

This modernization is required before hardening closeout:

- Adopt Alembic as authoritative migration system for schema evolution.
- Require deterministic revision governance and tested upgrade plus downgrade paths.
- Replace bespoke auth primitives with a proven maintained auth library.
- Preserve locked auth constraints:
  - email/password plus JWT only
  - no wallet-based login
- Preserve API contracts and lifecycle semantics unless explicitly versioned and documented.

## Notes

- Use the project virtual environment for local commands (`.\venv\Scripts\python.exe ...`) to ensure FastAPI/SQLAlchemy/dev tooling are available.
- Current suite entrypoint: `python -m unittest discover -s backend/tests -p "test_*.py"`.
