# RingLedger M4 Regression and Performance Gates

Last updated: 2026-03-01

## Purpose

Define explicit regression and performance baselines for M4 hardening closeout.

These gates are additive to existing lint, format, security, and integration checks.

## Regression Suite

Primary regression focus:

- failure taxonomy classification stability (`R-12`)
- deterministic replay-safe behavior assumptions used by confirm/reconcile flows

Command:

```bash
.\venv\Scripts\python.exe -m pytest backend/tests/regression -q
```

## Performance Suite

Primary performance focus:

- API liveness response loop baseline
- Xaman stub sign-request generation throughput baseline
- failure taxonomy classification throughput baseline

Command:

```bash
.\venv\Scripts\python.exe -m pytest backend/tests/performance -q
```

## Baseline Thresholds

| Metric | Baseline |
|---|---|
| `GET /healthz` loop (`250` requests) | completes in `< 10.0s` |
| Xaman stub sign-request generation (`1000` requests) | completes in `< 8.0s` |
| failure taxonomy classification (`120000` operations) | completes in `< 4.0s` |

## Gate Policy

1. A threshold failure blocks M4 closeout acceptance until root-cause and mitigation are documented.
2. Threshold changes require:
   - documented rationale,
   - updated baseline values in this file,
   - updated traceability evidence.
3. Performance tests must remain deterministic and avoid network dependency.

## References

- `docs/traceability-matrix.md`
- `docs/operations-runbook.md`
- `docs/ci-cd.md`

