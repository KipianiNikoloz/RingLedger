# RingLedger Release-Ready MVP Design

## Context

RingLedger claims completion of its locked XRPL Testnet MVP, but a repository audit found documentation drift, client-asserted ledger confirmation, public privileged-role registration, non-reproducible Python setup, incomplete container delivery, and an operator interface that needs a stronger authored identity. Live credentialed Xaman/XRPL validation remains an external operator responsibility.

## Delivery Model

Work proceeds through three sequential, independently green feature branches:

1. `feat/docs-update` establishes documentation governance and repairs current contracts.
2. `feat/release-verification-hardening` makes ledger confirmation backend-authoritative, secures role provisioning, locks dependencies, aligns CI, and adds the container runtime.
3. `feat/release-readiness-closeout` applies the Split Decision frontend identity and records final deterministic evidence.

Each branch owns one OpenSpec change, uses test-first atomic commits, updates affected documentation with behavior, passes clean-checkout gates, archives its change, and merges before the next branch begins.

## System Decisions

- Confirmation requests contain only `escrow_kind` and `tx_hash`. The backend obtains transaction truth from XRPL Testnet API v2 and never trusts browser-supplied ledger fields.
- Pending ledger results are retryable and not cached as idempotent terminal responses; validated success or rejection is deterministic and replayable.
- Public registration creates fighters only. Admins provision privileged roles, and a secret-safe bootstrap command creates the first admin.
- Python dependencies are locked with `uv.lock`; CI, containers, and local verification use the locked environment.
- PostgreSQL migrations run as a one-shot container dependency before the backend. Nginx serves the SPA and proxies `/api` for same-origin production traffic.
- Documentation governance is instruction-based with structural validation; commits are not forced to touch Markdown when behavior is unaffected.

## Frontend Identity: Split Decision

The visual system combines avant-garde fight editorial with machine-ledger precision. Basalt and warm bone form the structural field; phosphor lime marks authorized actions, cyan marks Xaman/XRPL boundaries, and infrared is reserved for failure. Display typography is sparse and expansive, operational hierarchy is condensed, and hashes and drops use mono type.

The system uses hard rules, clipped frames, asymmetric scorecard planes, decisive short motion, lifecycle-ordered responsive collapse, keyboard-visible focus, semantic status labels, WCAG AA contrast, and reduced-motion parity. It excludes generic rounded-card grids, glassmorphism, purple startup gradients, gratuitous glow, and decorative motion on evidence.

## Release Boundary

Completion means every deterministic repository gate passes from a clean checkout, the container stack boots with documented non-secret configuration, public contracts and documentation agree, and no known locked-scope defect remains. Mainnet, wallet login, disputes, multisig, extra assets, and live credentialed smoke execution remain outside this implementation.
