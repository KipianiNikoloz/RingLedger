# testnet-release-readiness Specification

## Purpose
TBD - created by archiving change prepare-testnet-release. Update Purpose after archive.
## Requirements
### Requirement: Testnet release evidence
The system SHALL document Testnet release readiness only when local quality gates, frontend gates, OpenSpec validation, and release smoke evidence are current for the locked MVP scope.

#### Scenario: Release evidence is current
- **WHEN** project status documents mark the MVP ready for Testnet release
- **THEN** the release evidence lists backend, frontend, browser E2E, regression, performance, migration, and OpenSpec validation results

#### Scenario: Release evidence remains bounded
- **WHEN** release readiness is documented
- **THEN** the documentation keeps the release scope bounded to XRPL Testnet, Xaman non-custodial signing, and the locked MVP lifecycle

### Requirement: Live smoke validation is separated from deterministic gates
The system SHALL keep deterministic local and CI validation separate from live Xaman API and XRPL Testnet smoke validation.

#### Scenario: CI remains deterministic
- **WHEN** CI and local quality gates run
- **THEN** they use deterministic validation that does not require live Xaman API credentials or XRPL Testnet availability

#### Scenario: Live release smoke is documented
- **WHEN** operators prepare a Testnet release
- **THEN** the release checklist identifies required live Xaman API mode, XRPL Testnet confirmation, non-secret evidence, and residual external-service risks

### Requirement: Release secret handling
The system SHALL document secret-handling boundaries for Testnet release evidence.

#### Scenario: Evidence excludes secrets
- **WHEN** release evidence is captured
- **THEN** it records non-secret operational identifiers such as payload IDs and transaction hashes while excluding API secrets, JWT secrets, private keys, and credentials

