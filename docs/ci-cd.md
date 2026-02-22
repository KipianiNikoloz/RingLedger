# RingLedger CI/CD and Dependency Automation

Last updated: 2026-02-22

## Objectives

- Enforce formatting, linting, and test gates on every PR.
- Scan repository content for accidental secret leakage.
- Produce a minimal delivery artifact on protected branch pushes.
- Keep dependencies current with automated update PRs.

## GitHub Actions Workflow

Workflow file: `.github/workflows/ci-cd.yml`

### Triggers

- `push` to `main` or `master`
- `pull_request`
- manual `workflow_dispatch`

### Jobs

1. `quality`
   - Python `3.12` setup
   - install project + dev dependencies
   - syntax compile check: `python -m compileall backend/app backend/tests`
   - formatting gate: `ruff format --check backend`
   - lint gate: `ruff check backend`
   - test gate: `python -m unittest discover -s backend/tests -p "test_*.py"` (includes unit/integration/contract/security/migration/e2e packages)
2. `frontend-quality`
   - Node `22` setup
   - frontend dependency install (`npm install`)
   - frontend typecheck gate: `npm run typecheck`
   - frontend unit/integration gate: `npm run test`
   - frontend browser e2e gate:
     - `npx playwright install --with-deps chromium`
     - `npm run test:e2e -- --project=chromium`
3. `secret-scan`
   - full checkout history
   - `gitleaks` repository scan
4. `delivery`
   - runs only on push to `main` or `master`
   - requires `quality`, `frontend-quality`, and `secret-scan` pass
   - publishes artifact: `ringledger-m1-foundation.tgz` (backend + frontend + docs)

## Dependabot

Config file: `.github/dependabot.yml`

### Update streams

- `github-actions`: weekly Monday updates
- `pip`: weekly Monday updates for Python dependency manifests
- `npm`: weekly Monday updates for frontend dependencies in `frontend/`

Both streams use commit prefix `chore(deps)`.

## Local Pre-PR Commands

Run these locally before opening/updating a PR:

```bash
python -m compileall backend/app backend/tests
ruff format --check backend
ruff check backend
python -m pytest backend/tests -q
python -m alembic -c backend/alembic.ini history
(cd frontend && npm install && npm run typecheck && npm run test)
(cd frontend && npx playwright install --with-deps chromium && npm run test:e2e -- --project=chromium)
```

## Mandatory Modernization Gates (Pre-M4 Closeout)

The following verification gates are mandatory for migration/auth modernization acceptance:

- Alembic migration governance gates:
  - revision metadata required for each schema change.
  - upgrade and downgrade validation evidence required in CI/test reports.
  - no production policy allowing unsafe implicit startup migrations.
- Auth-library modernization gates:
  - objective library selection record with maintenance/security/compatibility criteria.
  - auth regression coverage for register/login/token/role guards/failure paths.
  - security checks for replay/authz/secret leakage parity.

These gates are additive to existing quality and secret-scan requirements.

Current evidence includes:

- `python -m pytest backend/tests -q` passing with full backend suite (including M4 Xaman integration/reconciliation and backend-driven frontend E2E journeys).
- `python -m alembic -c backend/alembic.ini history` showing baseline revision head.
- Frontend verification gates are now codified in CI (`frontend-quality`) and executed in GitHub runner environment.

## Security Notes

- Secret scanning blocks merges when leaks are detected.
- Default/demo values (for example local JWT secrets) must never be used in production deployments.
- Runtime production secrets must come from deployment environment secret stores, not from repository files.
