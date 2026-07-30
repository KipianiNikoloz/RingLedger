## ADDED Requirements

### Requirement: Secure account workflows
The operator console SHALL present public registration as fighter-only and SHALL expose privileged-user provisioning only as an admin-token operation.

#### Scenario: Account controls render
- **WHEN** the authentication stage is displayed
- **THEN** fighter registration has no role selector and a separate provisioning form offers only promoter, management, or admin roles

### Requirement: Ledger-authoritative confirmation controls
The operator console SHALL request only escrow kind and transaction hash for escrow and payout confirmation.

#### Scenario: Confirmation stage renders
- **WHEN** an operator opens either confirmation stage
- **THEN** the interface does not request validated state, engine result, offer sequence, close time, or transaction invariant metadata

### Requirement: Automated responsive accessibility
The operator console SHALL remain keyboard-operable and free of horizontal document overflow at mobile, tablet, and desktop widths, including reduced-motion mode.

#### Scenario: Browser accessibility sweep
- **WHEN** automated browser verification visits the home and operator routes at supported widths with reduced motion enabled
- **THEN** landmarks, named controls, focus targets, and document geometry remain usable
