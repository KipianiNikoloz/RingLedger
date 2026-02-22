# RingLedger Xaman Signing Contract (M4 Slice A)

Last updated: 2026-02-22

## Purpose

Define backend responsibilities for non-custodial promoter signing with Xaman.

This slice hardens `R-06` without changing auth mode, payout/escrow state semantics, or confirm idempotency behavior.

## Backend Guarantees

- Backend never stores promoter private keys.
- Backend only prepares unsigned XRPL payloads and Xaman sign-request metadata.
- Backend confirm endpoints remain the only state-transition authority and require validated ledger evidence.

## Prepare Response Contract

Prepare endpoints include a `xaman_sign_request` object per unsigned transaction:

- `payload_id`
- `deep_link_url`
- `qr_png_url`
- `websocket_status_url` (optional)
- `mode` (`stub` or `api`)

Endpoints:

- `POST /bouts/{bout_id}/escrows/prepare`
- `POST /bouts/{bout_id}/payouts/prepare`

If sign-request generation fails, prepare endpoints return `502`.

## Runtime Modes

Environment variables:

- `XAMAN_MODE`:
  - `stub` (default): deterministic, non-network sign-request envelopes for local and CI.
  - `api`: create real Xaman payloads through API.
- `XAMAN_API_BASE_URL` (default: `https://xumm.app`)
- `XAMAN_API_KEY` (required in `api` mode)
- `XAMAN_API_SECRET` (required in `api` mode)
- `XAMAN_TIMEOUT_SECONDS` (default: `10`)

## Flow

1. Backend prepare endpoint returns unsigned tx plus `xaman_sign_request`.
2. Promoter signs and submits in Xaman app.
3. Client submits confirmation artifacts (`tx_hash`, validated result metadata) to backend confirm endpoint.
4. Backend validates ledger evidence and only then transitions escrow/bout state.

## Validation Coverage

- Unit: `backend/tests/unit/test_xaman_service.py`
- Integration: `backend/tests/integration/test_escrow_confirm_flow.py`
- Integration: `backend/tests/integration/test_payout_flow.py`
