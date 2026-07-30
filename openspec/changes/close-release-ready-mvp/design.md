## Context

The console already has lifecycle and evidence rails, but its final hardening must prevent old client-evidence controls from returning and prove the interface remains usable across viewport and accessibility modes.

## Decisions

- Keep the dark cyan/ultraviolet/magenta “Split Decision” identity with clipped telemetry surfaces.
- Keep API behavior in hooks and the typed client; page extraction remains presentational.
- Test security-relevant UI contracts in Vitest and layout/accessibility behavior in Playwright.
- Use semantic landmarks, labels, focusable native controls, reduced-motion CSS, and an explicit no-horizontal-overflow assertion.

## Risks

- Visual refactoring can break test selectors; retain accessible names and existing data-testid values.
- Browser layout checks can be flaky; assert stable document geometry at fixed viewports rather than pixel snapshots.
