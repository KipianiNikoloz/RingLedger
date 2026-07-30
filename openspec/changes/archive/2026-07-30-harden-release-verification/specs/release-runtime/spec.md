## ADDED Requirements

### Requirement: Reproducible verification environment
The repository SHALL commit a universal Python lock and SHALL run backend and frontend gates from locked clean installations.

#### Scenario: Dependency metadata drifts
- **WHEN** project dependency declarations do not match the committed lock
- **THEN** local or CI locked verification fails before tests execute

#### Scenario: Frontend tests cannot start
- **WHEN** no test is collected or an unhandled worker error occurs
- **THEN** the frontend test gate exits non-zero

### Requirement: Production configuration safety
The backend SHALL fail startup in production when secrets, signing mode, XRPL endpoint, CORS, or migration configuration is unsafe.

#### Scenario: Production uses default secret
- **WHEN** production starts with the default or a short JWT secret
- **THEN** startup fails without printing the secret

### Requirement: Health and readiness separation
The system SHALL expose process liveness separately from database and XRPL Testnet readiness.

#### Scenario: External dependency is unavailable
- **WHEN** the process is running but the database or XRPL Testnet is unavailable
- **THEN** `/healthz` remains healthy while `/readyz` reports unavailable

### Requirement: Containerized release stack
The repository SHALL provide non-root backend and frontend images plus Compose orchestration for PostgreSQL, one-shot migrations, API startup, and same-origin SPA delivery.

#### Scenario: Stack starts from documented configuration
- **WHEN** an operator supplies the documented non-secret settings and secret files and runs Compose
- **THEN** PostgreSQL becomes healthy, migrations complete once, the API becomes live, and Nginx serves SPA routes and proxies `/api`
