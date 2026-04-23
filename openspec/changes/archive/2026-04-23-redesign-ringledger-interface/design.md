## Context

The frontend is a React 19/Vite application under `frontend/`. The current app composes its operational behavior through `useRingLedgerConsole` and existing workflow panels for authentication, bout setup, escrow lifecycle, result entry, payout lifecycle, output, and status logging. The redesign is presentation-focused: it must reshape the route layout and CSS while preserving API calls, route behavior, workflow hooks, test IDs, and the existing ability to inspect JSON responses and errors.

## Goals / Non-Goals

**Goals:**
- Make `/app` feel like a dark backend-authoritative settlement control room for XRPL escrow operations.
- Keep lifecycle progress scannable through a four-stage rail: Authenticate, Escrows, Result, Payouts.
- Keep operator context, active workflow controls, and evidence/output visible at desktop widths.
- Use trust-boundary color semantics consistently: cyan for operator action, blue for signing, amber for backend processing, green for ledger/backend evidence, and red/orange for failures.
- Redesign `/` as a concise entry surface using the same identity.
- Maintain responsive usability on mobile, tablet, and desktop.

**Non-Goals:**
- No backend, API contract, or workflow semantic changes.
- No new component library or design-system dependency.
- No marketing-heavy homepage or decorative dashboard mimicry.
- No removal of raw evidence, JSON output, action log, or errors.

## Decisions

1. **Refactor `AppShell.tsx` as the layout owner.** The route-level shell will compute lifecycle state from `useRingLedgerConsole` data and arrange existing panels into header, stepper, context rail, workspace, evidence rail, and legend regions. This keeps behavioral code centralized in existing hooks and avoids duplicating workflow state.

2. **Reuse existing workflow panels.** Existing panels will remain the source of inputs, buttons, labels, test IDs, and API-triggering behavior. Markup changes should be limited to wrapper regions and small semantic additions that improve layout or accessibility.

3. **Implement the visual system in `styles.css`.** CSS variables, panel primitives, compact controls, responsive grids, and state classes will live in the global stylesheet. This avoids introducing a UI dependency and keeps the change easy to audit.

4. **Expose evidence through the right rail instead of hiding it.** The latest backend response, Xaman/signing details, ledger evidence, action log, and failure/error classification should be grouped into evidence surfaces. If a specific evidence source is unavailable, the UI should show a compact empty or pending state rather than removing the section.

5. **Keep homepage concise.** `/` will present brand, brief purpose, trust-boundary summary, and an action into `/app`; it will share the same dark design tokens without creating a long marketing page.

## Risks / Trade-offs

- **Risk: layout refactor breaks tests that query visible copy or labels.** Mitigation: preserve existing labels/test IDs where possible and update tests only when copy intentionally changes.
- **Risk: dense desktop layout becomes cramped on mobile.** Mitigation: use responsive single-column stacking, stable panel dimensions, and non-overflowing monospace blocks.
- **Risk: lifecycle state inference is imperfect.** Mitigation: derive from currently available hook state conservatively and label uncertain stages as pending or in progress.
- **Risk: right rail duplicates existing output panel content.** Mitigation: reuse `OutputPanel`/`StatusConsole` content where practical and add compact summary panels only where they improve scanning.
