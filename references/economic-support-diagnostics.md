# Economic support diagnostics (economic-support-diagnostics/1)

A read-only, validation-level view of which revenue-bearing parameters are actually covered by a scoped referenced-range calibration. It answers "which segment/year/scenario cells are supported, and exactly why the others are not" without recomputing the forecast and without adding any approval, gate or new source identity. It is a diagnostics view, not a buyer-grade economic quality certification.

## Scope model

- **Independent range endpoints** prove their real parameter, unit, observed period and declared reference scope; they may sit outside the revenue DAG. An unused upper bound remains a legal reference.
- **Actual conversions and forecast outputs** must bind to the target business, scenario, period and the real native DAG. Unrelated scope or period cannot be promoted by a textual calibration label; a cross-scope benchmark needs an explicit reviewable conversion relation.
- A direct conversion's native annual `period` must match its output's applicability, and a direct output must match the year of the actual consumed revenue/recognition cell. A mismatch adds specific parameter/output/claim/segment/scenario/period reasons and leaves optional support unverified; forecasting still runs. Source dates and historical observations are not an equality gate. An explicit native bridge can retain old provenance and derive a target-period conversion.
- Support never propagates from one driver to other segments, scenarios or forecast years. `unknown` is never filled with zero and `stress` is never renamed a calibration.

## CLI

```
python -X utf8 -B scripts/research_support_diagnostics.py --input <native-input.json> [--output <new-path>]
```

`--input` is the authored native forecast input (read-only). `--output` writes the diagnostics JSON to a **new** path; an existing file is never overwritten. Without `--output` the JSON prints to stdout. Invalid or non-validating input exits non-zero with the contract error on stderr.

Output fields: `schema_version="economic-support-diagnostics/1"`, `input_sha256` (SHA-256 of the input bytes), `requested_years`, `company`, `segments` and `economic_truth_inferred=false`. Each segment carries one entry per scenario x forecast year:

- `status`: `supported` (every revenue root covered by a referenced-range calibration), `conditional` (some covered), `unsupported` (none, or no optional research).
- `supported_parameter_ids` / `unsupported_parameter_ids`: the segment's revenue roots (driver and recognition IDs) for that cell.
- `calibration_ids` / `claim_ids`: the referenced calibrations covering the cell and their source claims.
- `reasons`: concrete relation/ID reasons — `parameter_without_referenced_range_calibration:<pid>`, `calibration_scope_not_covering:<calibration>:<segment>`, `calibration_not_referenced_range:<calibration>:<engine reason>` (carrying `conversion_observation_unverified_scope|_period:<parameter>:<claim>`, `calibration_scope_not_native_business:<scope>`, `calibration_output_scope_mismatch:<output>:<scope>-><actual>`), or `no_optional_operating_research_declared`. Never a single generic "insufficient".

The CLI calls no model, no download and no forecast compute; it validates the document and projects the same diagnostics the engine emits. It writes nothing except its own new output and never touches the input, sources or any publication registry.

## What it does not establish

A green cell means the scoped range/conversion/output binding agrees, not that the magnitude is empirically accurate or probability-calibrated. Multi-driver cells are `conditional` until each root has its own evidence. Real company magnitudes, management-target control, three-year paths and joint stress still require original-document research; see the remaining-research list in the skill's operating-research steps.
