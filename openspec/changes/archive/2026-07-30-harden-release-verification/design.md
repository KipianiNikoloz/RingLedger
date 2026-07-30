## Context

Confirmation endpoints currently accept browser-supplied finality, result, transaction, amount, timing, and fulfillment fields. Public registration also accepts every role. These violate the documented untrusted-frontend boundary. The repository additionally lacks locked Python resolution, deterministic local test startup, production configuration validation, and a complete container runtime.

## Goals / Non-Goals

**Goals:**

- Make XRPL Testnet API v2 the only source of confirmation evidence.
- Make transient ledger state safely retryable under existing idempotency semantics.
- Restrict privileged roles to admin-controlled provisioning.
- Provide reproducible clean-checkout verification and a runnable container stack.
- Keep the frontend functional throughout the breaking pre-release contract migration.

**Non-Goals:**

- Mainnet support, wallet login, background confirmation jobs, or a dispute workflow.
- Live network calls in deterministic tests or CI.
- The Split Decision visual redesign, which belongs to the next change.

## Decisions

1. **Use a small injected synchronous XRPL JSON-RPC client.** Routes are currently synchronous and the `tx` lookup is one bounded external call. `httpx.Client` provides explicit timeouts and testable transport injection without introducing a job system.
2. **Verify Testnet before accepting evidence.** The client calls `server_info` and requires network ID `1`, then calls API v2 `tx`. Confirmation derives all fields from `tx_json`, `meta`, and close-time data.
3. **Use terminal versus retryable failures.** Not-found or unvalidated transactions return `409 ledger_confirmation_pending` and upstream failures return `503 xrpl_unavailable`; neither is stored as an idempotent terminal response. Validated rejection and success are stored and replayed.
4. **Use partial unique indexes.** PostgreSQL unique indexes on each non-null transaction-hash column prevent one ledger transaction from settling multiple records while permitting existing null planned rows.
5. **Make public registration fighter-only.** `POST /auth/register` no longer accepts a role. Admins create promoter, management, and admin users through `POST /admin/users`; an idempotent bootstrap CLI accepts a password file or secure interactive input.
6. **Fail closed in production.** Production requires a strong non-default `JWT_SECRET`, Xaman API mode, HTTPS XRPL RPC URL, explicit safe CORS origins, and disabled automatic migrations.
7. **Separate liveness and readiness.** `/healthz` remains process-only. `/readyz` verifies database access and XRPL Testnet network identity without exposing provider details.
8. **Use uv and containers as release contracts.** `uv.lock` is committed; CI uses locked sync. Compose coordinates PostgreSQL health, one-shot Alembic migration, backend, and Nginx-served frontend with same-origin `/api` proxying.

## Risks / Trade-offs

- **Public RPC instability** → Bound timeouts, distinguish retryable transport state, and keep CI network-free.
- **Breaking clients** → Update the only checked-in client and all API docs in the same branch; the MVP is pre-release.
- **Bootstrap credential exposure** → Prefer password files or interactive entry and never echo secrets.
- **Container readiness depends on external Testnet** → Use liveness for container orchestration and expose external dependency state through `/readyz`.
- **Partial indexes can fail on existing duplicates** → Add a pre-migration duplicate assertion and migration contract tests.

## Migration Plan

1. Ship the reversible unique-index migration and new code together before live use.
2. Run Alembic upgrade as a one-shot deployment step before starting the backend.
3. Deploy the updated frontend with the backend because confirmation and registration bodies are breaking.
4. Bootstrap the first admin through a mounted secret file, then use the admin API for later privileged users.
5. Roll back application images first, then downgrade the additive indexes if necessary.

## Open Questions

None. Contract compatibility, retry behavior, provisioning, dependency tooling, and deployment shape were approved during design review.
