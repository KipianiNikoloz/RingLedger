## 1. Deterministic Tooling

- [x] 1.1 Commit `uv.lock`, document locked setup, and run backend commands through uv.
- [x] 1.2 Make Vitest collection and worker failures deterministic and align frontend package installation.

## 2. XRPL Ledger Authority

- [x] 2.1 Add failing unit tests for Testnet identity, API v2 transaction parsing, pending evidence, malformed responses, and transport failures.
- [x] 2.2 Implement the injected XRPL JSON-RPC client and ledger-evidence models.
- [x] 2.3 Add failing API/service tests for two-field confirmation, extra-field rejection, retryable idempotency, and terminal replay.
- [x] 2.4 Integrate backend-fetched evidence into escrow and payout confirmation and update the frontend contract.
- [x] 2.5 Add and test a reversible migration enforcing unique non-null create and close transaction hashes.

## 3. Privileged Role Security

- [ ] 3.1 Add failing tests for fighter-only public registration, admin provisioning, authorization, duplicates, and bootstrap replay.
- [ ] 3.2 Implement the public/auth schema change, admin API/service flow, and secret-safe bootstrap command.
- [ ] 3.3 Update the frontend registration contract and add the functional admin provisioning client/workflow surface.

## 4. Runtime and Delivery

- [ ] 4.1 Add failing tests for production configuration, CORS, liveness, database readiness, and XRPL Testnet readiness.
- [ ] 4.2 Implement validated settings, CORS middleware, `/readyz`, and safe error translation.
- [ ] 4.3 Add and verify non-root backend/frontend images, Nginx proxying, Compose migration ordering, persistent PostgreSQL, and `.env.example`.
- [ ] 4.4 Align CI with locked backend, frontend build/test/E2E, migrations, OpenSpec, secret scan, and container gates.

## 5. Documentation and Closeout

- [ ] 5.1 Update API, schema, state-machine, operations, CI, module, release, and traceability documentation.
- [ ] 5.2 Run all clean-checkout and container verification gates and record fresh non-secret evidence.
- [ ] 5.3 Complete the checklist and archive the OpenSpec change after every gate passes.
