> Documentation must be updated continuously as the codebase evolves; every behavior, API, configuration, schema, test, and operational change must keep the relevant documentation accurate in the same change.

# RingLedger Agent Guide

## Working Agreement

- Read this file, the root `README.md`, and the README nearest to the code you will change before editing.
- Treat documentation as part of the product. Update affected canonical docs, module READMEs, diagrams, examples, test evidence, and traceability in the same functional slice as the implementation.
- Do not manufacture a documentation edit for a change that has no documentation impact. State the reason in the commit or pull-request description instead.
- Preserve the locked XRPL Testnet MVP unless an approved OpenSpec change explicitly modifies it.

## Spec-Driven Delivery

- Use OpenSpec for substantial behavior, API, schema, security-boundary, integration, or release-operation changes.
- Read every OpenSpec context artifact before applying its tasks. Keep the task checklist current as work completes.
- Archive an OpenSpec change only after its implementation, tests, documentation, and verification are complete.
- Keep current capability contracts under `openspec/specs/`; historical archived changes are evidence and should not be rewritten.

## Branches and Commits

- Never implement directly on `main` or `master`. Use a focused `feat/*`, `fix/*`, `docs/*`, or `chore/*` branch.
- Build dependent work sequentially: merge or otherwise establish the accepted baseline before branching the next slice.
- Make incremental, cohesive commits. Each commit must have one reviewable purpose and pass the relevant targeted checks.
- Use clear Conventional Commit-style subjects such as `feat: verify confirmations against xrpl` or `docs: align release guidance`.
- Do not mix unrelated cleanup, dependency churn, formatting, or refactors into a feature commit.
- Preserve user-authored changes and existing branch history. Never use destructive Git commands unless the user explicitly requests them.

## Implementation and Verification

- Use test-driven development for behavior changes: add one failing behavioral test, confirm the expected failure, implement the minimum fix, then run targeted and regression tests.
- Keep the backend authoritative for authentication, authorization, lifecycle transitions, timing, money, idempotency, and ledger validation. Frontend checks are user experience only.
- Run the repository gates documented in `README.md` and `docs/ci-cd.md`. A completion claim requires fresh command output, not historical evidence.
- Diagnose failures to their root cause before changing code. Do not weaken tests, validation, security boundaries, or release gates to obtain a pass.

## Documentation Authority

- Requirements and scope: `docs/requirements-matrix.md`
- HTTP contracts: `docs/api-spec.md`
- Lifecycle rules: `docs/state-machines.md`
- Persistence: `docs/schema-doc.md`
- Requirement mapping and evidence: `docs/traceability-matrix.md`
- Operations and release: `docs/operations-runbook.md` and `docs/testnet-release-readiness.md`
- CI and local gates: `docs/ci-cd.md`
- Module ownership: the nearest backend or frontend README listed in the root `README.md`

When documents disagree, stop and resolve the conflict in the same change. Do not silently choose whichever version is convenient.

## Security and Evidence

- Never commit or document private keys, seed phrases, passwords, JWT secrets, API secrets, access tokens, raw credential files, or funded-account credentials.
- Use environment-managed secrets and sanitized fixtures. Examples must contain clearly non-production placeholder values.
- Release evidence may record non-secret request paths, payload IDs, transaction hashes, status summaries, versions, and command results.
- Keep Xaman signing non-custodial and the release network limited to XRPL Testnet.
