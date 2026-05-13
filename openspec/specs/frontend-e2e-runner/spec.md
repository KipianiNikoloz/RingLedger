# frontend-e2e-runner Specification

## Purpose
Defines the deterministic frontend browser-test runner lifecycle for starting the local operator workspace, executing Playwright, and cleaning up owned server processes.
## Requirements
### Requirement: Stable frontend E2E command
The system SHALL provide a frontend E2E command that starts the local browser-test server, runs Playwright, and exits with the actual test result.

#### Scenario: E2E command exits after passing browser journey
- **WHEN** `npm run test:e2e` is executed from `frontend/`
- **THEN** the command runs the Playwright browser journey and exits successfully when the journey passes

#### Scenario: E2E command cleans up owned server
- **WHEN** the E2E runner starts the local Vite server
- **THEN** the runner terminates that owned server process before exiting

#### Scenario: E2E command propagates browser-test failure
- **WHEN** Playwright reports a browser-test failure
- **THEN** the E2E command exits with a non-zero status
