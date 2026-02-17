# CI/CD and Dependency Automation

Last updated: 2026-02-16

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
   - test gate: `python -m unittest discover -s backend/tests -p "test_*.py"`
2. `secret-scan`
   - full checkout history
   - `gitleaks` repository scan
3. `delivery`
   - runs only on push to `main` or `master`
   - requires `quality` and `secret-scan` pass
   - publishes artifact: `ringledger-m1-foundation.tgz`

## Dependabot

Config file: `.github/dependabot.yml`

### Update streams

- `github-actions`: weekly Monday updates
- `pip`: weekly Monday updates for Python dependency manifests

Both streams use commit prefix `chore(deps)`.

## Local Pre-PR Commands

Run these locally before opening/updating a PR:

```bash
python -m compileall backend/app backend/tests
ruff format --check backend
ruff check backend
python -m unittest discover -s backend/tests -p "test_*.py"
```

## Security Notes

- Secret scanning blocks merges when leaks are detected.
- Default/demo values (for example local JWT secrets) must never be used in production deployments.
- Runtime production secrets must come from deployment environment secret stores, not from repository files.

