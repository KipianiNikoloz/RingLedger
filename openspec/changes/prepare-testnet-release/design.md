## Context

RingLedger has completed M4 hardening for the locked MVP/Testnet scope. The repository has deterministic backend, frontend, browser E2E, regression, performance, and OpenSpec evidence, but the release path still needs an explicit Testnet readiness contract that distinguishes repeatable CI gates from operator-run live Xaman/XRPL smoke validation.

The MVP constraints remain unchanged: XRPL Testnet only, Xaman non-custodial promoter signing, email/password plus JWT auth, XRP drops, 1v1 four-escrow bouts, and backend-authoritative lifecycle transitions.

## Goals / Non-Goals

**Goals:**

- Define the evidence required to mark the locked MVP ready for Testnet release.
- Add a release preflight checklist covering environment, backend/frontend gates, OpenSpec validation, and live smoke validation.
- Document how live Xaman API mode and XRPL Testnet confirmation checks are validated without making CI depend on external services.
- Preserve the M4 scope boundary and document residual release risks.

**Non-Goals:**

- No mainnet support.
- No wallet login or additional auth modes.
- No lifecycle, API, schema, or state-machine changes.
- No automatic live Xaman/XRPL CI dependency.

## Decisions

- Keep CI/local validation stub-backed and deterministic.
  - Rationale: M4 gates must remain repeatable and not depend on third-party availability.
  - Alternative considered: run live Xaman/XRPL checks in CI. Rejected because secrets, funding, and external service availability would make core quality gates flaky.
- Treat live Xaman API and XRPL Testnet checks as release smoke validation.
  - Rationale: deployability needs live integration evidence, but that evidence belongs in an operator-controlled release checklist with secrets and funded Testnet accounts.
  - Alternative considered: add new automated integration tests immediately. Rejected for this slice unless a safe existing pattern is found, because the current project intentionally separates deterministic tests from external integrations.
- Capture release readiness as documentation and evidence, not feature expansion.
  - Rationale: M4 has already locked the MVP behavior; release readiness should prove the existing behavior is deployable rather than change product scope.

## Risks / Trade-offs

- Live smoke validation can be skipped by operators -> Mitigation: make it an explicit release-readiness requirement and include required evidence fields.
- External Xaman or XRPL Testnet outages can block release evidence -> Mitigation: classify these as residual operational risks and keep local/CI gates independently green.
- Secrets may leak during evidence capture -> Mitigation: document that payload identifiers and transaction hashes are allowed, while API secrets, JWT secrets, and private keys are never recorded.
- A smoke blocker may reveal a real product defect -> Mitigation: fix only narrow release blockers inside the locked MVP scope; defer scope expansion to a later OpenSpec change.
