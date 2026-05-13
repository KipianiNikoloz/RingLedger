## Context

RingLedger already has the lifecycle-critical escrow/result/payout endpoints, but the MVP setup path is incomplete: fighter profiles and bout drafts are still created directly through services or fixtures. The API spec lists `PUT /fighters/me`, `POST /bouts`, `GET /bouts`, and `GET /bouts/{id}` as planned. Existing constraints remain locked: email/password JWT auth, XRP drops as integers, strict 1v1 bouts, exactly four escrows, and backend authority for every lifecycle invariant.

## Goals / Non-Goals

**Goals:**
- Provide authenticated fighter profile upsert with XRPL address validation.
- Provide promoter-only bout draft creation backed by `BoutService.create_bout_draft`.
- Provide role-scoped bout list/detail reads for promoters, fighters, and admins.
- Expose the management surface in the React operator workspace without weakening backend authority.
- Cover the new API and UI behavior with focused contract/security/integration tests.

**Non-Goals:**
- No new wallet login or custody model.
- No changes to Xaman signing, XRPL confirmation, payout, result, or idempotency semantics.
- No schema migration beyond existing tables unless implementation proves a missing required column.
- No public unauthenticated bout browsing.

## Decisions

1. **Use existing tables and service planning logic.** `POST /bouts` will call the current bout draft service so the four escrow rows, time rules, fulfillment generation, and drops constraints remain centralized. Alternative considered: build rows directly in the route; rejected because it would duplicate escrow planning invariants.

2. **Add thin management routes instead of expanding signing route modules.** Fighter profile routes live under `/fighters`; bout create/read routes live under `/bouts` beside the existing lifecycle routes. Alternative considered: a separate `/management` namespace; rejected because the API spec already names concrete MVP paths.

3. **Role-scoped reads are enforced by backend queries.** Promoters see their own bouts, fighters see bouts where they are fighter A/B, and admins see all bouts. Detail reads return `404` when the bout is outside the actor scope to avoid leaking identifiers. Alternative considered: returning `403`; rejected because the current API already uses not-found semantics for missing bout resources.

4. **Frontend management controls remain operational, not authoritative.** The operator workspace can upsert fighter profiles and create/select bout drafts, but all validation and lifecycle state remain backend-driven. Alternative considered: client-side gating by role only; rejected because frontend is explicitly untrusted.

## Risks / Trade-offs

- [Risk] SQLite tests can diverge from PostgreSQL enum/UUID behavior. -> Mitigation: follow existing test patterns and keep serialization contracts covered at API level.
- [Risk] Creating bout drafts before fighter profiles exist would produce unusable destination addresses. -> Mitigation: require fighter profile records with XRPL addresses for both fighters during `POST /bouts`.
- [Risk] Frontend forms may become busy in the already dense operator workspace. -> Mitigation: integrate compact management controls into the existing context/workflow panels rather than adding a new page.
