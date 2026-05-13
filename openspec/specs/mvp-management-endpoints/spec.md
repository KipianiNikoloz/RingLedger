# mvp-management-endpoints Specification

## Purpose
Defines fighter profile management and role-scoped bout create/read APIs needed to run the locked MVP lifecycle without manual database setup.
## Requirements
### Requirement: Fighter profile upsert
The system SHALL allow an authenticated fighter to create or update their own profile with a display name and XRPL address.

#### Scenario: Fighter upserts own profile
- **WHEN** an authenticated fighter calls `PUT /fighters/me` with a valid display name and XRPL address
- **THEN** the system persists one profile for that fighter and returns the profile identifier, display name, and XRPL address

#### Scenario: Non-fighter cannot upsert fighter profile
- **WHEN** an authenticated promoter or admin calls `PUT /fighters/me`
- **THEN** the system rejects the request without creating or updating a fighter profile

#### Scenario: Duplicate fighter XRPL address is rejected
- **WHEN** a fighter submits an XRPL address already assigned to a different fighter profile
- **THEN** the system rejects the request deterministically without changing the caller profile

### Requirement: Bout draft creation API
The system SHALL allow an authenticated promoter to create a draft bout using two fighter users, event time, promoter owner address, and integer XRP drops amounts.

#### Scenario: Promoter creates draft bout
- **WHEN** an authenticated promoter calls `POST /bouts` with two fighter user IDs, valid fighter profile destinations, event time, promoter owner address, and show/bonus drops
- **THEN** the system creates a draft bout with exactly four planned escrows and returns the bout summary

#### Scenario: Non-promoter cannot create bout
- **WHEN** an authenticated fighter or admin calls `POST /bouts`
- **THEN** the system rejects the request without creating a bout or escrows

#### Scenario: Bout creation requires fighter profiles
- **WHEN** a promoter calls `POST /bouts` for a fighter user without a profile XRPL address
- **THEN** the system rejects the request without creating a partial bout

### Requirement: Role-scoped bout reads
The system SHALL expose authenticated bout list and detail reads scoped to the caller role and relationship to the bout.

#### Scenario: Promoter lists own bouts
- **WHEN** an authenticated promoter calls `GET /bouts`
- **THEN** the system returns only bouts where the promoter is the bout promoter

#### Scenario: Fighter lists assigned bouts
- **WHEN** an authenticated fighter calls `GET /bouts`
- **THEN** the system returns only bouts where the fighter is fighter A or fighter B

#### Scenario: Admin lists all bouts
- **WHEN** an authenticated admin calls `GET /bouts`
- **THEN** the system returns all bouts visible to administrative operators

#### Scenario: Out-of-scope bout detail is hidden
- **WHEN** an authenticated actor calls `GET /bouts/{id}` for a bout outside their role scope
- **THEN** the system responds as though the bout was not found

