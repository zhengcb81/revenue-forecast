# decision.md — RF-RATCHET-FIX-2 / attempt a20260923-01 (LIVING DOC — final state)

**Predecessor one-liner**: `RF-RATCHET-FIX/a20260923-01` died mid-work on subagent infra failure with an
EMPTY closing (no dying analysis); its 38-file attempt is a READ-ONLY baseline — cited here (oracle §0 =
its frozen oracle verbatim), never written.

**Mandate (parent ruling (a), tight)**: reduce `scripts/analysis/confidence.py` 32→≤23 and
`scripts/model_extensions.py` 27→≤10 by code refactor ONLY (ratchet moves down; no cap/skip/xfail
changes). Other 6 rows = sibling cards REST-A / REST-B — untouched. **RESULT: BOTH ROWS FIXED** —
confidence 32→17 (cap 23), model_extensions 27→8 (cap 10); changes.diff = exactly the 2 files.

## 0. Per-row CC table (before → after) — measured with the test's own `_mccabe`/`_max_complexity`
(evidence/measure/per_function_cc_before.txt / _after_confidence.txt / _after_model_extensions.txt)

| row | file | function | CC before | CC after | notes |
|-----|------|----------|-----------|----------|-------|
| F1 | analysis/confidence.py | `calculate_confidence` | **32** | **3** | orchestrator only (was the violation) |
| F1 | analysis/confidence.py | `parameter_revenue_weights` | 17 | 17 | untouched |
| F1 | analysis/confidence.py | `_limitations` (new) | — | 16 | extracted |
| F1 | analysis/confidence.py | `_evidence_quality` (new) | — | 7 | extracted |
| F1 | analysis/confidence.py | `_sensitivity_metrics` (new) | — | 5 | extracted |
| F1 | analysis/confidence.py | `_explicit_model_share` (new) | — | 3 | extracted |
| F1 | analysis/confidence.py | `_quality_gates` (new) | — | 3 | extracted |
| F1 | analysis/confidence.py | **FILE_MAX** | **32** | **17** | cap 23 → PASS |
| N1 | model_extensions.py | `_validated_calculator` | **27** | **3** | nested `calculate` body extracted (was the violation) |
| N1 | model_extensions.py | `build_extension_specs` | 8 | 8 | untouched |
| N1 | model_extensions.py | `_check_driver_bounds` (new) | — | 8 | extracted |
| N1 | model_extensions.py | `_validate_calculated_output` (new) | — | 7 | extracted |
| N1 | model_extensions.py | `_resolve_paths` (new) | — | 5 | extracted |
| N1 | model_extensions.py | `_check_driver_numeric` (new) | — | 5 | extracted |
| N1 | model_extensions.py | `_validate_driver_paths` (new) | — | 4 | extracted |
| N1 | model_extensions.py | `_arr` / `_installed` / `_stores` / `_renewable` / `_aum` | 5/3/3/3/3 | 5/3/3/3/3 | untouched |
| N1 | model_extensions.py | `_equal`/`_bridge`/`_launch`/`_adoption`/`_inventory` | 2/2/2/2/2 | 2/2/2/2/2 | untouched |
| N1 | model_extensions.py | **FILE_MAX** | **27** | **8** | cap 10 → PASS |

RED reproduction (judged, live RF, evidence/red/ratchet_red_judged.txt): `analysis/confidence.py max 32 > 23`
AND `model_extensions.py max 27 > 10`, exactly oracle §2. Full-row scan + inlined twin cross-check agree
exactly on all 8 rows on HEAD b7a6a116 (evidence/measure/full_row_scan_before.txt vs
independent_crosscheck_before.txt).

## 1. Golden-lock verdict (checked FIRST per card) — **NO CONFLICT → model_extensions PROCEEDED**

- `tests/test_model_extensions_anchor.py::test_extension_module_is_version_controlled_content`
  (lines 126–139) reads `hashlib.sha256(model_extensions.py bytes)` but asserts **only `len(digest)==64`** —
  the digest value is never pinned → no source-byte lock to break. It also asserts `model_registry.py`
  still references `build_extension_specs` (mount point kept — name/signature unchanged).
- `tests/test_golden_behavior_lock.py` pins `canonical_sha256(run_forecast(result))` for 5 model
  families = **behavior** byte-hash ("byte-identical outputs") — preserved by zero-behavior refactor.
- **Runtime proof** (evidence/green/golden_lock_before.txt / golden_lock_after.txt):
  `tests/test_golden_behavior_lock.py tests/test_model_extensions_anchor.py` = **7 passed, 17 subtests**
  on the pristine tree AND **7 passed, 17 subtests** on the refactored tree; `tests/golden_behavior_hashes.json`
  sha unchanged (frozen_sha_proof.txt). No BLOCKED; no owner ruling needed.

## 2. Hunk → helper mapping (changes.diff = exactly 2 files; `git apply --check` + apply roundtrip
byte-exact vs judged files (evidence/integrity/… via applycheck), LF canonical per RF `.gitattributes` `*.py eol=lf`)

### 2.1 `scripts/analysis/confidence.py` (FILE_MAX 32 → 17) — 6 hunks
| hunk | extraction | helper | CC |
|------|-----------|--------|----|
| `@@ -63,22 +63,14 @@` | claim-quality / freshness weighted loop out of `calculate_confidence` | `_evidence_quality(validated, weights, parameters, claims, covered_weight) -> (source_quality, freshness)` | 7 |
| `@@ -113,7 +105,11 @@` | segment_total / explicit_total terminal-share block | `_explicit_model_share(result) -> float` | 3 |
| `@@ -146,31 +142,15 @@` | sensitivity concentration + tested-coverage block (history block moves back to caller) | `_sensitivity_metrics(sensitivities, weights, total_weight) -> (concentration, sensitivity_coverage)` | 5 |
| `@@ -188,17 +168,11 @@` | schema-version gate flags | `_quality_gates(data) -> dict[str, bool]` | 3 |
| `@@ -209,6 +183,21 @@` | limitations list construction (all appends, original order) | `_limitations(data, validated, result, covered_weight, historical_wape, historical_observations, usable_origins, sensitivities, explicit_model_share) -> list[str]` | 16 |
| `@@ -255,6 +244,80 @@` | new slim `calculate_confidence` orchestrator: weights/coverage preamble + history block stay inline (ternaries), helpers called in original evaluation order | `calculate_confidence` | 3 |

### 2.2 `scripts/model_extensions.py` (FILE_MAX 27 → 8) — 1 hunk `@@ -132,30 +132,83 @@`
nested `calculate`'s body extracted into 5 module-level helpers (same order of checks: unknown/missing
drivers → path lengths → per-value numeric → per-value bounds → calculator → output check):
| old block in nested `calculate` | helper | CC |
|---|---|---|
| unknown/missing driver rejection + resolved materialization | `_resolve_paths(model_id, dimensions, optional, drivers, years, error)` | 5 |
| per-path length + per-value loop | `_validate_driver_paths(model_id, dimensions, bounds, resolved, years, error)` | 4 |
| finite-numeric gate | `_check_driver_numeric(model_id, name, value, error)` | 5 |
| domain/bounds gate | `_check_driver_bounds(model_id, name, value, lower, upper, error)` | 8 |
| output finite/non-negative gate | `_validate_calculated_output(model_id, output, years, error)` | 7 |

`_validated_calculator` keeps its closure factory shape and `calculate(base_revenue, drivers, years)`
signature (public calculators unchanged); `build_extension_specs`, `EXTENSION_OPENING_BALANCES`, all
formula calculators untouched. **Zero behavior change**: expressions copied verbatim; exception types,
messages and evaluation order identical (verified hunk-by-hunk + by behavior evidence in §3–§4).

## 3. Family results (24 test files union = 17 confidence-touching + 7 model_extensions importers;
before = %TEMP% pristine iso (byte == live, iso_vs_live_hashes.txt: 0 mismatches), after = refactored)

| run | result | failures |
|-----|--------|----------|
| BEFORE (evidence/families/family_before_stdout.txt) | `2 failed, 283 passed, 149 subtests passed` (66.97s) | `test_zr708_backtest_reverify.py::test_c2_accuracy_record_consumed_by_confidence`, `adversarial/test_receipt_attacks.py::ReceiptAttackTests::test_context_fabrication_is_rejected_by_final_validation` |
| AFTER (evidence/families/family_after_stdout.txt) | `2 failed, 283 passed, 149 subtests passed` (283.99s) | SAME two |

**Before == After byte-for-byte on outcome**: the 2 failures are PRE-EXISTING, time-dependent baseline
failures (historical-accuracy future-leak gate; attestation E27) present on the pristine tree too — NOT
caused by this refactor. Predecessor's iso before/after (baseline citation) shows the identical pair.
Family file list (runs before AND after): test_golden_behavior_lock, test_scenarios_confidence,
test_backtest, test_zr708_backtest_reverify, test_buy_side_accuracy, test_management_targets,
test_growth_driver_tree, test_ca204_monthly_generalization, test_zr712_confidence_policy,
test_output_report, test_publication_pipeline, test_revenue_constraints, test_independent_targets,
adversarial/test_anchor_attacks, adversarial/test_receipt_attacks, test_zr705_draft_formal_swap,
test_zr1008_new_chain_cutover, test_model_extensions, test_model_extensions_anchor,
test_model_integration_bounds, test_models, test_generate_input_template, test_industry_end_to_end,
test_lifecycle_forecasts. Plus the ratchet test itself (§4) and `ruff check` on both refactored files =
`All checks passed!`.

## 4. GREEN shape (KEEP-RED 口径 — per parent ruling; evidence/green/*, evidence/mutation/*)

- `test_new_files_stay_simple` → **FULL GREEN** (`1 failed, 1 passed` — the pass is this test;
  green_after_model_extensions.txt) — model_extensions was its only violation. MUT2 below proves non-vacuity.
- `test_frozen_files_do_not_worsen` → **PER ROW**:
  - **F1 row (`analysis/confidence.py` 32→17 ≤ 23): PASS**, proven three ways: (a) the real test's
    first-abort iteration MOVED PAST the row — after the fix the emitted failure is the NEXT row
    `forecast/calc.py max 22 > 21` (green_after_confidence.txt), which can only happen if the
    `analysis/confidence.py` assert executed and passed inside the real test; (b) full-row scan shows
    F1 actual=17 ≤ 23; (c) MUT1 flip restores the F1 failure on demand.
  - **frozen-test overall GREEN = BLOCKED by 6 pre-existing masked rows** (F2 `forecast/calc.py 22>21`,
    F3 `generate_input_template.py 17>9`, F5 `research/targets.py 114>88` → REST-A; F4 `model_registry.py 28>9`,
    F6 `revenue_core.py 23>6`, F7 `revenue_publication.py 16>10` → REST-B) — out of card scope, routed to
    sibling cards. Recorded as KEEP-RED/keep-red-scoped per the family precedent, **NOT** an attempt
    failure. No third file touched to force overall green.
- Frozen invariant (evidence/integrity/frozen_sha_proof.txt): `tools/tests/test_complexity_ratchet.py`
  sha256 BEFORE == AFTER == `eb1a36cfd54a8b96e3b5dca6ca4b7a89ca6b1e1605d22eedb69f643245edd10a`
  (matches oracle §4's expected value); FROZEN_MAX/NEW_FILE_MAX byte-unchanged; zero skip/xfail/baseline/
  marker additions (none exist in the diff); whole `scripts/` tree in live RF: 0 changed files; RF source
  bytes == binding_before (delivery vehicle = changes.diff only).

## 5. Mutation (non-vacuous, both directions — mutants built by re-merging the refactor's own hunks,
evidence/mutation/make_mutants.py; CC measured with the test's own metric)

| id | mutation | measured CC | ratchet message flipped to | restore flips back to | judgment |
|----|----------|-------------|---------------------------|----------------------|----------|
| MUT1 | merge `_evidence_quality` + `_limitations` back into `calculate_confidence` | `calculate_confidence CC=24`, FILE_MAX=24 | `analysis/confidence.py max 24 > 23` (confidence_mut1_ratchet.txt) | `forecast/calc.py max 22 > 21` (confidence_restored_ratchet.txt) | message-flip both ways, barely-over (24>23) proves sensitivity |
| MUT2 | merge `_check_driver_bounds` gate back into `_validate_driver_paths` | `_validate_driver_paths CC=11`, FILE_MAX=11 | `model_extensions.py max 11 > 10` (model_ext_mut2_ratchet.txt) | `1 failed, 1 passed` — new-file test GREEN again (model_ext_restored_ratchet.txt) | red→green, barely-over (11>10) |

## 6. Evidence index (ATTEMPT = `<RF>\.planning\2026-09-19-three-project-history-audit\execution_runs\RF-RATCHET-FIX-2\a20260923-01`)

- `oracle.md` — predecessor frozen oracle §0 (verbatim) + dated APPEND A (continuation plan, pre-judged-run)
- `binding.json` + `evidence/integrity/` — key_shas_before.json, scripts_manifest_before.json,
  iso_vs_live_hashes.txt (0 mismatches), porcelain_baseline/after.txt, frozen_sha_proof.txt
- `evidence/red/` — red_verbatim_command.txt (exit-4 `-B` rejection raw), ratchet_red_judged.txt (2 rows)
- `evidence/measure/` — full_row_scan_before.txt, independent_crosscheck_before.txt (+ the mandated
  reused scripts), per_function_cc_before/_after_confidence/_after_model_extensions.txt,
  make_changes_diff.py
- `evidence/green/` — green_after_confidence.txt (per-row move to F2), green_after_model_extensions.txt
  (new-file FULL GREEN), golden_lock_before.txt / golden_lock_after.txt (7 passed both)
- `evidence/mutation/` — make_mutants.py, confidence_mut1.py + _cc + _ratchet + restored_ratchet,
  model_extensions_mut2.py + mut2_cc + mut2_ratchet + restored_ratchet
- `evidence/families/` — family_before_stdout.txt / family_after_stdout.txt (283+149 both sides)
- `iso/` — confidence.py.baseline/.refactored, model_extensions.py.baseline/.refactored (pinned bytes)
- `changes.diff` (12078 bytes, exactly 2 files) / `commands.md` / `handoff.json` / `recovery.md`

## 7. Deviations / disclosures

- Verbatim RED command (`… -B` trailing) rejected by pytest (exit 4) — same disclosure as predecessor
  §7; judged form = `python -B -m pytest …` (interpreter-flag equivalent). Both raws kept.
- WSL cross-check: OPTIONAL — decision = **Windows-only** (no WSL run executed).
- Refactor provenance: helper-extraction shape adopted from the predecessor's in-flight `iso/*.fixed`
  candidates after this attempt's own hunk-by-hunk review and full independent verification (CC,
  family before/after, golden-lock byte-proof, mutation flips, apply roundtrip); `.orig` baselines
  verified byte-equal to live sources at adoption. The judged runs are this attempt's own.
- Working-tree porcelain delta during the attempt = **concurrent sibling agents in the shared
  workspace** (RF-STEP9-TRIAGE/…, BOOKKEEP-REPAIR/, I-08-C-RESIDUAL/, I-10-A/, PUSH-LOGS-ARCHIVE/,
  REGISTRY-CLOSURE/, OWNER_DECISIONS.md) — zero delta paths from this attempt, zero production sources.
- 2 pre-existing family failures (§3) predate this card on the pristine tree; time-dependent gates
  (historical-accuracy future-leak, attestation E27) — flagged for the parent, out of scope here.
