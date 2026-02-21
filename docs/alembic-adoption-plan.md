# RingLedger Alembic Adoption Plan (Mandatory Pre-M4 Closeout)

Last updated: 2026-02-21

## Purpose

Define the mandatory migration modernization step that makes Alembic the authoritative schema evolution system.

This is maintainability/safety hardening, not feature expansion.

## Scope

- Adopt Alembic as the authoritative migration mechanism.
- Define deterministic revision naming and sequencing policy.
- Define migration validation policy requiring tested upgrades and downgrades.
- Define startup/runtime migration safety policy for production environments.
- Preserve existing API, lifecycle, and invariant behavior unless explicitly versioned and documented.

## Non-Goals

- No schema feature expansion unrelated to migration governance.
- No API contract changes.
- No lifecycle semantic changes.
- No wallet-login auth additions.

## Current-State Baseline

- Current bootstrap path includes SQLAlchemy `create_all` usage (`backend/app/db/init_db.py`).
- Current baseline schema artifact exists as static SQL (`backend/sql/001_init_schema.sql`).
- Migration authority and rollback governance are not yet Alembic-driven in project policy.

## Target-State Policy

- Alembic is authoritative for schema evolution.
- `create_all` is forbidden as production schema evolution mechanism.
- Each schema change requires:
  - deterministic Alembic revision metadata.
  - tested `upgrade` evidence.
  - tested `downgrade` evidence.
- Production runtime policy does not execute unsafe implicit migrations during app startup.

## Deterministic Revision Governance

- Revision naming format: `<UTCYYYYMMDDHHMM>_<short_slug>`.
- One logical schema concern per revision where practical.
- Every revision must include explicit downgrade logic or explicit documented waiver with owner and risk rationale.
- Revision review checklist includes requirement mapping and index/constraint impact note.

## Sequence

1. Establish Alembic environment/configuration and policy docs.
2. Baseline current schema into deterministic revision history.
3. Define and run upgrade plus downgrade validation workflow.
4. Update CI/CD and traceability requirements to enforce policy.
5. Publish acceptance evidence and residual risk statement.

## Acceptance Evidence

- Documented Alembic authority and revision policy.
- Migration validation evidence for upgrade and downgrade paths.
- CI/CD gate policy updates for migration checks.
- Traceability updates linking requirements, implementation, tests, and docs.
- No unapproved API/lifecycle contract drift.

## Rollback Strategy

- Technical rollback: execute validated Alembic downgrade path to last known good revision.
- Operational rollback: block further rollout, restore service via prior revision plus runbooked recovery checks.
- Documentation rollback: record incident, revision pair, impact scope, and corrective actions in traceability and runbook artifacts.

