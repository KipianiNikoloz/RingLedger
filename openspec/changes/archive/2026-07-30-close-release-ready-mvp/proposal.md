## Why

The release-hardening change secured runtime trust boundaries, but the final operator experience needs explicit regression coverage and a maintainable page boundary before the release-ready MVP can be closed.

## What Changes

- Preserve the approved “Split Decision” visual identity across home and operator routes.
- Make fighter registration, admin provisioning, and server-authoritative ledger confirmation visible and testable in the UI.
- Add responsive, reduced-motion, keyboard/accessibility, and horizontal-overflow browser checks.
- Extract the homepage into a focused page unit and synchronize frontend documentation.

## Impact

Frontend composition, component tests, browser tests, operator-interface specs, and release evidence are updated. Backend lifecycle authority and API behavior do not change.
