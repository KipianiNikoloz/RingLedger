## ADDED Requirements

### Requirement: Fighter-only public registration
The system SHALL create only fighter accounts through unauthenticated public registration.

#### Scenario: Visitor registers
- **WHEN** an unauthenticated caller submits a valid email and password to `POST /auth/register`
- **THEN** the system creates and returns a fighter account

#### Scenario: Visitor submits a role
- **WHEN** public registration includes a role field
- **THEN** request validation rejects the extra field without creating an account

### Requirement: Admin privileged-user provisioning
The system SHALL allow an authenticated admin to create promoter, management, or admin users and SHALL reject every non-admin caller.

#### Scenario: Admin creates a promoter
- **WHEN** an authenticated admin posts valid credentials and role `promoter` to `POST /admin/users`
- **THEN** the system creates the promoter and returns its non-secret account data

#### Scenario: Non-admin provisions a user
- **WHEN** a fighter, promoter, management user, or unauthenticated caller uses the admin endpoint
- **THEN** the system rejects the request without creating an account

### Requirement: First-admin bootstrap
The system SHALL provide a repeat-safe operator command that creates the first admin from interactive or password-file input without emitting the password.

#### Scenario: No admin exists
- **WHEN** the bootstrap command receives a valid unique email and secret input while no admin exists
- **THEN** it creates one admin and reports only non-secret identity data

#### Scenario: Bootstrap is replayed
- **WHEN** the same bootstrap identity already exists as admin
- **THEN** the command exits successfully without changing the password or creating another admin
