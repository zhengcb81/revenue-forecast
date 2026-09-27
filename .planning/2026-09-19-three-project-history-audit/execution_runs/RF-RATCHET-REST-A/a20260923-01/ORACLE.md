# RF-RATCHET-REST-A — Step 1: ORACLE (frozen first)

Attempt: `a20260923-01` · Card: fix3 of the 8 masked complexity-ratchet violations (70dd9f6e fcap→main checkpoint trio) ·
Parent ruling in force: **refactor-DOWN only, NO frozen-cap changes** (raising caps = owner ruling, not granted).

## 1. The ratchet test (single source of truth)

- Test: `tools/tests/test_complexity_ratchet.py`
- Test file sha256 (FROZEN-TABLE-SHA): `EB1A36CFD54A8B96E3B5DCA6CA4B7A89CA6B1E1605D22EEDB69F643245EDD10A`
- `SRC = Path(__file__).resolve().parents[2] / "scripts"` → `<RF>/scripts` (confirmed live by scan: `SRC resolved ... exists=True`).
- Two gate rows: `test_frozen_files_do_not_worsen` (FROZEN_MAX table) and `test_new_files_stay_simple` (NEW_FILE_MAX=10 for files not in the table).
- Per-file metric `_max_complexity` = max over **top-level** `def`s (name not starting `test_`) of `1 + _mccabe(source segment)`; `_mccabe` counts `If/For/While/And/Or/ExceptHandler/comprehension/Assert/With` (+1 each; each `BoolOp` also adds `len(values)-1`, and its `And/Or` operator node itself +1 → a 2-value `and` contributes +3 inside an `if` header: If+1, op+1, len-1=+1). `class` methods and nested defs are not measured separately (nested code is charged to the enclosing top-level def). `test_`-prefixed top-level defs are excluded. `SyntaxError → 0`.

## 2. My three rows (RED numbers)

Row numbers below come from the ratchet test's OWN `_max_complexity`, imported live by `scan_ratchet.py`; an independently written twin (ast.walk traversal) agreed on **all 43 scanned files** (`files cross-checked by two implementations: 43`, no disagreements).

| # | file (rel to SRC) | actual | frozen | over by | driving function (cc) |
|---|---|---|---|---|---|
| 1 | `forecast/calc.py` | **22** | **21** | +1 | `collect_parameter_roles` (22) — next: `base_segment_parameter_ids` (18) |
| 2 | `generate_input_template.py` | **17** | **9** | +8 | `build_template` (17) — `main` is 8 |
| 3 | `research/targets.py` | **114** | **88** | +26 | `validate_management_target_coverage` (114) — `add_management_target_analysis` (12) |

Card's expected actuals (22 / 17 / 114) re-derived independently ✓.

## 3. Full-row RED scan (honest measurement; the test aborts at first failure)

`evidence/scan_red.txt` / `scan_red.json` — every FROZEN_MAX row + every NEW_FILE row, both implementations agreeing:

**Exactly 8 failing rows repo-wide** (the 8 masked violations), ownership split:

| failing row | actual>frozen | owner |
|---|---|---|
| `analysis/confidence.py` | 32 > 23 | sibling RF-RATCHET-FIX (in flight) |
| `model_extensions.py` [new-file] | 27 > 10 | sibling RF-RATCHET-FIX |
| **`forecast/calc.py`** | **22 > 21** | **this card (REST-A)** |
| **`generate_input_template.py`** | **17 > 9** | **this card (REST-A)** |
| **`research/targets.py`** | **114 > 88** | **this card (REST-A)** |
| `model_registry.py` | 28 > 9 | sibling REST-B |
| `revenue_core.py` | 23 > 6 | sibling REST-B |
| `revenue_publication.py` | 16 > 10 | sibling REST-B |

So among rows owned by this card the scan shows exactly my 3 failing; the other 5 failing rows are owned by sibling cards (and are also the honest reason overall gate RED persists after my rows go green). All other rows PASS (incl. at-cap: sensitivity 12/12, contracts/evidence 10/10, filing_fetch 23/23, fix_hashes 12/12, segments 15/15, lint_input 25/25, coverage 26/26, drivers 19/19, revenue_backtest 18/18, revenue_constraints 29/29, revenue_forecast 18/18, canary 5/5, publication_registry 16/16, source_preparation 17/17, revenue_report 146/150, company_wiki 17/18, document 31/32, trust_anchor 8/8, revenue_core? no. revenue_report has headroom +4.)

## 4. Test-family inventory (computed before any edit)

Method: `family_inventory.py` — static AST import graph over `scripts/`, **upward closure** from the 3 seeds (`forecast.calc`, `generate_input_template`, `research.targets`) = **16 modules**
(`analysis.confidence, analysis.sensitivity, contracts.document, forecast.calc, forecast.segments, generate_input_template, research.coverage, research.drivers, research.targets, revenue_backtest, revenue_core, revenue_forecast, revenue_publication, revenue_report, rolling_backtest, schema_compatibility`),
then every test file under `tests/` + `tools/tests/` referencing any closure module or owned path → **family = 55 test files** (`evidence/family_inventory.json`).

- Family aggregate sha256 (before): `947AB2EC03BA8082514413E5314F1F5DAF9FB8B6133F3C197B615B7218715387` (`evidence/family_shas_before.txt`, 55 lines).
- Includes golden lock (`tests/test_golden_behavior_lock.py`), the 3 template tests, ratchet test (`tools/tests/test_complexity_ratchet.py`), adversarial/receipt attacks, backtests, publication pipeline, journey/e2e tests.
- Note: closure transitively includes sibling-owned modules (confidence, model_registry? no — model_registry not in closure; confidence/revenue_publication are) → baseline run is pinned by an iso snapshot so sibling edits landing mid-flight cannot skew before/after comparison.

## 5. Strategy note (pre-70dd9f6e restore — tested, not assumed)

`git log 70dd9f6e..HEAD -- <3 files>` is empty → current content == content introduced by the checkpoint; `70dd9f6e^` images are the pre-images.

| file | pre-image cc (test / twin) | current cc | frozen |
|---|---|---|---|
| forecast/calc.py | **21 / 21** | 22 | 21 |
| generate_input_template.py | **9 / 9** | 17 | 9 |
| research/targets.py | **88 / 88** | 114 | 88 |

Pre-images sit *exactly at* the frozen caps → revert would be the trivial fix **iff behavior-identical**. But `git diff 70dd9f6e^ 70dd9f6e` shows the checkpoint shipped real behavior: `driver_value_bounds()` range validation replacing inline driver rules (calc), `EXTENSION_OPENING_BALANCES` foundation fields (calc), `segment_models`/`MODEL_REGISTRY`/`MONETARY_DIMENSIONS`/`--segment-model` CLI, changed `as_of`/`published_date`, per-model driver ids, opening-balance fields, unit/currency/scale fields (template), and targets.py +67 lines of conversion/benchmark logic. Reverting would delete live behavior, not just move branches. Decision rule per card: run the full family with pre-images installed; if anything distinguishes → **must refactor**. Evidence in `evidence/revert_family/`. (Refactor is the expected outcome; revert would have to be disclosed as revert-not-refactor with both shas.)

## 6. Frozen-table-sha invariant

- Before: `EB1A36CFD54A8B96E3B5DCA6CA4B7A89CA6B1E1605D22EEDB69F643245EDD10A`
- After (re-verified at handoff): see `evidence/frozen_table_sha_after.txt` — must be equal. No table edit is shipped, ever.

## 7. Binding pins (step 2)

| artifact | sha256 before |
|---|---|
| `scripts/forecast/calc.py` | `BC4F33D92738029AE1E146E6323A23E818C3ABEB7CDF173C9BCFA4C462B02F79` |
| `scripts/generate_input_template.py` | `F7C57911D5F85204B04D07DE02FDCF9BCDB2315CF0236181CD727986292870B1` |
| `scripts/research/targets.py` | `1C885DEAF4168BACBD7D445EC6E76DA93193132FCE3B6CA67FBED4E6C910C48B` |
| `tools/tests/test_complexity_ratchet.py` (frozen table) | `EB1A36CFD54A8B96E3B5DCA6CA4B7A89CA6B1E1605D22EEDB69F643245EDD10A` |
| family (55 tests, aggregate) | `947AB2EC03BA8082514413E5314F1F5DAF9FB8B6133F3C197B615B7218715387` |

## 8. Commands discipline (step 3)

- Git usage: **read-only only** (`git log`, `git diff`, `git show`) — no index/HEAD/checkout/worktree mutations.
- Production tree: read-only (iso copies under the attempt dir + `%TEMP%` copy); pytest runs only inside the `%TEMP%` iso copy (no `__pycache__`/`.pytest_cache` writes into RF).
- `%TEMP%` scratch: `%TEMP%\rf-rest-a-iso` (robocopy of RF excluding `.git`, caches, `.tmp-*`, review dirs) — disclosed; it is a plain file copy, not a git worktree (no `.git` metadata inside).
