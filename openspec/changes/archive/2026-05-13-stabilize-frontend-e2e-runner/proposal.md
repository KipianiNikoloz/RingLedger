## Why

The frontend browser journey is passing but the local `npm run test:e2e` command hangs during Playwright web-server teardown on Windows. Stabilizing the runner makes the E2E gate usable as release evidence instead of relying on a partial pass before timeout.

## What Changes

- Replace Playwright's built-in `webServer` launcher with an explicit npm runner script.
- Start Vite as a child process, wait for the local test server, run Playwright, and always clean up the child process.
- Keep the existing browser journey and base URL contract unchanged.
- Document the stable E2E command and update verification evidence.

## Capabilities

### New Capabilities
- `frontend-e2e-runner`: deterministic frontend browser-test command lifecycle for the operator workspace.

### Modified Capabilities
- `operator-console-interface`: browser-level verification remains required for the operator workspace but uses the stable runner lifecycle.

## Impact

- Frontend package scripts and Playwright config.
- A small Node runner under `frontend/scripts/`.
- Frontend README and traceability evidence.
