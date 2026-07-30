## ADDED Requirements

### Requirement: Continuous documentation maintenance
The repository SHALL require relevant documentation to remain synchronized with changes to behavior, APIs, configuration, schemas, tests, and operational procedures.

#### Scenario: Contributor changes repository behavior
- **WHEN** a contributor changes an implementation or operational contract
- **THEN** the same functional change updates every affected canonical or module-local document

#### Scenario: Change has no documentation impact
- **WHEN** a change does not alter any documented behavior or contract
- **THEN** the workflow permits the change without an unrelated documentation-file edit

### Requirement: Root agent guidance
The repository SHALL provide root `AGENTS.md` guidance whose leading directive makes continuous documentation maintenance the highest-priority repository instruction.

#### Scenario: Agent begins repository work
- **WHEN** an agent reads the root guidance
- **THEN** it encounters the continuous-documentation directive before branch, implementation, testing, or delivery rules

### Requirement: Spec-driven incremental delivery
The repository SHALL direct substantial changes through OpenSpec artifacts, feature branches, atomic commits, relevant verification, and final artifact archival.

#### Scenario: Agent implements a substantial change
- **WHEN** work changes product behavior, public contracts, schemas, security boundaries, or release operations
- **THEN** the agent creates or selects an OpenSpec change, works on a feature branch, commits cohesive increments, runs required gates, and archives the completed change

### Requirement: Documentation authority and traceability
The repository SHALL identify canonical documentation and require requirement-to-implementation-to-test-to-documentation traceability to remain accurate.

#### Scenario: Contract changes
- **WHEN** an API, lifecycle rule, schema, integration boundary, or release procedure changes
- **THEN** its canonical document and traceability entry are updated alongside the implementation

### Requirement: Secret-safe documentation
Repository documentation and evidence SHALL exclude private keys, seed phrases, passwords, JWT secrets, API secrets, and other credential material.

#### Scenario: Contributor records verification evidence
- **WHEN** local, CI, deployment, Xaman, or XRPL evidence is documented
- **THEN** only non-secret identifiers, sanitized summaries, and safe configuration names are recorded
