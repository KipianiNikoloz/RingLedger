# operator-console-interface Specification

## Purpose
TBD - created by archiving change redesign-ringledger-interface. Update Purpose after archive.
## Requirements
### Requirement: Operator workspace route
The system SHALL present `/app` as a dark operator workspace for RingLedger escrow lifecycle work while preserving existing workflow behavior and backend API contracts.

#### Scenario: Workspace renders at app route
- **WHEN** an operator navigates to `/app`
- **THEN** the page displays the RingLedger operator workspace with header, lifecycle stepper, context rail, central workflow area, evidence rail, and trust-boundary legend

#### Scenario: Existing workflows remain available
- **WHEN** an operator uses authentication, escrow, result, payout, output, and status controls
- **THEN** the controls remain accessible and continue to call the existing frontend workflow hooks and API client behavior

### Requirement: Lifecycle state visibility
The system SHALL display a four-stage lifecycle rail with Authenticate, Escrows, Result, and Payouts states derived from existing frontend workflow state where possible.

#### Scenario: Lifecycle rail summarizes progress
- **WHEN** workflow state changes after authentication, escrow actions, result entry, or payout actions
- **THEN** the lifecycle rail updates each stage as pending, in progress, complete, or failed using compact labels and trust-boundary colors

### Requirement: Evidence-first layout
The system SHALL keep backend responses, signing request details, XRPL ledger evidence, action log entries, and failures visible or discoverable in the operator workspace.

#### Scenario: Evidence rail presents latest output
- **WHEN** a workflow action returns a response, signing payload, ledger evidence, log entry, or error
- **THEN** the right rail presents the latest evidence without hiding raw JSON output needed for audit

### Requirement: Trust-boundary visual language
The system SHALL apply a consistent dark visual identity and color mapping for operator actions, signing state, backend processing, ledger evidence, and failures.

#### Scenario: Trust-boundary legend is visible
- **WHEN** an operator scans the workspace
- **THEN** the interface includes a legend mapping cyan/teal to operator actions, blue to signing state, amber to backend processing, green to ledger evidence, and red/orange to failures

### Requirement: Concise homepage entry
The system SHALL present `/` as a concise dark RingLedger entry screen with a clear route into `/app`.

#### Scenario: Homepage opens workspace
- **WHEN** a user visits `/`
- **THEN** the page uses the same dark trust-boundary identity, briefly explains RingLedger, and provides a clear action to open `/app`

### Requirement: Responsive operator usability
The system SHALL keep the redesigned frontend usable at mobile, tablet, and desktop widths without incoherent overlap or clipped operational controls.

#### Scenario: Layout adapts to narrow screens
- **WHEN** the viewport width is narrow
- **THEN** the app stacks header, lifecycle, workflow, context, evidence, and legend regions so labels, controls, JSON output, and buttons remain usable

### Requirement: Management setup controls
The system SHALL expose fighter profile, bout creation, and bout selection controls in the operator workspace while preserving existing lifecycle workflow behavior.

#### Scenario: Fighter profile setup is available
- **WHEN** an operator uses the workspace profile setup controls with a fighter token
- **THEN** the interface calls `PUT /fighters/me` and surfaces the persisted profile evidence

#### Scenario: Promoter creates lifecycle-ready bout
- **WHEN** an operator uses the workspace bout creation controls with a promoter token and fighter/profile inputs
- **THEN** the interface calls `POST /bouts`, stores the returned bout identifier as the active bout, and keeps the existing escrow workflow controls available

#### Scenario: Operator selects an accessible bout
- **WHEN** an operator lists or loads bouts available to the active role
- **THEN** the interface calls `GET /bouts` or `GET /bouts/{id}` and updates the active bout context without mutating lifecycle state

### Requirement: Stable browser verification
The system SHALL keep browser-level verification available for the operator workspace through the frontend E2E command.

#### Scenario: Operator journey remains covered
- **WHEN** the frontend E2E command runs
- **THEN** the browser journey covers fighter profile setup, bout creation, escrow preparation, signing reconciliation, confirmation, result entry, and payout closeout controls

