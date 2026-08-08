# Schema 3.4 → 3.5 Migration Guide

> Note: schema 3.5 has since been superseded by 3.6; this guide documents the
> historical 3.4→3.5 transition. For the current schema, see
> `schema-migration-3.5-to-3.6.md`.

## What changed

| Aspect | 3.4 (legacy) | 3.5 (current) |
|---|---|---|
| `FORECAST_SCHEMA_VERSION` | `"3.4"` | `"3.5"` |
| Publication receipt | None | Required — signed after output validation |
| Execution receipt | Lists `output_recomputation` gate (premature) | Does **not** list `output_recomputation` |
| Output validation | Separate step after `run_forecast` | Called inside `run_forecast` before return |
| Formal / draft | No distinction | `run_forecast(data, mode="formal"|"draft")` |
| Custom research dimensions | Rejected by output validator (`len == 9`) | Accepted (`len >= 9`, first 9 must be canonical) |
| Management communication | Free-text `not_available` | Structuralserch_event with `query_scope`, `query_time`, `event_ids` required when present |
| Sensitivity terminal check | Impact arithmetic only | Re-runs shock against the model |
| Probability contract | Only weighted arithmetic checked | Sum to 1, non-negative, three keys enforced |
| Target `meets_target` | Required to be `True` (trusted) | Re-derived from comparison operator and tolerance |
| Prohibited field scan | 5 explicit blocks | Full output tree with value-type distinction |
| File acquisition | Bundled acquisition module (removed in R3) | `filing_fetch_client.py` → standalone `filing-fetch` skill |

## How to migrate

### 1. Re-run the forecast

A 3.4 artifact must be **re-computed** with the current engine to become a
3.5 artifact.  Do not change the `schema_version` field and recompute the
hash — the output validator will reject it because the artifact lacks a
`publication_receipt`.

```bash
python scripts/revenue_forecast.py input.json --output forecast.json
```

### 2. Validate legacy artifacts

3.4 artifacts can be **validated as legacy read-only**:

```python
legacy["schema_version"] = "3.4"
legacy["engine_version"] = "3.10.0"
legacy["result_sha256"] = canonical_sha256({k:v for k,v in legacy.items() if k != "result_sha256"})
validate_forecast_output(legacy)  # passes as legacy — no publication_receipt required
```

Legacy artifacts are marked `legacy_read_only_validated` and must not be
consumed by `invest-*` skills.

### 3. Adapt consumers

- **invest-* skills** must only accept schema 3.5 artifacts with a valid
  `publication_receipt` in `formal` mode.
- **Filing-fetch** replaces the bundled acquisition module (removed in R3); use
  `filing_fetch_client.resolve_filing()` to obtain a handle.

### 4. Snapshot compatibility

Snapshots with schema 3.4 and a supported engine version pass
`validate_snapshot` as legacy. Only 3.5 snapshots carry a publication
receipt and are eligible for current-validated status.
