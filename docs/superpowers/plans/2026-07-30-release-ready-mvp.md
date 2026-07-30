# RingLedger Release-Ready MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a secure, reproducible, containerized XRPL Testnet MVP with continuously maintained documentation and an avant-garde operator interface.

**Architecture:** Three sequential OpenSpec changes isolate documentation governance, release/security hardening, and frontend closeout. The backend becomes the exclusive ledger-evidence authority, privileged roles become admin-provisioned, and a same-origin container stack packages the API, migrations, database, and SPA.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL 16, uv, React 19, TypeScript, Vite, Vitest, Playwright, Nginx, Docker Compose, XRPL JSON-RPC v2, Xaman.

## Global Constraints

- Preserve the locked XRPL Testnet MVP and its four-escrow 1v1 lifecycle.
- Never store promoter private keys or include credentials in source, docs, logs, commits, images, or release evidence.
- Keep documentation synchronized with every affected behavior and contract.
- Use feature branches, OpenSpec artifacts, test-first behavior changes, atomic commits, and clean verification before merge.
- Treat frontend checks as UX only; backend and validated XRPL evidence remain authoritative.

---

### Task 1: Documentation Governance

**Produces:** Root agent guidance, repaired canonical docs, validated module documentation, and archived `establish-documentation-governance` change.

- [ ] Create and validate the OpenSpec proposal, design, specs, and tasks.
- [ ] Add root `AGENTS.md` with the documentation directive before all other instructions.
- [ ] Repair current OpenSpec purposes, configuration names, commands, links, dates, and traceability.
- [ ] Run documentation and OpenSpec gates, commit cohesive increments, and archive the change.

### Task 2: Ledger and Authorization Hardening

**Produces:** Backend-fetched XRPL confirmation, fighter-only registration, admin provisioning, safe runtime configuration, migrations, and compatible frontend requests.

- [ ] Create `harden-release-verification` OpenSpec artifacts on `feat/release-verification-hardening`.
- [ ] Add failing unit/contract/integration tests for XRPL API v2 evidence and retryable idempotency.
- [ ] Implement the injected Testnet ledger client and two-field confirmation contracts.
- [ ] Add failing auth tests, then implement fighter registration, admin user creation, and first-admin bootstrap.
- [ ] Add reversible unique-transaction migration, readiness, CORS, and production configuration validation.
- [ ] Update frontend types and workflows so the branch remains fully functional.

### Task 3: Reproducible Delivery

**Produces:** Locked Python dependencies, deterministic CI, production images, Compose orchestration, and release artifacts.

- [ ] Commit `uv.lock` and convert local/CI commands to locked uv execution.
- [ ] Make frontend tests fail on zero tests or unhandled errors and serialize test files.
- [ ] Align CI with pytest, migrations, frontend build/E2E, OpenSpec, secret scan, and container validation.
- [ ] Add non-root backend/frontend images, PostgreSQL health, one-shot migration, Nginx `/api` proxying, `.env.example`, and smoke verification.
- [ ] Update operational documentation, pass all gates, and archive `harden-release-verification`.

### Task 4: Split Decision Frontend

**Produces:** A responsive, accessible, distinctive home and operator workspace without changing backend lifecycle authority.

- [ ] Create `close-release-ready-mvp` OpenSpec artifacts on `feat/release-readiness-closeout`.
- [ ] Add behavior tests for navigation, lifecycle stages, ledger retry, admin provisioning, evidence, and responsive access.
- [ ] Split the application shell into focused page and workspace units.
- [ ] Implement the approved typography, color, rhythm, clipped-frame, motion, and trust-boundary system.
- [ ] Add keyboard, reduced-motion, automated accessibility, mobile/tablet, and no-overflow Playwright coverage.

### Task 5: Release Closeout

**Produces:** Clean-checkout evidence and archived capability contracts without overstating live release validation.

- [ ] Run backend, frontend, migration, OpenSpec, secret, Docker, Compose, and artifact gates from a clean dependency installation.
- [ ] Fix every discovered locked-scope defect through root-cause analysis and a failing regression test.
- [ ] Synchronize API, schema, lifecycle, operations, CI, README, module, and traceability documents.
- [ ] Record deterministic evidence, retain live Xaman/XRPL smoke as operator-pending, and archive the final change.
