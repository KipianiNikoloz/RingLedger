## ADDED Requirements

### Requirement: Privileged user management API
The system SHALL expose an admin-only endpoint for creating promoter, management, and additional admin users.

#### Scenario: Admin provisions privileged operator
- **WHEN** an authenticated admin calls `POST /admin/users` with a unique email, valid password, and allowed privileged role
- **THEN** the system returns the created user's identifier, email, and role without returning password or token material

#### Scenario: Duplicate privileged email
- **WHEN** an admin provisions an email already assigned to a user
- **THEN** the system returns a deterministic conflict without changing the existing user
