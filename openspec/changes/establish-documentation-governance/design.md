## Context

RingLedger already documents its locked MVP through root and module READMEs, canonical reference documents, OpenSpec capabilities, and a traceability matrix. The current branch expands module-local documentation, but the repository lacks root agent instructions tying documentation maintenance to every behavioral change. Two archived capabilities also retain generated purpose placeholders, and several operational references have drifted from the executable configuration.

The change is documentation-only. It must preserve the existing feature-documentation work and commits, avoid introducing a requirement that every commit touch Markdown, and establish the workflow that later release-hardening branches will follow.

## Goals / Non-Goals

**Goals:**

- Make continuous documentation maintenance the first and most prominent repository instruction.
- Define OpenSpec-first planning, feature-branch delivery, atomic commits, verification, traceability, and secret-handling expectations.
- Align canonical documents and OpenSpec purposes with repository truth.
- Retain automated structural validation for the existing module documentation inventory.

**Non-Goals:**

- Change runtime behavior, public APIs, schemas, or dependencies.
- Force an arbitrary documentation file change in every commit.
- Rewrite historical archived OpenSpec artifacts.
- Expand the locked Testnet MVP scope.

## Decisions

1. **Put the documentation directive before the `AGENTS.md` title.** The user explicitly requires it above everything else, so a blockquote directive is the first content in the file. A conventional title and detailed instructions follow it.
2. **Use instruction-based governance plus existing structural checks.** Documentation accuracy requires judgment and cannot be proven by checking that a Markdown file changed. Existing tests continue to validate inventory, required sections, diagrams, and repository links.
3. **Keep canonical contracts authoritative.** The root guide points contributors to the nearest module README and then to the canonical requirements, API, state-machine, schema, operations, and traceability documents. Changes update every affected layer in the same functional slice.
4. **Preserve the approved branch history.** The existing `feat/docs-update` commits remain intact. New work is added through focused commits and the completed OpenSpec change is archived only after verification.
5. **Repair current specs, not historical archives.** Generated `TBD` purposes are corrected in `openspec/specs/`; archived proposal history remains immutable evidence of prior work.

## Risks / Trade-offs

- **Instruction-only enforcement can be ignored** → Make the directive prominent, repeat the required documentation workflow in delivery rules, and retain structural tests that catch objective drift.
- **Broad documentation edits can hide unrelated changes** → Limit repairs to verified placeholders, incorrect paths, stale commands, configuration names, and evidence claims.
- **Canonical and module docs can diverge** → Define canonical documents as authoritative and require module READMEs to link rather than duplicate detailed contracts.

## Migration Plan

1. Add and validate the OpenSpec artifacts.
2. Add root `AGENTS.md` and the approved Superpowers design/plan records.
3. Repair current documentation and canonical OpenSpec purposes.
4. Run documentation, OpenSpec, formatting, and link validation.
5. Archive the completed change and merge `feat/docs-update` before creating dependent branches.

Rollback is a normal revert of the focused commits; no data or runtime migration is involved.

## Open Questions

None. The documentation enforcement level, branch order, and scope were approved during design review.
