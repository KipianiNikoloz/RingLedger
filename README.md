# RingLedger

RingLedger is an XRPL Testnet escrow settlement system for fighter purses. The locked MVP uses FastAPI, PostgreSQL, React, Xaman promoter signing, backend-enforced lifecycle guards, and XRP drops-only accounting.

## System At A Glance

```mermaid
flowchart TD
    operator[Operator console<br/>React] --> api[FastAPI backend]
    api --> auth[Email/password + JWT]
    api --> lifecycle[Bout lifecycle services]
    lifecycle --> db[(PostgreSQL)]
    lifecycle --> xrpl[XRPL escrow validation]
    lifecycle --> xaman[Xaman sign requests]
    lifecycle --> crypto[Bonus crypto conditions]
    xaman --> promoter[Promoter wallet signing]
    promoter --> xrpl
    xrpl --> api
```

## Current Status

- M1 through M4 are complete for the locked MVP/Testnet scope.
- Testnet release readiness is documented; live Xaman/XRPL smoke validation remains operator-run with environment-managed secrets.
- OpenSpec changes for release readiness and documentation overhaul are archived and synced into main specs.
- CI enforces backend tests, frontend tests, browser E2E, docs validation, and secret scanning.

## Locked MVP Scope

| Area | Constraint |
|---|---|
| Network | XRPL Testnet only |
| Auth | Email/password plus JWT only; no wallet login |
| Money | XRP drops as integers |
| Bout model | 1v1 with `show_a`, `show_b`, `bonus_a`, `bonus_b` escrows |
| Custody | Platform controls bonus fulfillment; promoter controls signatures |
| Signing | Xaman non-custodial signing; backend never stores promoter private keys |
| Timing | `FinishAfter = event_datetime_utc + 2h`; bonus `CancelAfter = event_datetime_utc + 7d` |
| Ledger truth | State transitions only after validated XRPL `tesSUCCESS` |
| Frontend trust | Frontend is advisory; backend enforces invariants |

## Lifecycle Overview

```mermaid
stateDiagram-v2
    [*] --> draft
    draft --> escrows_created: 4 EscrowCreate confirmations
    escrows_created --> result_entered: admin winner entry
    result_entered --> payouts_in_progress: first payout confirm
    payouts_in_progress --> closed: all required payouts complete

    draft --> draft: prepare/sign/reconcile no transition
    result_entered --> result_entered: payout prepare/sign/reconcile no transition
```

## Maintainer Documentation Map

Start at the README closest to the code you are changing. These module-local READMEs explain responsibility, flow, tests, and related contracts.

### Backend

| Module | README |
|---|---|
| Backend app overview | `backend/app/README.md` |
| HTTP routes | `backend/app/api/README.md` |
| Bout route modules | `backend/app/api/bouts_routes/README.md` |
| Config and security | `backend/app/core/README.md` |
| Crypto conditions | `backend/app/crypto_conditions/README.md` |
| Database and Unit of Work | `backend/app/db/README.md` |
| Pure domain rules | `backend/app/domain/README.md` |
| External integrations | `backend/app/integrations/README.md` |
| Middleware/request guards | `backend/app/middleware/README.md` |
| Persistence models | `backend/app/models/README.md` |
| Repositories | `backend/app/repositories/README.md` |
| API schemas | `backend/app/schemas/README.md` |
| Service layer | `backend/app/services/README.md` |
| Backend tests | `backend/tests/README.md` |

### Frontend

| Module | README |
|---|---|
| Frontend source overview | `frontend/src/README.md` |
| Typed API client | `frontend/src/api/README.md` |
| App shell | `frontend/src/app/README.md` |
| UI components | `frontend/src/components/README.md` |
| Workflow hooks | `frontend/src/hooks/README.md` |

## Canonical Reference Docs

| Contract | Document |
|---|---|
| Requirements | `docs/requirements-matrix.md` |
| API | `docs/api-spec.md` |
| Lifecycle states | `docs/state-machines.md` |
| Schema | `docs/schema-doc.md` |
| Traceability | `docs/traceability-matrix.md` |
| Operations | `docs/operations-runbook.md` |
| Operator flow | `docs/operational-flow.md` |
| Xaman signing | `docs/xaman-signing-contract.md` |
| Testnet release | `docs/testnet-release-readiness.md` |
| CI/CD | `docs/ci-cd.md` |

## Repository Layout

```mermaid
flowchart LR
    repo[RingLedger] --> backend[backend]
    repo --> frontend[frontend]
    repo --> docs[docs]
    repo --> openspec[openspec]
    backend --> app[backend/app]
    backend --> tests[backend/tests]
    frontend --> src[frontend/src]
    docs --> contracts[reference and operations docs]
    openspec --> specs[specs and archived changes]
```

## Local Verification

```powershell
.\venv\Scripts\python.exe -m ruff check backend
.\venv\Scripts\python.exe -m ruff format --check backend docs
.\venv\Scripts\python.exe -m pytest backend/tests -q
cd frontend
npm run typecheck
npm run test
npm run test:e2e
```

## Delivery Rules

- Keep changes in small vertical slices.
- Every code/config/schema change needs matching tests and docs.
- Maintain requirement -> implementation -> tests -> docs traceability.
- Preserve the locked MVP scope unless a new OpenSpec change explicitly changes it.
