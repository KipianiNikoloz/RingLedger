## ADDED Requirements

### Requirement: Feature documentation hub
The repository SHALL provide a maintainer-focused feature documentation hub that maps locked MVP capabilities to per-feature READMEs.

#### Scenario: Maintainer starts from the feature hub
- **WHEN** a maintainer opens the feature documentation hub
- **THEN** they can navigate to each MVP feature README and identify the feature purpose, main flows, source areas, tests, and canonical references

### Requirement: Per-feature README structure
Each feature README SHALL use a consistent maintainer template covering purpose, flows, invariants, implementation map, tests, operations, and references.

#### Scenario: Feature README is complete
- **WHEN** a feature README is reviewed
- **THEN** it contains the required maintainer sections and at least one Mermaid diagram relevant to the feature

### Requirement: Diagram format
Feature documentation SHALL use Mermaid diagrams stored directly in Markdown for feature visualizations.

#### Scenario: Diagram is reviewable
- **WHEN** a feature flow, state, sequence, or relationship is documented visually
- **THEN** the diagram is represented as a Mermaid fenced code block rather than a generated binary image

### Requirement: Documentation validation
The repository SHALL include automated validation for the feature documentation inventory and structural expectations.

#### Scenario: Feature docs drift
- **WHEN** a required feature README is missing, lacks required sections, lacks a Mermaid diagram, or references a non-existent repo path
- **THEN** the documentation validation gate fails
