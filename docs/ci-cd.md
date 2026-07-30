# RingLedger CI/CD and Dependency Automation

Last updated: 2026-07-30

## Required Workflow

`.github/workflows/verify.yml` runs on every push and pull request with clean, locked installs. Its independent gates cover backend lint/format/tests, frontend typecheck/tests/build, both container builds, and a pinned Gitleaks scan of full history.

The Playwright browser contract remains a required local/release gate via `npm run test:e2e`; it uses the locally installed matching Chromium runtime.

## Local Pre-PR Gates

```powershell
uv sync --locked --extra dev
uv run --locked --extra dev ruff check backend
uv run --locked --extra dev ruff format --check backend docs
uv run --locked --extra dev pytest backend/tests -q
uv run --locked --extra dev alembic -c backend/alembic.ini history
cd frontend
npm ci
npm run typecheck
npm test
npm run build
npm run test:e2e
cd ..
docker compose config
docker build -f Dockerfile.backend -t ringledger-api .
docker build -f Dockerfile.frontend -t ringledger-web .
```

## Release Rules

- Dependency declarations and `uv.lock`/`package-lock.json` stay synchronized.
- Production schema changes run through the one-shot Compose migration service; the API never auto-migrates in production.
- Runtime secrets use deployment secret files and are excluded from the Docker build context.
- Live Xaman/XRPL evidence contains identifiers and summaries only—never credentials or secret material.
