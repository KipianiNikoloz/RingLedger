## Why

RingLedger has strong milestone and reference documentation, but maintainers still have to jump across roadmap docs, API specs, state machines, tests, and source directories to understand one feature end to end. A feature-oriented documentation layer will make the completed MVP easier to maintain, review, onboard, and extend without changing runtime behavior.

## What Changes

- Add a maintainer-focused feature documentation hub under `docs/features/`.
- Add per-feature READMEs that summarize purpose, invariants, source files, tests, operational notes, and links back to canonical docs.
- Standardize visualizations on Mermaid diagrams stored directly in Markdown.
- Add validation coverage that checks the feature docs structure, required headings, Mermaid fences, and referenced repo paths.
- Keep existing central docs as authoritative references; feature READMEs summarize and link rather than fork contracts.

## Capabilities

### New Capabilities

- `feature-documentation`: Defines the maintainer-facing feature documentation structure, diagram expectations, and validation requirements.

### Modified Capabilities

- None.

## Impact

- Documentation: new `docs/features/` hub and per-feature README files, plus links from top-level docs.
- Tests: documentation validation test coverage for required feature README structure and repo path references.
- Runtime behavior: none.
- APIs, schemas, state machines, dependencies: unchanged.
