# Input Construction (Schema 3.5)

Building a schema 3.5 input from scratch is the slowest part of forecasting — a
real 2026-07-30 exercise took 23 fail-fast rounds before the input validated.
Analysis of those failures: field-name/shape mistakes 65%, cross-reference
integrity 26%, hash self-consistency 9%. This page lists the conventions that
bite, the hash ring, and the helper tools that cut round-trips to 2-4.

## Helper tools (recommended order)

1. `scripts/generate_input_template.py` — emit a field-correct skeleton with
   FIXME placeholders (`--name`, `--base-year`, `--forecast-years`,
   `--segments`, `--currency`, `--unit`, `--output`).
2. Fill in business values and source excerpts; replace every `FIXME`.
3. `scripts/lint_input.py <file>` — collect-all static pre-flight. Reports every
   field-shape, reference-integrity, hash-staleness, and aggregate-weight problem
   in one pass (does not fail fast). Exit 0 when clean, exit 2 on any finding.
4. `scripts/fix_hashes.py <file>` — recompute and sync all input-side hashes in
   place. `--check` reports drift without writing (CI-friendly, exit 2 on drift);
   `--dry-run` previews changes.
5. `python scripts/revenue_forecast.py <file> --validate-only` — full engine
   validation. Add `--verbose` to report every input violation in one grouped
   pass instead of failing on the first.

## Counter-intuitive naming conventions

Each row below has caused real build failures; none is guessable from the field
name alone.

| Convention | Intuitive (wrong) | Correct |
|---|---|---|
| Capture version field | `schema_version` | `capture_schema_version` |
| Capture date field | `capture_date` | `captured_date` |
| Prompt-injection status | `none_detected` | `not_detected` |
| Historical target_id | `history_2022` | `historical_revenue:2022` |
| Recognition target_id | `recognition_policy` | `recognition:segmentName` |
| Recognition support_type | `rationale_support` | `policy_support` |
| Sensitivity field | `shock` | `shock_type` |
| percentage_point parameter | `down_value` / `up_value` | `shock_value` (positive) |
| `derived_fact` | `x0` / `x1` / `formula` only | also requires `input_parameter_ids` |
| `not_available` communication | `rationale` only | also `conclusion` / `checked_date` / `search_description` |
| `source.capture` object | ad-hoc fields | EXACTLY the 9-key strict set |

The 9 capture keys are: `capture_schema_version`, `capture_method`, `tool_name`,
`tool_call_id`, `captured_date`, `snapshot_sha256`, `content_treatment`,
`prompt_injection_status`, `receipt_sha256`. Any extra or missing key is rejected.

## Hash ring (only 2 layers are recomputable)

The engine checks four SHA-256 fields. `fix_hashes.py` recomputes the two
computable layers and syncs the two copies; the snapshot hash is opaque
(produced by the capture tool) and is never overwritten.

| Field | How it is derived | `fix_hashes.py` |
|---|---|---|
| `source.capture.receipt_sha256` | `canonical_sha256(capture minus receipt_sha256)` | recomputes |
| `claim.excerpt_sha256` | `text_sha256(excerpt.strip())` | recomputes |
| `source.capture.snapshot_sha256` | opaque capture-tool fingerprint | leaves as-is (warns if not 64-hex) |
| `claim.content_sha256` | copy of its source capture's `snapshot_sha256` | syncs |
| `claim.capture_receipt_sha256` | copy of its source capture's `receipt_sha256` | syncs |

`canonical_sha256(value)` = `json.dumps(value, ensure_ascii=False, sort_keys=True,
separators=(",", ":"))` encoded UTF-8, then SHA-256 hexdigest. `text_sha256(value)`
= SHA-256 of `value.strip()` encoded UTF-8. Both `fix_hashes.py` and
`lint_input.py` import these directly from `contracts.evidence`, so their
recomputed hashes match the engine byte-for-byte.
