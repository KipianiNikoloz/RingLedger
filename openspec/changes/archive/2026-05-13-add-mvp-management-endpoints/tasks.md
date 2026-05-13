## 1. Backend Management API

- [x] 1.1 Add fighter profile schemas, repository/service behavior, and `PUT /fighters/me` route with role and duplicate-address guards.
- [x] 1.2 Add bout create/read schemas plus role-scoped repository/service queries for list/detail responses.
- [x] 1.3 Add `POST /bouts`, `GET /bouts`, and `GET /bouts/{id}` routes using existing bout draft planning and backend-only authorization.
- [x] 1.4 Cover profile upsert, bout creation, role-scoped reads, and forbidden/out-of-scope cases with backend tests.

## 2. Frontend Management Surface

- [x] 2.1 Extend the typed API client and workflow hooks for fighter profile upsert and bout create/list/detail calls.
- [x] 2.2 Add compact operator workspace controls for profile setup, bout creation, and active bout selection without disrupting existing lifecycle controls.
- [x] 2.3 Cover the new frontend client/workspace flows with unit and browser-level tests.

## 3. Documentation And Verification

- [x] 3.1 Update API, traceability, README, and frontend/backend docs to mark management endpoints implemented and aligned to requirements.
- [x] 3.2 Run relevant backend and frontend verification commands and record current evidence.
- [x] 3.3 Validate the OpenSpec change and commit the completed slice with detailed commit messages.
