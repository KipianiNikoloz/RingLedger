## Why

RingLedger has extensive maintainer documentation but no repository-wide operating contract that requires agents and contributors to keep it synchronized with implementation changes. Canonical OpenSpec files also retain generated placeholders and some release guidance has drifted from the executable repository configuration.

## What Changes

- Add a root `AGENTS.md` whose leading directive makes continuous documentation maintenance mandatory.
- Define the repository's OpenSpec-first, feature-branch, atomic-commit, verification, traceability, and secret-handling workflow for agents.
- Repair generated placeholders and align canonical documentation with the repository's actual paths, commands, configuration names, and release boundary.
- Preserve structural documentation tests without adding a CI rule that forces a documentation file into every commit.

## Capabilities

### New Capabilities

- `documentation-governance`: Repository-wide requirements for continuously maintained documentation and agent delivery practices.

### Modified Capabilities

- `feature-documentation`: Clarify that module documentation participates in the repository-wide governance contract and must remain accurate as implementation changes.

## Impact

This change affects root contributor guidance, canonical Markdown documentation, OpenSpec capability contracts, and the existing documentation validation suite. It does not change runtime APIs, schemas, dependencies, or application behavior.
