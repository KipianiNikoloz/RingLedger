# RingLedger Backend (M2 Escrow Create Flow)

## Current Scope

- FastAPI application bootstrap (`app/main.py`)
- Health endpoint (`GET /healthz`)
- Auth endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
- Escrow create endpoints:
  - `POST /bouts/{bout_id}/escrows/prepare`
  - `POST /bouts/{bout_id}/escrows/confirm` (`Idempotency-Key` required)
- Core domain utilities:
  - money conversion and drop validation
  - time rules and Ripple epoch conversion
- XRPL create transaction behavior:
  - unsigned EscrowCreate payload generation
  - validated-ledger confirmation field checks (`tesSUCCESS` + invariant matching)
- Replay-safe idempotency storage and mismatch rejection for confirm calls
- Audit logging for escrow confirm success/rejection outcomes
- PostgreSQL schema foundation in `sql/001_init_schema.sql`

## Structure

- `app/api/`: route definitions
- `app/services/`: service-layer business logic
- `app/middleware/`: request guard helpers (idempotency header enforcement)
- `app/models/`: SQLAlchemy models and enums
- `app/domain/`: pure domain utilities
- `app/core/`: config and security helpers
- `app/db/`: database session and init helpers
- `tests/`: unit/property/contract/security/migration tests

## Notes

- Use the project virtual environment for local commands (`.\venv\Scripts\python.exe ...`) to ensure FastAPI/SQLAlchemy/dev tooling are available.
- Current suite entrypoint: `python -m unittest discover -s backend/tests -p "test_*.py"`.
