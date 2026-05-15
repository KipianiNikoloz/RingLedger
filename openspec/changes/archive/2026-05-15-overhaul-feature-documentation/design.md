## Context

RingLedger documentation is currently organized around roadmap milestones, central reference contracts, and package-level READMEs. That is useful for historical evidence, but maintainers need feature-level entry points that explain how one capability works across backend services, frontend workflows, tests, API contracts, and operational guardrails.

The documentation overhaul must avoid creating a second source of truth. Existing files such as `docs/api-spec.md`, `docs/state-machines.md`, `docs/schema-doc.md`, and `docs/operations-runbook.md` remain canonical. Feature READMEs provide navigation, mental models, diagrams, and source/test pointers.

## Goals / Non-Goals

**Goals:**

- Add a `docs/features/` hub and per-feature README set for the locked MVP.
- Use Mermaid diagrams for maintainable visualizations.
- Make each feature README useful to maintainers by listing purpose, flows, invariants, key files, tests, and canonical references.
- Add automated validation for required headings, Mermaid fences, and referenced repo paths.

**Non-Goals:**

- No runtime behavior, API, schema, state-machine, or dependency changes.
- No generated binary diagrams.
- No replacement of existing milestone/reference documentation.
- No live external service validation.

## Decisions

- Organize by capability rather than code package.
  - Rationale: features cross backend, frontend, tests, and docs; package-only docs force maintainers to reconstruct behavior manually.
  - Alternative considered: add READMEs inside every source directory. Rejected because it would duplicate package structure without explaining end-to-end behavior.
- Standardize on Mermaid diagrams in Markdown.
  - Rationale: Mermaid is reviewable, version-controlled text and supports flows, sequences, state diagrams, and entity relationships.
  - Alternative considered: static SVG/PNG diagrams. Rejected for the first pass because they are harder to diff and keep synchronized.
- Add a small docs validation test in the backend test suite.
  - Rationale: the repo already uses Python tests as quality gates; a focused test can keep the feature docs complete without adding a new toolchain.
  - Alternative considered: introduce a dedicated Markdown linter. Rejected for this slice to avoid new dependencies.

## Risks / Trade-offs

- Feature READMEs can drift from canonical docs -> Mitigation: link to canonical sources and validate source/test path references.
- Diagram syntax can be visually wrong even if Markdown exists -> Mitigation: keep diagrams simple and text-reviewable; deeper rendering validation can be a future enhancement.
- Docs validation can become brittle -> Mitigation: validate structure and existence, not prose wording.
- Too many feature docs can overwhelm maintainers -> Mitigation: use a consistent concise template and a hub index.
