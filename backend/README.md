# FightPurse Backend (M1 Foundation)

## Current Scope

- FastAPI application bootstrap (`app/main.py`)
- Health endpoint (`GET /healthz`)
- Auth endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
- Core domain utilities:
  - money conversion and drop validation
  - time rules and Ripple epoch conversion
- PostgreSQL schema foundation in `sql/001_init_schema.sql`

## Structure

- `app/api/`: route definitions
- `app/services/`: service-layer business logic
- `app/models/`: SQLAlchemy models and enums
- `app/domain/`: pure domain utilities
- `app/core/`: config and security helpers
- `app/db/`: database session and init helpers
- `tests/`: unit/property/contract/security/migration tests

## Notes

- The environment used for this implementation does not have external packages installed.
- Code and tests are scaffolded for the declared stack; dependency install and full test execution are required in CI/local dev environment.
