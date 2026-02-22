# RingLedger Frontend (M4 In Progress)

## Scope

This package implements the first React frontend contract surface for M4 hardening:

- Email/password login flow that stores JWTs by role (`promoter`, `admin`).
- Promoter escrow flow controls:
  - `POST /bouts/{bout_id}/escrows/prepare`
  - `POST /bouts/{bout_id}/escrows/signing/reconcile`
  - `POST /bouts/{bout_id}/escrows/confirm`
- Admin result entry control:
  - `POST /bouts/{bout_id}/result`
- Promoter payout flow controls:
  - `POST /bouts/{bout_id}/payouts/prepare`
  - `POST /bouts/{bout_id}/payouts/signing/reconcile`
  - `POST /bouts/{bout_id}/payouts/confirm`

No lifecycle or ledger invariant is enforced by frontend code; backend remains authoritative.

## Structure

- `src/App.tsx`: minimal entry component.
- `src/app/AppShell.tsx`: view composition and panel orchestration.
- `src/hooks/useRingLedgerConsole.ts`: workflow composition layer.
- `src/hooks/useActionRunner.ts`: shared busy/error/log action runner.
- `src/hooks/useAuthWorkflow.ts`: auth register/login workflow state.
- `src/hooks/useEscrowWorkflow.ts`: promoter escrow workflow state/actions.
- `src/hooks/useResultPayoutWorkflow.ts`: admin result and promoter payout workflow state/actions.
- `src/components/AuthPanel.tsx`: register/login UI.
- `src/components/BoutWorkspacePanel.tsx`: bout context input.
- `src/components/EscrowFlowPanel.tsx`: promoter escrow prepare/reconcile/confirm controls.
- `src/components/ResultEntryPanel.tsx`: admin result entry controls.
- `src/components/PayoutFlowPanel.tsx`: promoter payout prepare/reconcile/confirm controls.
- `src/components/OutputPanel.tsx`: response rendering blocks.
- `src/flow-utils.ts`: request payload extraction and validation helpers from prepare contracts.

## Commands

From `frontend/`:

- `npm install`
- `npm run dev`
- `npm run typecheck`
- `npm run test`
- `npm run test:e2e`

## Environment

- `VITE_API_BASE_URL` (default: `http://127.0.0.1:8000`)

## Test Coverage

- Unit/integration (Vitest): `src/api/client.test.ts`, `src/App.test.tsx`
- Browser E2E (Playwright): `e2e/promoter-flow.spec.ts`
