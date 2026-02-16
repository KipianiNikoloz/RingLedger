# FightPurse (RingLedger)

Escrow-based fighter purse settlement on XRPL Testnet, with promoter signing via Xaman and backend-enforced lifecycle/security invariants.

## Status

- Baseline product and technical documentation are in place.
- Implementation has started with backend/database M1 foundation scaffolding.

## MVP Scope (Locked)

- Stack: FastAPI (Python), PostgreSQL, React, XRPL Testnet, Xaman.
- Auth: email/password + JWT only (no wallet login).
- Money: XRP only, amounts in drops (integers), DB `BIGINT`.
- Bout model: 1v1 with 4 escrows: `show_a`, `show_b`, `bonus_a`, `bonus_b`.
- Custody split: platform controls bonus preimage/fulfillment; promoter controls signatures.
- Signing: promoter signs in Xaman; backend never stores promoter private keys.
- Timing: `FinishAfter = event_datetime_utc + 2h`; `CancelAfter = event_datetime_utc + 7d` (bonus only).
- Ledger truth: state transitions only after validated XRPL `tesSUCCESS`.
- Idempotency: required on confirm endpoints.
- Security: frontend untrusted, backend authoritative for all invariants.

## Core Docs

- Requirements baseline: `docs/requirements-matrix.md`
- Lifecycle contract: `docs/state-machines.md`
- Requirement traceability: `docs/traceability-matrix.md`

## Repository Layout

- `backend/`: FastAPI service scaffold, domain modules, SQL schema, and initial test suite.
- `docs/`: locked requirements, state machines, and implementation traceability.

## Implementation Roadmap (Current)

1. M1: backend + database foundation (`R-02`, `R-03`, `R-04`, `R-07`) - in progress.
2. M2: escrow create prepare/confirm with XRPL validation + idempotency.
3. M3: result entry and payout prepare/confirm with bonus fulfillment logic.
4. M4: hardening (security, failure paths, regression/performance, operational readiness).

## Delivery Rules

- Implement in small vertical slices with atomic commits.
- Every code/config/schema change must include matching tests and documentation updates.
- Maintain traceability: requirement -> implementation -> tests -> docs.
