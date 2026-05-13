## ADDED Requirements

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
