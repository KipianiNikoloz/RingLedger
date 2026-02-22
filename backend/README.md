# RingLedger Backend (M4 Hardening In Progress)

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
- Xaman signing integration behavior:
  - prepare endpoints return per-transaction sign-request metadata (`payload_id`, deep link, QR URL)
  - backend remains non-custodial and never stores promoter private keys
- Explicit confirm failure taxonomy behavior:
  - `signing_declined`, `confirmation_timeout`, `ledger_tec_tem`, `invalid_confirmation`
  - failures are persisted/audited and never advance state
- Replay-safe idempotency storage and mismatch rejection for confirm calls (`escrows/confirm` and `payouts/confirm`)
- Audit logging for escrow create/payout and bout lifecycle outcomes
- Alembic-governed PostgreSQL schema evolution with baseline revision

## Structure

- `app/api/`: route definitions
- `app/services/`: service-layer business logic
- `app/middleware/`: request guard helpers (idempotency header enforcement)
- `app/crypto_conditions/`: bonus preimage/condition/fulfillment helpers
- `app/models/`: SQLAlchemy models and enums
- `app/domain/`: pure domain utilities
- `app/core/`: config and security helpers
- `app/integrations/`: Xaman sign-request integration boundary
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

## Mandatory Modernization (Implemented Pre-M4 Closeout)

Implemented modernization scope:

- Adopt Alembic as authoritative migration system for schema evolution.
- Require deterministic revision governance and tested upgrade plus downgrade paths.
- Replace bespoke auth primitives with a proven maintained auth library.
- Preserve locked auth constraints:
  - email/password plus JWT only
  - no wallet-based login
- Preserve API contracts and lifecycle semantics unless explicitly versioned and documented.

## Next Increment (M4 Hardening Closeout)

- Continue residual hardening scope for operational readiness and risk burn-down.
- Focus areas:
  - Xaman integration hardening completion (`R-06`) after initial sign-request contract delivery
  - failure taxonomy expansion after initial declined/timeout/`tec`/`tem` delivery (`R-12`)
  - e2e/frontend journey coverage (`R-01`, `R-10`)
  - regression/performance baselines and runbook completion

## Notes

- Use the project virtual environment for local commands (`.\venv\Scripts\python.exe ...`) to ensure FastAPI/SQLAlchemy/dev tooling are available.
- Current suite entrypoint: `python -m pytest backend/tests -q`.
- Xaman integration runtime mode is controlled by `XAMAN_MODE`:
  - `stub` (default): deterministic non-network sign-request envelopes for local/CI.
  - `api`: calls Xaman API using `XAMAN_API_KEY` and `XAMAN_API_SECRET`.
