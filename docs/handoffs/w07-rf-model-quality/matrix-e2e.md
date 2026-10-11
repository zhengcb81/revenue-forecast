# Model Generalization Matrix (`model-generalization-matrix/1`)

- generated_at: 2026-10-11T18:25:40.620728+00:00
- wall_seconds: 3.006072
- source_truth_verified: False
- economic_reasonableness: not_evaluated

Finite cross-mechanism combination stress matrix over the native draft engine. Synthetic engineering vectors; no real company, no source truth, no buy-side conclusion.

## Counts

| total | passed | failed | reject_ok | reject_mismatch | errored | not_run |
|---|---|---|---|---|---|---|
| 16 | 11 | 0 | 5 | 0 | 0 | 0 |

## Class status

| class | status |
|---|---|
| M01 | PASS |
| M02 | PASS |
| M03 | PASS |
| M04 | PASS |
| M05 | PASS |
| M06 | PASS |
| M07 | PASS |
| M08 | PASS |

## Cases

### M01-L — PASS

- class: M01  vector: legal  mode: draft
- boundary: quantity x price computes revenue at an explicit currency/unit label
- expected: `{"values": {"revenue": {"2026": 50.0, "2027": 60.0}}, "reject": false, "reject_reason": null, "unknown_fields": []}`
- observed: `{"revenue": {"2026": 50.0, "2027": 60.0}}`
  - ✓ input_driver[units] (input): expected=[10.0, 12.0] observed=[10.0, 12.0]
  - ✓ input_driver[unit_revenue] (input): expected=[5.0, 5.0] observed=[5.0, 5.0]
  - ✓ conversion[5.0 usd_million->usd_thousand] (value): expected=5000.0 observed=5000.0
  - ✓ revenue.2026 (value): expected=50.0 observed=50.0
  - ✓ revenue.2027 (value): expected=60.0 observed=60.0

### M01-C — REJECT_OK

- class: M01  vector: counter  mode: draft
- boundary: mixed currency/units are refused or explicitly converted, never auto-FX
- expected: `{"values": {}, "reject": true, "reject_reason": "incompatible unit conversion", "unknown_fields": []}`
- observed: `{"attempts": ["usd_million->rmb_million: ForecastInputError: incompatible unit conversion: usd_million -> rmb_million", "percent->usd_million: ForecastInputError: incompatible unit conversion: percent -> usd_million"], "all_rejected": true}`
  - ✓ mixed_units_rejected (reject): expected=True observed=True

### M02-L — PASS

- class: M02  vector: legal  mode: draft
- boundary: closing ARR is not full-year revenue; revenue follows the committed bridge
- expected: `{"values": {"revenue": {"2026": 105.0, "2027": 136.25}}, "reject": false, "reject_reason": null, "unknown_fields": []}`
- observed: `{"revenue": {"2026": 105.0, "2027": 136.25}}`
  - ✓ input_driver[opening_arr] (input): expected=[100.0, 125.0] observed=[100.0, 125.0]
  - ✓ input_driver[new_arr] (input): expected=[20.0, 30.0] observed=[20.0, 30.0]
  - ✓ revenue.2026 (value): expected=105.0 observed=105.0
  - ✓ revenue.2027 (value): expected=136.25 observed=136.25

### M02-C — REJECT_OK

- class: M02  vector: counter  mode: draft
- boundary: a missing ARR driver is refused, never zero-filled
- expected: `{"values": {}, "reject": true, "reject_reason": null, "unknown_fields": []}`
- observed: `{"exception": "ForecastInputError: research parameter_id subscription_arr_bridge_new_arr_2026_base for growth_curve is not used by the revenue model"}`
  - ✓ reject_reason (reject): expected=(any non-empty contract reason) observed=research parameter_id subscription_arr_bridge_new_arr_2026_base for growth_curve is not used by the revenue model

### M03-L — PASS

- class: M03  vector: legal  mode: draft
- boundary: demand is capped by capacity; the launch fraction is applied exactly once
- expected: `{"values": {"revenue": {"2026": 80.0, "2027": 480.0}}, "reject": false, "reject_reason": null, "unknown_fields": []}`
- observed: `{"revenue": {"2026": 80.0, "2027": 480.0}}`
  - ✓ input_driver[eligible_units] (input): expected=[1000.0, 1200.0] observed=[1000.0, 1200.0]
  - ✓ input_driver[annual_supply_capacity] (input): expected=[80.0, 300.0] observed=[80.0, 300.0]
  - ✓ revenue.2026 (value): expected=80.0 observed=80.0
  - ✓ revenue.2027 (value): expected=480.0 observed=480.0

### M03-C — PASS

- class: M03  vector: counter  mode: draft
- boundary: zero capacity yields finite zero revenue, never unbounded growth
- expected: `{"values": {"revenue": {"2026": 0.0, "2027": 0.0}}, "reject": false, "reject_reason": null, "unknown_fields": []}`
- observed: `{"revenue": {"2026": 0.0, "2027": 0.0}}`
  - ✓ input_driver[annual_supply_capacity] (input): expected=[0.0, 0.0] observed=[0.0, 0.0]
  - ✓ revenue.2026 (value): expected=0.0 observed=0.0
  - ✓ revenue.2027 (value): expected=0.0 observed=0.0

### M04-L — PASS

- class: M04  vector: legal  mode: draft
- boundary: a cross-calendar partial window inside the FY is accepted at its real coverage
- expected: `{"values": {"months": 6.0}, "reject": false, "reject_reason": null, "unknown_fields": []}`
- observed: `{"months": 6.0, "annual": {"2026": 165.00000000000003, "2027": 181.50000000000003}}`
  - ✓ months (value): expected=6.0 observed=6.0

### M04-C — REJECT_OK

- class: M04  vector: counter  mode: draft
- boundary: a dated flow outside its declared FY window is refused, not zero-filled
- expected: `{"values": {}, "reject": true, "reject_reason": "must lie within the FY2026 window", "unknown_fields": []}`
- observed: `{"exception": "ForecastInputError: seg_bad: period_flow dates must lie within the FY2026 window (2026-01-01..2026-12-31) implied by fiscal_year_end 12-31"}`
  - ✓ reject_reason (reject): expected=must lie within the FY2026 window observed=seg_bad: period_flow dates must lie within the FY2026 window (2026-01-01..2026-12-31) implied by fiscal_year_end 12-31

### M05-L — PASS

- class: M05  vector: legal  mode: draft
- boundary: zero-base launch revenue is computable
- expected: `{"values": {"cagr": null, "terminal": 480.0, "annual": {"2026": 80.0, "2027": 480.0}}, "reject": false, "reject_reason": null, "unknown_fields": ["cagr"]}`
- observed: `{"cagr": null, "terminal": 480.0, "annual": {"2026": 80.0, "2027": 480.0}}`
  - ✓ unknown[cagr] (unknown): expected=None observed=None
  - ✓ cagr (value): expected=None observed=None
  - ✓ terminal (value): expected=480.0 observed=480.0
  - ✓ annual.2026 (value): expected=80.0 observed=80.0
  - ✓ annual.2027 (value): expected=480.0 observed=480.0

### M05-C — PASS

- class: M05  vector: unknown  mode: draft
- boundary: CAGR from a zero base is undefined=null, not 0 growth nor a bad forecast
- expected: `{"values": {"cagr": null}, "reject": false, "reject_reason": null, "unknown_fields": ["cagr"]}`
- observed: `{"cagr": null, "terminal": 480.0, "annual": {"2026": 80.0, "2027": 480.0}}`
  - ✓ unknown[cagr] (unknown): expected=None observed=None
  - ✓ cagr (value): expected=None observed=None

### M06-L — PASS

- class: M06  vector: legal  mode: draft
- boundary: a shared shock propagates once; the joint volume/price path conserves the delta
- expected: `{"values": {"delta_2026": -20.0, "delta_2027": 15.0, "delta_sum": -5.0}, "reject": false, "reject_reason": null, "unknown_fields": []}`
- observed: `{"delta_2026": -20.0, "delta_2027": 14.999999999999972, "delta_sum": -5.000000000000028, "baseline_annual": {"2026": 165.00000000000003, "2027": 181.50000000000003}, "stressed_annual": {"2026": 145.00000000000003, "2027": 196.5}}`
  - ✓ delta_2026 (value): expected=-20.0 observed=-20.0
  - ✓ delta_2027 (value): expected=15.0 observed=14.999999999999972
  - ✓ delta_sum (value): expected=-5.0 observed=-5.000000000000028
  - ✓ shock_applied_once (conservation): expected=-20.0 observed=-20.0

### M06-C — REJECT_OK

- class: M06  vector: counter  mode: draft
- boundary: a fixed shared cap that would force Low<=Base<=High is refused, not reordered
- expected: `{"values": {}, "reject": true, "reject_reason": "scenario ordering", "unknown_fields": []}`
- observed: `{"exception": "ForecastInputError: segment scenario ordering failed for Segment A/2027"}`
  - ✓ reject_reason (reject): expected=scenario ordering observed=segment scenario ordering failed for Segment A/2027

### M07-L — PASS

- class: M07  vector: legal  mode: draft
- boundary: a comparable annual target keeps its own value and basis
- expected: `{"values": {"comparison_value": 144.0, "measurement_basis": "annual_period"}, "reject": false, "reject_reason": null, "unknown_fields": []}`
- observed: `{"comparison_value": 144.0, "measurement_basis": "annual_period"}`
  - ✓ comparison_value (value): expected=144.0 observed=144.0
  - ✓ measurement_basis (value): expected=annual_period observed=annual_period

### M07-C — REJECT_OK

- class: M07  vector: counter  mode: draft
- boundary: a run-rate/period-end target is not re-labelled as the current annual figure
- expected: `{"values": {}, "reject": true, "reject_reason": "requires explicit annual recognized revenue conversion", "unknown_fields": []}`
- observed: `{"exception": "ForecastInputError: run_rate_at_period_end target requires explicit annual recognized revenue conversion: five_year_revenue_goal"}`
  - ✓ reject_reason (reject): expected=requires explicit annual recognized revenue conversion observed=run_rate_at_period_end target requires explicit annual recognized revenue conversion: five_year_revenue_goal

### M08-L — PASS

- class: M08  vector: legal  mode: draft
- boundary: support is scoped per segment/year/scenario; one calibrated cell never presumes another
- expected: `{"values": {"cells": {"Segment A|low|2026": "supported", "Segment A|base|2026": "supported", "Segment A|high|2026": "supported", "Segment A|base|2027": "unsupported", "Segment B|base|2026": "unsupported"}, "economic_truth_inferred": false}, "reject": false, "reject_reason": null, "unknown_fields": []}`
- observed: `{"cells": {"Segment A|low|2026": "supported", "Segment A|low|2027": "unsupported", "Segment A|base|2026": "supported", "Segment A|base|2027": "unsupported", "Segment A|high|2026": "supported", "Segment A|high|2027": "unsupported", "Segment B|low|2026": "unsupported", "Segment B|low|2027": "unsupported", "Segment B|base|2026": "unsupported", "Segment B|base|2027": "unsupported", "Segment B|high|2026": "unsupported", "Segment B|high|2027": "unsupported"}, "economic_truth_inferred": false}`
  - ✓ cells.Segment A|low|2026 (value): expected=supported observed=supported
  - ✓ cells.Segment A|base|2026 (value): expected=supported observed=supported
  - ✓ cells.Segment A|high|2026 (value): expected=supported observed=supported
  - ✓ cells.Segment A|base|2027 (value): expected=unsupported observed=unsupported
  - ✓ cells.Segment B|base|2026 (value): expected=unsupported observed=unsupported
  - ✓ economic_truth_inferred (value): expected=False observed=False

### M08-C — PASS

- class: M08  vector: unknown  mode: draft
- boundary: an unknown observed range/actual stays null, never coerced to 0
- expected: `{"values": {"unknown_stays_null": true}, "reject": false, "reject_reason": null, "unknown_fields": ["observed_range"]}`
- observed: `{"observed_range": null, "adequacy_status": "unverified"}`
  - ✓ observed_range_stays_null (unknown): expected=None observed=None
  - ✓ adequacy_unverified (unknown): expected=unverified observed=unverified

## Cleanup / residuals

- cleanup: `{"scratch_path": "C:\\Users\\郑曾波\\Projects\\_harness_worktrees\\w07\\rf-model-quality\\.tmp\\w07-e2e-owned\\.tmp\\w07-278cf5cb", "baseline": {"existed": false, "sentinel": null}, "restored_absent": true, "readonly_unchanged": true}`
- residuals: []
