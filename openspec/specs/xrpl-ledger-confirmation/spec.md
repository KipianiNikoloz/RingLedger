# xrpl-ledger-confirmation Specification

## Purpose
TBD - created by archiving change harden-release-verification. Update Purpose after archive.
## Requirements
### Requirement: Backend-fetched transaction evidence
The system SHALL accept only an escrow kind and transaction hash from confirmation callers and SHALL fetch all transaction evidence from XRPL Testnet API v2.

#### Scenario: Validated escrow creation succeeds
- **WHEN** XRPL returns a matching `EscrowCreate` transaction with `validated=true`, `tesSUCCESS`, and all expected fields
- **THEN** the backend records the ledger-derived transaction hash and offer sequence and advances state

#### Scenario: Client submits legacy evidence
- **WHEN** a confirmation request includes client-asserted validation, result, amount, timing, address, or fulfillment fields
- **THEN** request validation rejects the extra fields without querying XRPL or changing state

### Requirement: Testnet network boundary
The system SHALL verify that confirmation evidence comes from XRPL network ID `1` before accepting it.

#### Scenario: RPC points to another network
- **WHEN** `server_info` reports a network ID other than `1` or omits the network ID
- **THEN** the backend rejects confirmation without changing state

### Requirement: Retryable ledger state
The system SHALL distinguish pending or unavailable ledger evidence from validated terminal outcomes.

#### Scenario: Transaction is pending
- **WHEN** XRPL does not find the transaction or reports it as unvalidated
- **THEN** the backend returns `409 ledger_confirmation_pending`, does not cache the response, and permits the same idempotent intent to retry

#### Scenario: RPC is unavailable
- **WHEN** the XRPL request times out or fails at the transport/provider boundary
- **THEN** the backend returns `503 xrpl_unavailable`, does not cache the response, and preserves lifecycle state

### Requirement: Ledger transaction uniqueness
The system SHALL prevent a non-null XRPL transaction hash from being recorded against more than one escrow create or close operation.

#### Scenario: Transaction hash is reused
- **WHEN** a terminal confirmation attempts to store a create or close hash already assigned to another escrow
- **THEN** persistence rejects the duplicate without settling the second escrow

