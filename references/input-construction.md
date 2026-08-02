# Input Construction (Schema 3.6)

Building a schema 3.6 input from scratch is the slowest part of forecasting — a
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

## Engine enum quick-reference

These values are enforced by `scripts/revenue_core.py`. The guard test
`tests/test_input_construction_consistency.py` asserts the bullet lists below
stay aligned with the source constants, so edit both together.

- `TIME_BASES`: `annual`, `point_in_time`
- `PARAMETER_DIMENSIONS`: `revenue`, `quantity`, `ratio`, `revenue_per_unit`, `activity`, `revenue_per_activity`, `monetary_balance`, `area`, `revenue_per_area`, `backlog`, `coverage_units`, `reserve_volume`
- `MONETARY_DIMENSIONS`: `revenue`, `revenue_per_unit`, `revenue_per_activity`, `monetary_balance`, `revenue_per_area`, `backlog`
- `GROWTH_DRIVER_PERSISTENCE`: `multi_year_structural`, `cyclical`, `temporary`, `uncertain`
- `GROWTH_DRIVER_INFERENCE_DISTANCES`: `direct`, `one_step`, `analogical`, `contrary`
- `GROWTH_DRIVER_COUNTEREVIDENCE_STATUSES`: `found`, `searched_none_found`, `data_gap`

Binding rules (kept backtick-sparse on the bullet lines above so the guard can parse them):

- No `fiscal_year` time basis exists, and no `growth_rate` parameter dimension exists — express a growth rate as a `ratio`.
- Currency/scale: a parameter whose dimension is in `MONETARY_DIMENSIONS` must carry `currency` equal to the top-level `currency` and `scale` equal to the top-level `unit`.
- A historical-revenue claim `unit` must be exactly `{currency} {unit}` (for example `USD million`, `RMB 100M`), not the bare unit.
- Growth-driver tree: `horizon` is an object `{start_year, end_year}` (ints); each `segment_attribution` weight lies in `[-1, 1]` excluding zero (negative = quantified headwind) and all weights for a segment reconcile to 1.0; evidence lives in `evidence_nodes`, and every evidence claim has `target_type` `growth_driver` with `support_type` `rationale_support`.
- Recognition: a segment's `modeled_presentation` must equal its `presentation`, and `basis_claim_ids` must reference a `recognition_policy` claim (support_type `policy_support`).
- Sensitivity: a test may shock a parameter only if that parameter is referenced by the **base** scenario — low/high-only parameters are rejected.

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

## Build script skeleton

A per-company `build_input.py` turns researched numbers into a validating
`input.json` without hand-writing thousands of lines of JSON. The shape below is
the reusable pattern (worked example: Alphabet). It is a skeleton, not a shared
framework — every company's data is different, so do not generalize it into a
library.

### Helpers (define once per company)

```python
import hashlib, json

CURRENCY, UNIT, AS_OF = "USD", "million", "2026-08-01"
MONETARY = {"revenue", "revenue_per_unit", "revenue_per_activity",
            "monetary_balance", "revenue_per_area", "backlog"}
sources = {s["source_id"]: s for s in json.load(open("sources_meta.json", encoding="utf-8"))["sources"]}
parameters, claims = [], []

def sha(text):
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

def add_param(pid, kind, value, unit, period, definition, dimension, scenario,
              source_ids=None, claim_ids=None, rationale=None, time_basis="annual"):
    p = {"parameter_id": pid, "kind": kind, "value": value, "unit": unit,
         "period": period, "definition": definition, "dimension": dimension,
         "time_basis": time_basis, "scenario": scenario,
         "source_ids": source_ids or [], "claim_ids": claim_ids or []}
    if dimension in MONETARY:                      # currency/scale rule
        p["currency"], p["scale"] = CURRENCY, unit
    if rationale:
        p["rationale"] = rationale
    parameters.append(p)
    return pid

def add_claim(cid, source_id, target_type, target_id, support, locator, excerpt,
              extracted_value=None, unit=None, period=None):
    c = {"claim_id": cid, "source_id": source_id, "target_type": target_type,
         "target_id": target_id, "support_type": support, "locator": locator,
         "excerpt": excerpt,
         "excerpt_sha256": sha(excerpt),                  # hash ring: recomputable
         "content_sha256": sources[source_id]["capture"]["snapshot_sha256"],   # copied
         "capture_receipt_sha256": sources[source_id]["capture"]["receipt_sha256"],  # copied
         "verification_status": "opened_and_checked",
         "verified_by": "research-agent-" + AS_OF, "verified_date": AS_OF}
    if extracted_value is not None:
        c.update(extracted_value=extracted_value, unit=unit, period=period)
    claims.append(c)
    return cid
```

### Naming conventions

- Base segment revenue parameter: `<seg>_base_rev` (dimension `revenue`, scenario `all`).
- Growth-rate parameter: `<seg>_<scenario>_<year>_g` (dimension `ratio`; `analyst_assumption` for base, `scenario_stress` for low/high).
- Historical revenue claim: `claim_hist_<year>_<src>`, `target_type` `historical_revenue`, `target_id` `historical_revenue:<year>`.
- Segment base claim: `claim_<seg>_base`, `target_type` `parameter`, `support_type` `exact_value`.
- Recognition policy claim: `claim_rec_<seg>`, `target_type` `recognition_policy`, `target_id` `recognition:<SegmentName>`, `support_type` `policy_support`.
- Growth-driver evidence claim: `claim_gd_<eid>`, `target_type` `growth_driver`, `support_type` `rationale_support`.

### Build loops (in order)

1. **Sources** — register once in `sources_meta.json` (each with the 9-key `capture` object), load into `sources`.
2. **Historical revenue** — per year: `add_claim(target_type="historical_revenue", support="exact_value", extracted_value=…)`, append `{"year", "value", "claim_ids", "source_ids"}` to `historical_revenue`. Claim `unit` is `"{currency} {unit}"`.
3. **Segment base + reported total + rounding adjustment** — per segment: `add_claim` (`exact_value`) + `add_param` (`reported_fact`, `<seg>_base_rev`). Add `reported_total_revenue_parameter_id` and any `base_adjustment_parameter_ids` (`analyst_assumption` + `rationale_support`) so the segment sum reconciles to the reported total.
4. **Growth rates** — `for seg × year × scenario`: `add_param(<seg>_<scenario>_<year>_g, "ratio", …)`. Base rates come from research; low/high are multipliers or independent paths.
5. **Growth-driver evidence** — for each `evidence_nodes` entry: `add_claim(target_type="growth_driver", support="rationale_support")`.
6. **Recognition** — per segment: `add_claim("recognition_policy", "policy_support")`, set `recognition.basis_claim_ids`, and keep `modeled_presentation == presentation`.
7. **Assemble** the top-level document: `schema_version` 3.6, `currency`, `unit`, `fiscal_year_end`, `base_year`, `forecast_years`, `sources`, `parameters`, `evidence_claims`, `segments`, `reported_total_revenue_parameter_id`, `base_adjustment_parameter_ids`, `historical_revenue`, `research_coverage`, `management_communication_coverage`, `growth_driver_tree`, `management_targets`, `sensitivity_tests`, …

### Validate iteration (drive round-count down)

Run after every edit to `input.json`, not only at delivery:

1. `python scripts/lint_input.py input.json` — collect-all field/reference/hash/weight findings in one pass.
2. `python scripts/lint_input.py input.json --check-conclusion-facts --check-sensitivity-propagation` — the heuristic flags (conclusion digits without a backing claim; absolute-level sensitivity parameters shocked before the terminal year).
3. `python scripts/fix_hashes.py input.json` — recompute the two recomputable hash layers and sync the two copies.
4. `python scripts/revenue_forecast.py input.json --validate-only --verbose` — full engine validation, every violation grouped.
5. Repeat until clean, then drop `--validate-only` to emit `forecast.json` / `forecast.md`.
