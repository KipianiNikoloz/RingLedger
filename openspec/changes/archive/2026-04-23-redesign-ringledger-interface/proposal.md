## Why

RingLedger's frontend needs to communicate that backend and XRPL evidence are the source of truth for escrow settlement work. The current interface should be redesigned into a dense, auditable operator workspace that keeps lifecycle state, signing state, backend responses, and ledger evidence visible while preserving existing workflow behavior.

## What Changes

- Redesign `/app` as a dark operator console with a header, four-stage lifecycle stepper, left context rail, central workflow area, right evidence rail, and bottom trust-boundary legend.
- Redesign `/` as a concise dark product entry screen that routes users into `/app` without becoming a marketing-heavy landing page.
- Restyle and reorganize existing workflow panels so authentication, escrow, result entry, payout, JSON output, action log, and error states remain accessible.
- Derive lifecycle stage states from existing frontend workflow state where possible.
- Preserve API client behavior, backend contracts, routes, workflow hooks, test IDs, and core user flows.
- Avoid new runtime dependencies unless implementation proves a focused helper is necessary.

## Capabilities

### New Capabilities
- `operator-console-interface`: Covers the dark, evidence-first RingLedger frontend interface for `/` and `/app`, including lifecycle navigation, trust-boundary visual language, responsive layout, and workflow evidence visibility.

### Modified Capabilities

## Impact

- Affected code: `frontend/src/app/AppShell.tsx`, `frontend/src/styles.css`, and potentially focused updates to frontend component markup and tests.
- Affected tests: `frontend/src/App.test.tsx` and Playwright route/flow assertions if visible copy changes.
- APIs and backend systems: no backend API contract or workflow semantic changes.
- Dependencies: no planned new runtime dependencies.
