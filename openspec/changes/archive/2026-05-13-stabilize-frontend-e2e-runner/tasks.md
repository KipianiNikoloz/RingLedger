## 1. Runner Implementation

- [x] 1.1 Add a frontend E2E runner script that starts Vite, waits for readiness, runs Playwright, and cleans up the owned server process.
- [x] 1.2 Update `npm run test:e2e` and Playwright config so the runner owns server lifecycle instead of Playwright `webServer`.

## 2. Documentation And Verification

- [x] 2.1 Update frontend and traceability docs with stable E2E runner behavior and current evidence.
- [x] 2.2 Run frontend E2E, typecheck, unit, and build gates; validate the OpenSpec change.
- [x] 2.3 Commit the completed runner slice with a detailed commit message.
