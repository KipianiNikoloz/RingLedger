## Why

The release audit found that the browser can assert ledger finality and privileged roles can self-register, so the current implementation does not satisfy its backend-authoritative security contract. Dependency drift, non-deterministic test startup, and the absence of a runnable release stack also prevent repeatable Testnet release evidence.

## What Changes

- **BREAKING** Reduce escrow and payout confirmation requests to `escrow_kind` plus `tx_hash`; fetch and validate all final evidence from XRPL Testnet API v2.
- **BREAKING** Restrict public registration to fighters and add admin-authorized privileged-user provisioning plus secret-safe first-admin bootstrap.
- Add Testnet network verification, retryable ledger-pending semantics, deterministic idempotency, and unique non-null transaction hashes.
- Add readiness and production configuration validation, including safe secrets and CORS.
- Commit a universal Python lock, align all CI gates, and make frontend tests deterministically fail on missing or unhandled tests.
- Add non-root backend/frontend images, PostgreSQL migration orchestration, same-origin API proxying, example configuration, and container smoke checks.
- Keep the existing frontend functional against the breaking contracts before the later visual redesign.

## Capabilities

### New Capabilities

- `xrpl-ledger-confirmation`: Backend-authoritative Testnet transaction lookup, validation, retry, and replay behavior.
- `privileged-role-provisioning`: Fighter-only public signup, admin-created privileged users, and first-admin bootstrap.
- `release-runtime`: Reproducible dependencies, deterministic verification, production configuration, health/readiness, and container delivery.

### Modified Capabilities

- `testnet-release-readiness`: Require authoritative ledger confirmation, privileged-role security, reproducible clean-checkout gates, and container smoke evidence before live validation.
- `mvp-management-endpoints`: Add the admin user-provisioning management contract.

## Impact

This change affects confirmation and auth APIs, frontend request types and forms, XRPL integration services, idempotency behavior, database indexes and Alembic history, application configuration and middleware, CI, dependency management, container manifests, operations documentation, and release evidence. Existing pre-release clients must adopt the new request bodies.
