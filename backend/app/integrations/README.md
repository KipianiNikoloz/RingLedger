# Integrations

## Purpose

`backend/app/integrations` isolates Xaman signing and authoritative XRPL Testnet JSON-RPC calls behind explicit boundaries.

## Directory Map

- `backend/app/integrations/xaman_service.py`: Xaman stub/API modes and payload status lookup.
- `backend/app/integrations/xrpl_client.py`: network-identity checks and validated transaction evidence retrieval.
- `backend/tests/unit/test_xaman_service.py`: deterministic Xaman boundary coverage.
- `backend/app/services/signing_reconciliation_service.py`: consumes payload status outcomes.

## Diagrams

```mermaid
flowchart LR
    prepare[Prepare route] --> xaman[xaman_service.py]
    xaman --> mode{XAMAN_MODE}
    mode --> stub[stub mode]
    mode --> api[api mode]
    api --> external[Xaman API]
    stub --> response[deterministic sign request]
    external --> response
```

## Maintenance Notes

- Local and CI should use `XAMAN_MODE=stub`.
- `XAMAN_MODE=api` requires environment-managed `XAMAN_API_KEY` and `XAMAN_API_SECRET`.
- Keep external failures mapped to retry-safe route behavior.
- XRPL pending/unavailable responses must not become terminal idempotency records.
- Do not let integration calls own lifecycle transitions.

## Related Docs

- `docs/xaman-signing-contract.md`
- `docs/operations-runbook.md`
- `docs/testnet-release-readiness.md`
- `backend/app/services/README.md`
