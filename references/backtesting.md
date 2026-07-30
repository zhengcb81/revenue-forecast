# Immutable snapshots and backtesting v2

## Snapshot

`create` calls `run_forecast` (which validates and signs the publication receipt
before returning). Snapshot schema 2.0 hashes the canonical input and complete
forecast result, and binds both hashes to company, as-of date, forecast version,
engine version, forecast schema, and snapshot ID. Any input or result mutation
fails evaluation.

Legacy snapshots (schema 3.4 with a supported engine) pass `validate_snapshot`
as legacy read-only; only 3.5 snapshots carry a publication receipt and are
eligible for current-validated status.

```powershell
python scripts/revenue_backtest.py create input.json --version 2026-07-12-v1 --output snapshot.json
```

## Actuals

Require `actuals_schema_version="2.0"`, matching company/currency/unit, actuals
as-of date, sources (each with a `capture` receipt), actual evidence claims
(each binding `content_sha256` to the source `snapshot_sha256` and
`capture_receipt_sha256` to the source capture receipt), and company revenue.
Segment actuals are optional. Each record uses an exact-value claim; its source
must be published after the corresponding fiscal-year end and no later than
actuals as-of.

## Evaluation

```powershell
python scripts/revenue_backtest.py evaluate snapshot.json actuals.json --output backtest.json
```

Segment accuracy compares actual revenue against `effective_revenue` when
cross-segment constraints are present, falling back to `recognized_revenue`.
Evaluation returns absolute error, signed percentage error when defined, APE,
sMAPE, base-scaled error, interval coverage, and direction only for consecutive
observations. It summarizes company, segment, and horizon results and flags
nonconsecutive actual years.

When all actual revenue is zero, WAPE remains undefined but absolute error, MAE,
sMAPE, and base-scaled error remain visible.

The output includes `evaluation_sha256`, `backtest_id`, and a hash-linked
`accuracy_record`. Copy only that generated record into a later forecast's
`historical_accuracy_records`; confidence verifies its hash and imports WAPE
automatically. Never type WAPE manually.
