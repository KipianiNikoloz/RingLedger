# RingLedger Testnet Release Readiness Memo

Date: 2026-05-15
Milestone: Testnet release readiness after M4 closeout
Scope type: release evidence and operational readiness only

## Decision

RingLedger is ready to enter operator-run XRPL Testnet release validation. The deterministic 2026-07-30 hardening gates are green; the remaining live smoke requires credentials, funded accounts, and external Testnet/Xaman availability.

This memo does not expand MVP scope. It records the release boundary, required evidence, and residual risks for deploying the locked MVP to a Testnet environment.

## Locked Release Scope

- XRPL Testnet only.
- Xaman non-custodial promoter signing only.
- Email/password plus JWT auth only.
- XRP drops integer money model only.
- 1v1 bout model with `show_a`, `show_b`, `bonus_a`, and `bonus_b` escrows.
- Backend-authoritative lifecycle transitions after validated ledger evidence.
- Deterministic local and CI validation must not require live Xaman credentials or XRPL Testnet availability.

## Required Environment

Non-secret configuration:

- `XAMAN_MODE=api` for live Testnet release smoke validation.
- XRPL Testnet RPC configuration appropriate for the deployment environment.
- Public frontend API base URL pointing at the release backend.

Secrets and credentials:

- `XAMAN_API_KEY`
- `XAMAN_API_SECRET`
- strong environment-managed `JWT_SECRET`
- funded Testnet accounts and signing access controlled outside the repository

Secrets must never be committed, pasted into release notes, or captured in evidence. Release evidence may include non-secret payload identifiers, transaction hashes, request paths, status codes, and summarized command results.

## Release Gate Evidence

The release candidate must have current evidence for:

- backend syntax, lint, format, migration, full test, regression, and performance gates
- frontend typecheck, unit/integration, production build, and browser E2E gates
- OpenSpec validation for the active release-readiness change
- secret-scan and CI quality jobs on the merge commit when run in GitHub
- live Testnet smoke validation performed by an operator with environment-managed secrets

## Live Smoke Checklist

1. Boot the backend in the release environment with `XAMAN_MODE=api`.
2. Confirm `GET /healthz` succeeds.
3. Bootstrap/authenticate the first admin, provision the promoter through `POST /admin/users`, and register fighters publicly.
4. Create or verify fighter profiles with funded XRPL Testnet addresses.
5. Create a promoter bout draft and confirm the four-escrow plan.
6. Prepare escrow signing and verify Xaman returns a sign-request payload identifier.
7. Complete promoter signing in Xaman and reconcile signing status.
8. Confirm escrow creation only after validated XRPL Testnet `tesSUCCESS` evidence.
9. Enter the bout result as an authorized admin.
10. Prepare payout signing, complete/reconcile Xaman signing, and confirm payout only after validated XRPL Testnet evidence.
11. Record non-secret evidence: environment mode, request paths, payload identifiers, transaction hashes, command summaries, and any deterministic failure codes encountered.

## Current Deterministic Evidence

Evidence captured on 2026-07-30 from the release-hardening branch:

| Gate | Result |
|---|---|
| Locked Ruff lint | pass |
| Locked backend suite | pass (`111 passed`, `34 subtests passed`) |
| Frontend typecheck and production build | pass |
| Vitest | pass (`11 passed`) |
| Playwright Chromium | pass (`2 passed`) |
| `npm audit` | pass (`0 vulnerabilities`) |
| Compose configuration | pass |
| Non-root backend and frontend image builds | pass |

Live Xaman/XRPL transaction execution is intentionally not represented by these deterministic gates and remains the operator-run release validation step.

## Historical Verification Evidence

The following results are the 2026-05-15 baseline, not current completion evidence. They must be replaced by a clean-checkout verification run after release hardening.

| Gate | Result | Notes |
|---|---|---|
| `.\venv\Scripts\python.exe -m compileall backend/app backend/tests` | pass | Syntax validation completed. |
| `.\venv\Scripts\python.exe -m ruff check backend` | pass | Backend lint gate is clean. |
| `.\venv\Scripts\python.exe -m ruff format --check backend docs` | pass | Backend/docs format check is clean. |
| `.\venv\Scripts\python.exe -m pytest backend/tests -q` | pass (`90 passed`, `15 subtests passed`) | One non-blocking FastAPI/Starlette deprecation warning for the 422 constant. |
| `.\venv\Scripts\python.exe -m pytest backend/tests/regression backend/tests/performance -q` | pass (`10 passed`, `15 subtests passed`) | Deterministic M4 regression/performance gates. |
| `.\venv\Scripts\python.exe -m alembic -c backend/alembic.ini history` | pass | Baseline revision head: `202602220000_baseline_schema`. |
| `npm run typecheck` (`frontend/`) | pass | TypeScript validation completed. |
| `npm run test` (`frontend/`) | pass (`10 passed`) | Vitest suite completed. |
| `npm run build` (`frontend/`) | pass | Production build completed. |
| `npm run test:e2e` (`frontend/`) | pass (`1 passed`) | Required installing the matching local Playwright Chromium runtime before rerun. |
| `openspec validate prepare-testnet-release` | pass | Change is valid. |
| Live Xaman/XRPL smoke validation | operator-run | Requires live credentials and funded Testnet accounts outside local CI. |

## Residual Risks

- Xaman API or XRPL Testnet outages can block live smoke validation even when local/CI gates are green.
- Testnet funding, account state, and transaction finality are operational dependencies outside the repository.
- Release evidence depends on operators capturing identifiers and summaries without recording secrets.
- Mainnet readiness remains explicitly out of scope.
