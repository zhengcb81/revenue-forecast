# Immutable snapshots and backtesting (engine 4.1.0)

## Snapshot

`create` calls `run_forecast` (which validates and signs the publication receipt
before returning). Snapshot schema 2.0 hashes the canonical input and complete
forecast result, and binds both hashes to company, as-of date, forecast version,
engine version, forecast schema, and snapshot ID. Any input or result mutation
fails evaluation.

The current engine emits canonical forecast schema 3.7 or opt-in 3.8 under
snapshot schema 2.0. Compatibility depends on both schema and emitting engine,
as defined by `schema_compatibility.py`. Keep old snapshots byte-for-byte and
use their pinned emitting runtime when required; do not change an old engine
version to make it pass the new validator. Adopt revised models with a new
input and forecast version.

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
actuals as-of. The actual must also not already have been published at the
forecast origin. Freeze forecast inputs before knowing the actual result;
evaluating a retrospective reconstruction is not evidence of prospective skill.

## Evaluation

```powershell
python scripts/revenue_backtest.py evaluate snapshot.json actuals.json --output backtest.json
```

Segment accuracy compares actual revenue against `effective_revenue` when
cross-segment constraints are present, falling back to `recognized_revenue`.
Evaluation summarizes company, segment and horizon records, flags nonconsecutive
actual years and measures direction only for consecutive observations. Sign
convention is **forecast minus actual**: a positive signed error or bias means
overprediction.

| Output | Definition and interpretation |
|---|---|
| `absolute_error`, `signed_error_amount`, `squared_error` | Magnitude, signed amount and squared amount for an observation |
| `signed_error`, `absolute_percentage_error` | Signed/absolute error divided by actual; undefined when actual is zero |
| `smape` | Twice absolute error divided by the sum of absolute forecast and actual; both zero gives 0 |
| `base_scaled_error` | Absolute error divided by the absolute base revenue; undefined for zero base |
| `mae`, `bias_amount`, `rmse` | Mean absolute error, mean signed amount and root mean squared error |
| `wape` | Sum of absolute errors divided by sum of absolute actuals |
| `within_interval`, `interval_coverage` | Whether actual falls between low/high, and the observed fraction covered |
| `scenario_width`, `mean_scenario_width` | High minus low for one observation and its mean; inspect together with coverage |
| `direction_accuracy` | Share of eligible consecutive observations with correctly forecast direction |

Low/high are conditional scenario bounds, **not probability quantiles**. More
coverage obtained by widening bounds is not sufficient evidence of a better
forecast. There is no declared nominal probability and no automatic claim of
an 80%/95% statistical prediction interval.

## Frozen-history benchmarks and scaled errors

`benchmark_diagnostics` currently uses the frozen **company** historical
revenue, not future actuals, to calculate:

- `flat_base`: every forecast year equals base-year revenue.
- `historical_cagr`: continue the first-to-last historical CAGR from base
  revenue, when history and positive starting revenue allow that calculation.
- MASE: model MAE divided by mean absolute consecutive annual changes in the
  training history; RMSSE: square root of model MSE divided by mean squared
  training changes. These are annual, nonseasonal scaling denominators, not
  estimates from future evaluation data.
- `mae_skill_vs_flat_base` and `mae_skill_vs_historical_cagr`: one minus model
  absolute-error sum divided by the corresponding benchmark error sum. Positive
  means lower error than that benchmark; negative means worse. Zero benchmark
  error makes the skill ratio undefined.

Missing or constant history makes the relevant MASE/RMSSE denominator undefined;
report null rather than introducing an epsilon or claiming perfect skill.
These company-level benchmarks do not imply that segment histories or a
seasonal-naive model were estimated. An unusually short or distorted historical
CAGR remains only a diagnostic benchmark, not a recommended forecast.

When all actual revenue is zero, WAPE remains undefined but absolute error, MAE,
sMAPE, and base-scaled error remain visible.

## Accuracy record 1.1 and point-in-time scoring

The output includes `evaluation_sha256`, `backtest_id`, and a generated
`accuracy_record` with `record_schema_version="1.1"`. Copy that complete record
into a later forecast's `historical_accuracy_records`; do not manually type a
WAPE or reconstruct a successful-looking summary.

The 1.1 record binds `company_name`, `currency`, `unit`, `fiscal_year_end`,
`forecast_as_of_date`, `actuals_as_of_date`, `snapshot_id`, `backtest_id`,
`evaluation_sha256`, `observations`, `wape`, `mae`, `mean_smape`,
`sum_absolute_error`, `sum_absolute_actual`, and `record_sha256`.
Current consumption validates:

1. The record hash, unique backtest ID and positive integer observation count;
   1.1 `backtest_id`, `snapshot_id` and `evaluation_sha256` must be lowercase
   64-character SHA-256 identifiers, with no duplicate snapshot counted twice.
2. Exact company/currency/unit/fiscal-year-end match with the consuming forecast.
3. `forecast_as_of_date < actuals_as_of_date <= current as_of_date`; future
   evaluations cannot improve a past forecast's score.
4. No duplicate forecast origin among 1.1 records. Select one appropriate
   evaluation per origin rather than adding repeated evaluations of the same
   forecast to inflate the sample.
5. Nonnegative error/actual totals, `wape = sum_absolute_error /
   sum_absolute_actual` when defined, and `mae × observations = sum_absolute_error`.

Across eligible records, historical WAPE is **pooled**:

```text
pooled WAPE = Σ sum_absolute_error / Σ sum_absolute_actual
```

Do not average WAPE percentages, even after weighting by observation count.
A record with all-zero actuals has undefined individual WAPE but its absolute
errors remain in the pooled numerator. The pooled value is undefined only
when the pooled actual denominator is zero.

Legacy 1.0 records remain readable and integrity-checked, but lack sufficient
identity, information-availability and denominator fields. They do not earn
historical-accuracy score or count as usable origins. The current history-score
component applies a conservative sample multiplier
`min(1, observations / 5, usable_origins / 3)`; this is a workflow policy, not a
calibrated probability or statistical independence correction. Several horizons
from one origin, overlapping periods and common macro shocks remain correlated.

## Integrity, authentication and accuracy are separate

An accuracy-record hash detects inconsistent or changed bytes relative to its
payload; it does not authenticate the author, prove that a cited backtest was
actually run, or make invented actuals true. The summary's `evaluation_sha256`
is a linkage value, not a digital signature or independent retrieval of the
evaluation. Retain the snapshot, actuals, evaluation and source captures for
reproduction. Host-signed source/publication receipts strengthen only the
specific trust boundary they cover. Do not describe an ordinary summary hash
as source authentication.

## Demonstrating improved forecast accuracy

For a real A/B comparison, freeze the old/simple model and proposed model using
the same company, revenue perimeter, information date and forecast horizon.
Register the candidate and benchmark before observing actuals. Repeat across
rolling origins and relevant lifecycle/industry cases, preserve failed launches
and downturns, and compare bias and error by horizon as well as aggregate WAPE.
Actuals first released after the origin are evaluation data, not training data;
document later accounting restatements separately.

This research procedure is not an automated rolling-origin experiment runner.
Do not claim that unit tests, higher evidence scores, additional formulas, or
one favorable evaluation establish better real-world accuracy. Training fit is
not a substitute for genuine held-out forecasts, and chronological validation
must respect information availability. See [Hyndman and Athanasopoulos:
forecast evaluation](https://otexts.com/fpp3/accuracy.html) and [time-series
cross-validation](https://otexts.com/fpp3/tscv.html).
