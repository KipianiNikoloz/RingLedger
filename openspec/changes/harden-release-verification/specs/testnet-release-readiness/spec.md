## MODIFIED Requirements

### Requirement: Testnet release evidence
The system SHALL document Testnet release readiness only when locked clean-checkout backend/frontend gates, authoritative XRPL confirmation tests, privileged-role security tests, migration checks, OpenSpec validation, secret scanning, container build/Compose smoke checks, and the operator live-smoke boundary are current for the locked MVP scope.

#### Scenario: Release evidence is current
- **WHEN** project status documents mark the MVP ready for Testnet release
- **THEN** the release evidence lists backend, frontend, browser E2E, XRPL confirmation, auth security, regression, performance, migration, OpenSpec, secret-scan, image-build, and container-smoke results

#### Scenario: Release evidence remains bounded
- **WHEN** release readiness is documented
- **THEN** the documentation keeps the release scope bounded to XRPL Testnet, Xaman non-custodial signing, and the locked MVP lifecycle

#### Scenario: Deterministic hardening is incomplete
- **WHEN** any required clean-checkout or container gate is missing or failing
- **THEN** status documentation does not claim readiness for live Testnet validation
