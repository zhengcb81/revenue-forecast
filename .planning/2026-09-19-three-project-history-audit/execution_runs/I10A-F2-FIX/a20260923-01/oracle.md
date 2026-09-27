# I10A-F2-FIX oracle.md — FROZEN EXPECTATIONS (written before the first judged product edit)

Attempt `a20260923-01`. This file is the frozen expectation face of card **I10A-F2-FIX**
(F-I10A-2, HIGH product defect, route: I-10-B fix-surface extension + E-1..E-7 erratum
same-track; owner order 「发现的缺陷都要全部修复」).

Freeze discipline: every expectation below is derived from FROZEN inputs (I-10-A finding
text, I-10-B registry contract, M-card D specs, measured PRE-FREEZE baselines) — NOT from
calling any fixed code. Freeze record (sha + timestamp) is appended to
`evidence/run_log.jsonl` as `ORACLE-FREEZE`; **no judged run starts before it; this file
is not edited after it**. Product edits happen ONLY inside `iso/rf/**` (RF is READ-ONLY;
delivery = `changes.diff`).

## 0. Anchors (recomputed at attempt open; a mismatch stops the attempt)

| file (RF original == iso copy) | sha256 | role |
|---|---|---|
| `scripts/forecast/calc.py` | `bc4f33d92738029ae1e146e6323a23e818c3abeb7cdf173c9bcfa4c462b02f79` (14978 B) | defect site 1: `_optional_series` :126-139 `default: float = 0.0` |
| `scripts/forecast/segments.py` | `95555509bc8a30affe1bcde3bb658ee4e3211d3b91f0ac6b1038dfc6d79765dd` (27697 B) | defect site 2: fill site :101-110 (esp. :109 `float(spec.get("defaults", {}).get(driver, 0.0))`) |
| `scripts/model_registry.py` | `62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081` (30116 B) | I-10-B registry mechanism (post-promotion) — **MUST stay byte-identical** |
| `scripts/model_extensions.py` | `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911` (14475 B) | extension specs (`defaults={}` for all 8) — unchanged |

iso copy verified byte-identical to RF originals for all four before any edit.

## 1. Field-class split (RAISE vs default-tolerant) — frozen BEFORE edits

**Authority chain (supersession, per parent ruling + E-1..E-7 landing):**
1. Registry code contract (promoted, current production): `model_registry.py:401-413` —
   an omitted optional driver is legal ONLY when `spec.defaults` carries an explicit
   value; otherwise `ModelRegistryError("missing driver for {model}: {driver} has no
   explicit default")`. (I-10-B DEC-I10B-1 option (c); baseline 31 slots/24 models in
   I-10-B `oracle.md` `baseline_measurement_at_freeze.slots_by_driver`.)
2. M-card line-9 可选默认 **0 值条目** (e.g. `card_M03.md:9 {"timing_factor":1,"other_revenue":0}`,
   `card_M05.md:9 …"usage_revenue":0`, `card_M09.md:9 {"other_revenue":0}`) are
   **I-10-B 前口径** — superseded by errata **E-1..E-4** landed at
   `execution_runs/E1E7-ERRATA-LANDING/a20260921-01/evidence/landed_text/M05.md` §②③④
   (verbatim: 「这些 `defaults` 相位的冻结期望成立，恰恰依赖缺陷①的『静默补 0』」;
   E-4 additionally marks M24 `hand_notes.defaults` 「omitted -> 0」= 修复前口径).
   M-card line-9 **1.0/0.5 条目** agree with `spec.defaults` and stay authoritative.
3. Consequence frozen here: **GREEN REQUIRES mut_omit(other_revenue) → clean raise**
   (card GREEN clause), consistent with the promoted registry contract.

### RAISE list — omitted ⇒ clean error (31 slots / 24 models; = I-10-B frozen slots_by_driver)

| driver | slots | models (M-card line-9 citations of the superseded 0-default where applicable) |
|---|---|---|
| `other_revenue` | 14 | unit_sales(M03:9), capacity_utilization(M04:9), services(M07:9), resource(M09:9), infrastructure, bank_revenue, asset_management, real_estate_rental, advertising, gaming, delivery_pipeline, insurance_service, renewable_generation(ext), + 1 |
| `usage_revenue` | 3 | subscription(M05:9, E-1), cohort_subscription(M20:9, E-3), subscription_arr_bridge(M24:9, E-4) |
| `milestone_revenue` | 2 | licensing_commercial, milestone_royalty |
| `service_revenue` | 2 | licensing_commercial, milestone_royalty |
| `fixed_revenue` | 1 | usage_platform (M06:9 superseded-0) |
| `backlog_remeasurements` | 1 | project_backlog (M08:9 superseded-0) |
| `reserve_revisions` | 1 | reserve_depletion |
| `performance_fee_revenue` | 1 | asset_management |
| `franchise_system_sales` | 1 | retail_franchise (M14, E-2) |
| `recognized_fee_rate` | 1 | retail_franchise (M14, E-2) |
| `supply_revenue` | 1 | retail_franchise (M14, E-2) |
| `ancillary_revenue` | 1 | transport |
| `royalty_revenue` | 1 | licensing_commercial |
| `recognized_performance_fees` | 1 | aum_fee_bridge (ext) |

### default-tolerant list — omitted ⇒ fill with the DECLARED value, byte-identical (9 slots / 7 models)

| model | declared default | citation |
|---|---|---|
| unit_sales | `timing_factor=1.0` | `card_M03.md:9 {"timing_factor":1,…}` == `model_registry.py:223 defaults=` |
| capacity_utilization | `timing_factor=1.0` | `card_M04.md:9` == `:224` |
| subscription | `timing_factor=1.0` | `card_M05.md:9` == `:225` |
| services | `timing_factor=1.0` | `card_M07.md:9` == `:227` |
| cohort_subscription | `timing_factor=1.0`, `new_customer_revenue_fraction=0.5`, `churned_customer_lost_fraction=0.5` | `card_M20.md:9` == `:240` |
| delivery_pipeline | `timing_factor=1.0` | `card_M?` == `:241` |
| insurance_service | `timing_factor=1.0` | == `:243` |

Models with NO optional drivers (direct_growth, direct_revenue) and all `spec.required`
drivers are outside this contract (missing required already raises at `segments.py:78-79`).
Extension models (`model_extensions.py:171 defaults={}`) contribute 0 tolerant slots.
**The whitelist is the explicit `spec.defaults` data — never a blanket value.**

## 2. Raise-presence contract (entry layer)

Site `calc.py:126-139` + call site `segments.py:101-110`:

| input class | BEFORE (defect) | AFTER (frozen expectation) |
|---|---|---|
| optional driver key ABSENT, no declared default | silently `[0.0]*len(years)` | **raise ForecastInputError** with message byte-equal to the registry form: `missing driver for {model}: {driver} has no explicit default` |
| optional driver key ABSENT, declared default | `[spec.defaults[driver]]*len(years)` | unchanged: fill with the DECLARED value (same numbers ⇒ output byte-identical for this class) |
| optional driver key PRESENT (any value incl. explicit 0.0) | `resolve_driver_series(...)` | unchanged (explicit 0.0 remains accepted — fix forbids IMPLICIT filling, not the value 0; I-10-B R-B1-N3) |
| `driver_ids[driver]` present-but-malformed (`None`, non-list, wrong length) | existing `require` raises (`must be a list of parameter_ids` / `must contain one parameter_id per forecast year`) | unchanged (already never silent) |
| `driver_parameter_ids` not a dict / unknown / extra keys / missing required | existing raises at `segments.py:72-81` | unchanged |

Mechanics (frozen design): `_optional_series` signature keeps the name `default` but its
type becomes `float | None = None` where **`None` = "no declared default ⇒ absent must
raise"** (sentinel, no blanket value anywhere); call site passes
`spec.get("defaults", {}).get(driver)` instead of `.get(driver, 0.0)`.

Error shape (frozen): exception type `ForecastInputError` (subtype of ValueError,
`contracts/evidence.py:29`); CLI path `revenue_forecast.py:120-122` ⇒ stderr line
`error: missing driver for {model}: {driver} has no explicit default`, process **rc 2**.
Message must be byte-identical to `model_registry.py:410-412` so the two layers are
indistinguishable to probes/validators.

## 3. Invariants (violation = attempt failure)

- **I-1**: `model_registry.py` + `model_extensions.py` byte-identical before/after (registry
  semantics untouched; I-10-B contract is REUSED, not re-implemented).
- **I-2**: every path whose inputs already carry explicit values (I-10-A GREEN normal arm;
  all default-tolerant omissions) produces byte-identical outputs before/after (probe
  payloads compared modulo `started_at/finished_at` timestamps only).
- **I-3**: error shape exactly as §2 (type + message + rc 2); no new exception types.
- **I-4**: regression families: after-run outcomes == before-run outcomes per testcase id
  (mechanically diffed by `scripts/diff_family.py`); **no new skip/xfail** (baseline:
  10 skipped, 1 xfailed — the sets must be identical), no test deleted or renamed.
- **I-5**: RF product tree gets ZERO writes; all product/test edits live in `iso/rf/**`
  and are delivered as `changes.diff` hunks; no git; no network.
- **I-6**: golden lock (`tests/test_golden_behavior_lock.py` + `golden_behavior_hashes.json`)
  stays GREEN; its baseline hash may be refreshed ONLY under the §5 disposition G1
  (fixture gains explicit zero-valued optional parameters ⇒ metadata bytes change; all
  revenue series values must remain identical — asserted explicitly in step "golden value
  identity check").

## 4. rgm cases (rc legend frozen: 0=pass, 1=harness failure, 2=correctly rejected,
## 3=not as expected — same legend as I-10-A probe batch)

Harness = I-10-A's own `run_mapping_probe.py` (copied verbatim; sha pinned in binding),
4 cases × 5 arms, run against `iso/rf`.

- **RED (before edit — MEASURED pre-freeze, `evidence/probe_before/**`)**:
  `mut_omit_optional` = rc **3,3,3,2** (ZJ-MIN/ZJ-SMT/XM-PHONE survive with silent 0.0;
  XM-EV killed only by output mismatch 0≠2.8e9) — silent0 reproduced; `normal` = rc 0×4;
  `red_conv` = 2×4; `mut_swap_ids` = 2×4; `mut_swap` = 3×4 (equivalent mutant, F-I10A-3,
  stays 3 — NOT this card's defect).
- **GREEN (after edit)**: `mut_omit_optional` = rc **2×4** with recorded product refusal
  `error_type=ForecastInputError`, `error=missing driver for {resource|unit_sales}:
  other_revenue has no explicit default` (all 3 scenarios refused per instance);
  `normal` = rc 0×4 with payload byte-identical to `probe_before` modulo timestamps;
  `red_conv`/`mut_swap_ids` = 2×4 unchanged; `mut_swap` = 3×4 unchanged (equivalent
  mutant is expected to survive — registered, not "fixed"); default-tolerant arms
  (timing_factor omitted anywhere in families) unaffected.
- **MUTATION (non-vacuity)**: temporarily re-arm the blanket fill at the guard
  (`calc.py` returns `[0.0]*len(years)` when `default is None`) ⇒ re-run
  `mut_omit_optional` ⇒ must fall back to rc 3,3,3,2 (silent0 returns) and the
  crafted per-field-class omit case must pass silently again; restore the guard and
  re-run ⇒ rc 2×4 again. Guard removal must be provably the only thing standing
  between GREEN and RED.
- **Family non-vacuity**: default-tolerant omission (`unit_sales` with `timing_factor`
  absent) must still produce 1.0-filled identical values after the fix (declared-default
  path unaffected).

## 5. Regression families + measured pre-freeze flip surface + dispositions

**Baseline (BEFORE, iso pristine, `evidence/family_before_junit.xml`):** full pytest suite
`1169 passed, 59 failed, 10 skipped, 1 xfailed, 4 errors, 332 subtests passed` (the 59+4
are pre-existing environment-dependent failures, identical in the instrumented re-run —
observation plugin proven non-invasive).

**Families named by the card:** (a) forecast/calc + segments importer tests (= the whole
suite via `revenue_core`), (b) I-10-B registry tests (`test_model_registry_contract`,
`test_model_economic_guardrails`, `test_models`, `test_model_extensions*` + rerun of
I-10-B `frozen_regression_rerun.py` + byte-sha check of registry files), (c) I-10-A probe
suite (20 runs) + I-10-A `validate_adaptation.py` R1-R12 validator, (d) golden lock.

**Measured flip surface (pre-freeze, observation-only wrap of
`forecast.segments._optional_series`, `evidence/flip_surface_events.json`):** 1021
blanket-fill events → **58 distinct tests in 13 files** will raise after the fix unless
their fixture is explicitized. Disposition table (frozen):

| # | file (tests affected) | omitted classes seen | disposition |
|---|---|---|---|
| G1 | `tests/test_golden_behavior_lock.py` (1 test / 5 families) | resource.other_revenue, capacity_utilization.other_revenue, subscription.usage_revenue, project_backlog.backlog_remeasurements, reserve_depletion.other_revenue+reserve_revisions | **fixture change + hash refresh**: add explicit 0.0-valued optional parameters for exactly these drivers; `--update-golden`; I-6 requires all revenue series byte-identical (value-identity checked separately) |
| T1 | `tests/test_models.py` (6 tests) | 31 model.driver pairs incl. rejects-tests | **fixture change**: extend `CASES`/local driver dicts with explicit 0.0 series for undeclared-optional omissions so intent tests (continuity/stock-flow) reach their intended raise; asserted revenue values unchanged |
| T2 | `tests/test_industry_end_to_end.py` (5 tests) | all 31 pairs | **shared-builder change**: `model_document()` adds explicit 0.0 series for undeclared optional drivers (also serves `test_lifecycle_forecasts` 2 tests + `test_model_integration_bounds`) |
| T3 | `tests/test_zr709_zijin_journey.py` `_zijin_document` (7) | resource.other_revenue | **shared-builder change** (also serves `test_ca204` 3, `test_ca302` 6, `test_zr1008` 11, `test_zr1103` 1) |
| T4 | `tests/test_zr1007_mine_shadow.py` (9) | resource/unit_sales.other_revenue | **fixture change** (local builders) |
| T5 | `tests/test_zr601_asset_facts.py` (4) | reserve_depletion.other_revenue+reserve_revisions | **fixture change** (local builders) |
| T6 | `tests/test_zr602_asset_facts_basis.py` (2) | reserve_depletion + resource | **fixture change** (local builders) |
| T7 | `tests/test_zr605_mine_year_operation.py` (1) | resource.other_revenue | **fixture change** (local builder) |

Rows in these files whose baseline status is already failed/error stay failed/error
(I-4 compares statuses, not aspiration). Every fixture edit is test-plane, disclosed
per file in `decision.md` + delivered in `changes.diff` (parent ruling). No test may be
weakened: values added are 0.0 (neutral by formula) with declared dimensions; no
assertion may be deleted; no skip/xfail added.

**Known blind spot (frozen honestly):** the observation plugin cannot see subprocess
CLI runs; `scripts/generate_input_template.py:171-182` emits `spec.required` only (a
product-side generator that, post-fix, can emit documents lacking undeclared-optional
drivers — NOT a card-named site; disclosed in handoff as adjacent-surface follow-up
unless a family test actually flips on it). The AFTER-run junit diff is authoritative
for any missed flip and must still satisfy I-4 or be dispositioned here before delivery.

## 6. Boundaries

RF READ-ONLY (zero product writes outside this attempt's `iso/rf`) · no git · network=0 ·
fix surface = the two named sites (+ disclosed test-plane fixtures) · registry layer
byte-identical · no M-card/frozen-evidence edits (E-errata already landed; this card
registers none) · status ends `review_pending`, unsigned, unmapped, unproven — implementer
does not self-sign; F-I10A-2 disposition = `FIXED-pending-review`.
