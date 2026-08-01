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

## Snapshot version discipline

A snapshot is immutable: its `snapshot_id`, `input_sha256`, and
`forecast_result_sha256` bind the exact input and result it froze. Any input
field change — including conclusion wording, source registration, or target
metadata — produces a different `input_sha256` and therefore requires a **new
version label** (`2026-08-01-v2`, never reuse `-v1` for different content).

- Never delete or overwrite an already-published snapshot file; `write_new_json`
  refuses to overwrite an existing path (`FileExistsError`, pinned by
  `test_backtest.py::test_write_new_json_refuses_overwrite`).
- If a snapshot must be superseded, keep the old file, create a new version
  label, and record the old `snapshot_id` and the reason in `progress.md`.
- Validate a new snapshot with `validate_snapshot` (fingerprint + ID
  consistency) and, for determinism, confirm a re-run of `create` on the same
  input yields the same `snapshot_id`.
- Note: `create` freezes `input + forecast_version` (the version label is part
  of the frozen document), so `snapshot.input_sha256` is not byte-identical to
  the receipt's `validated_input_sha256`; both are internally consistent and
  deterministic.

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
