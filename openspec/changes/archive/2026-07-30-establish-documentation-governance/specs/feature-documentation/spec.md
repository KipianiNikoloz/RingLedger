## MODIFIED Requirements

### Requirement: Module-local documentation
The repository SHALL provide continuously maintained, maintainer-focused README files at meaningful backend and frontend module boundaries.

#### Scenario: Maintainer starts from a module
- **WHEN** a maintainer opens a module directory such as `backend/app/domain`
- **THEN** the local README accurately explains the module purpose, files, flow, maintenance notes, and related canonical docs

#### Scenario: Module implementation changes
- **WHEN** a module's responsibilities, files, data flow, or maintenance constraints change
- **THEN** its local README is updated in the same functional change
