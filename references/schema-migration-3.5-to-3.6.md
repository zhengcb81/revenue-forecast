# Schema 3.5 → 3.6 Migration Guide

## What changed

| Aspect | 3.5 (legacy) | 3.6 (current) |
|---|---|---|
| `FORECAST_SCHEMA_VERSION` | `"3.5"` | `"3.6"` |
| Growth-driver attribution weight | `(0, 1]` (positive only) | `[-1, 1]` excluding zero; negative weight = quantified revenue headwind |
| Negative roots | Rejected by validator | Reported in `growth_driver_analysis.headwinds[]`; excluded from `top_drivers[]` |
| Segment weight sum | 1.0 per segment | Still 1.0 per segment (positive and negative roots net to one) |
| Reconciliation | Driver increments reconcile to segment increment | Unchanged — signed weights still reconcile |
| Legacy schemas | 3.0–3.4 | 3.0–3.5 |

A negative root must keep its segment's total attribution equal to 1.0; a
driver with weight `0` is rejected, and weights outside `[-1, 1]` are rejected.

## How to migrate

### 1. Re-run the forecast

A 3.5 artifact must be **re-computed** with the current engine to become a
3.6 artifact. Do not change the `schema_version` field and recompute the hash —
the output validator will reject it because the artifact carries a legacy
`schema_version`.

```bash
python scripts/revenue_forecast.py input.json --output forecast.json
```

### 2. Validate legacy artifacts

3.5 artifacts can be **validated as legacy read-only**:

```python
legacy["schema_version"] = "3.5"
legacy["engine_version"] = "3.10.0"
legacy["result_sha256"] = canonical_sha256({k: v for k, v in legacy.items() if k != "result_sha256"})
validate_forecast_output(legacy)  # passes as legacy — no publication_receipt required
```

Legacy artifacts are marked `legacy_read_only_validated` and must not be
consumed by `invest-*` skills.

### 3. Backward compatibility

Existing inputs with only positive weights (weights in `(0, 1]`) continue to
validate unchanged — the `[-1, 1]` range is a strict superset. No field
renames, no new required keys, and no change to the reconciliation formula.

### 4. Snapshot compatibility

Snapshots with schema 3.4/3.5 and a supported engine version pass
`validate_snapshot` as legacy. Only 3.6 snapshots carry a publication receipt
and are eligible for current-validated status.
