## 1. Context and Layout

- [x] 1.1 Inspect existing frontend shell, workflow panels, hook state, unit tests, and Playwright flow expectations.
- [x] 1.2 Refactor `AppShell.tsx` to compute lifecycle stage summaries and render `/` plus `/app` using the new operator-console route structure.

## 2. Visual System

- [x] 2.1 Replace the global stylesheet with the dark trust-boundary design system, compact controls, panel primitives, lifecycle stepper, rails, evidence surfaces, and responsive breakpoints.
- [x] 2.2 Adjust existing panel markup only where needed so workflow controls, labels, JSON output, errors, and action logs fit the dense console layout.

## 3. Evidence and State

- [x] 3.1 Surface latest backend response, signing request details, ledger evidence, action log, and failure classification in the right rail without changing workflow semantics.
- [x] 3.2 Add the bottom trust-boundary legend and ensure stage/state colors map consistently across the workspace.

## 4. Verification

- [x] 4.1 Update unit and e2e assertions only where visible copy or route structure intentionally changed.
- [x] 4.2 Run `npm run typecheck`, `npm test`, `npm run build`, and `npm run test:e2e` when practical; inspect responsive layout for overflow or unusable controls.
