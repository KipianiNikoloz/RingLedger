# RingLedger Backend (M4 Hardening Complete)

## Current Scope

- FastAPI application bootstrap (`app/main.py`)
- Health endpoint (`GET /healthz`)
- Auth endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
- Fighter profile endpoint:
  - `PUT /fighters/me`
- Bout management endpoints:
  - `POST /bouts`
  - `GET /bouts`
  - `GET /bouts/{bout_id}`
- Protected bout lifecycle endpoints (`Authorization: Bearer <jwt>` required):
  - `POST /bouts/{bout_id}/escrows/prepare`
  - `POST /bouts/{bout_id}/escrows/signing/reconcile`
  - `POST /bouts/{bout_id}/escrows/confirm` (`Idempotency-Key` required)
  - `POST /bouts/{bout_id}/result` (admin-only)
  - `POST /bouts/{bout_id}/payouts/prepare`
  - `POST /bouts/{bout_id}/payouts/signing/reconcile`
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
  - `signing_declined`, `signing_expired`, `confirmation_timeout`, `ledger_tec_tem`, `invalid_confirmation`
  - failures are persisted/audited and never advance state
- Frontend-consumer contract coverage behavior:
  - backend-driven E2E journey tests validate frontend-expected API contracts before React screens are implemented
  - critical journeys cover login-to-closeout and declined-signing replay-safe handling
- Replay-safe idempotency storage and mismatch rejection for confirm calls (`escrows/confirm` and `payouts/confirm`)
- Audit logging for escrow create/payout and bout lifecycle outcomes
- Alembic-governed PostgreSQL schema evolution with baseline revision

## Structure

- `app/api/`: route definitions
- `app/api/bouts_routes/`: thin `/bouts` route modules (`escrow`, `payout`, `signing`) plus shared route helpers
- `app/services/`: service-layer business logic
- `app/middleware/`: request guard helpers (idempotency header enforcement)
- `app/crypto_conditions/`: bonus preimage/condition/fulfillment helpers
- `app/models/`: SQLAlchemy models and enums
- `app/domain/`: pure domain utilities
- `app/core/`: config and security helpers
- `app/integrations/`: Xaman sign-request integration boundary
- `app/db/`: database session and init helpers
- `tests/`: unit/property/contract/security/migration tests

Module-level maintainer documentation starts at `backend/app/README.md` and `backend/tests/README.md`.

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

## M4 Closeout Status

M4 hardening is complete for the locked MVP/Testnet scope. Residual risk remains bounded to deployment operations and real external XRPL/Xaman availability; runtime lifecycle authority, failure taxonomy, signing reconciliation, management endpoints, and regression/performance evidence are implemented and documented.

## Notes

- Use the project virtual environment for local commands (`.\venv\Scripts\python.exe ...`) to ensure FastAPI/SQLAlchemy/dev tooling are available.
- Current suite entrypoint: `python -m pytest backend/tests -q`.
- Frontend package and browser tests are under `frontend/` (`npm run test`, `npm run test:e2e`).
- Xaman integration runtime mode is controlled by `XAMAN_MODE`:
  - `stub` (default): deterministic non-network sign-request envelopes for local/CI.
  - `api`: calls Xaman API using `XAMAN_API_KEY` and `XAMAN_API_SECRET`.
