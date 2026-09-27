# RF-RATCHET-REST-A a20260923-01 — Evidence index

## RED (oracle, step 1)
- `scan_red.txt` / `scan_red.json` — full-row scan with the ratchet test's OWN `_max_complexity` (imported live) + independent twin (43/43 agreement): **exactly 8 failing rows repo-wide** = my 3 (calc 22>21, template 17>9, targets 114>88) + RATCHET-FIX 2 (confidence 32>23, model_extensions 27>10 [new-file]) + REST-B 3 (model_registry 28>9, revenue_core 23>6, revenue_publication 16>10).
- `family_inventory.json` / `family_inventory.txt` — 55-test family (16-module upward closure), `family_shas_before.txt` (aggregate `947AB2EC…`), `family_files.txt`, `supplement_family.json` (+6 text-scanning tests).

## Family runs
- `family_before/` — RED-context baseline on iso of production bytes: 14 failed / 554 passed / 3 skipped / 130 subtests. 12 pre-existing (named in handoff; corroborated by sibling RF-STEP9-TRIAGE `win_head` evidence), 2 = ratchet test aborting at sibling rows.
- `family_pre70dd/` + `compare_before_vs_pre70dd.json` — revert-strategy test (pre-70dd9f6e images): **8 green→red regressions + 33 failing subtests → revert disqualified** (tests distinguish).
- `family_after/` + `compare_before_after.json` — AFTER on final refactored files: 14/554/3, **all_outcome_changes = {} , regressions = []** (perfect green-before==green-after).
- `supp_before/`, `supp_after/` + `compare_supp_before_after.json` — 4/42/3 both sides, **zero outcome changes** (includes C4 mypy gate green).

## Type gate
- `mypy_full_after.txt` — `mypy scripts --no-error-summary --ignore-missing-imports`: **67 errors ≤ 69 baseline** (originals measured 69-ish; targeted: originals 5 errors in my3 → refactored 3, all pre-existing). See decision.md "Type gate incident" for the dict[str, Any]→Any fix.

## Differential behavior probe
- `probe_orig.json` (ORIG = production bytes), `probe_new.json` (NEW = iso final), `probe_compare.json` → **identical: true, 25/25 probes** (full JSON incl. order + exception type/message).

## GREEN + mutation non-vacuity (step 7)
- `green_unittest.txt` — scratch ratchet (sibling rows pinned only, my caps asserted byte-identical 21/9/88): both ratchet tests PASS.
- `scan_green_iso.json` / `.txt` — real unmodified table in iso: my rows not failing; only sibling rows fail; twin agreement re-checked.
- `mutation_green.json` / `mutation_green.out` / `mutation_scripts_forecast_calc.py.txt` / `mutation_scripts_generate_input_template.py.txt` / `mutation_scripts_research_targets.py.txt` — per row: re-inflate to production original → both CC impls flip (22/17/114) → ratchet's own FIRST AssertionError names that file (`<rel> max <actual> > <frozen>`).

## Integrity / shas
- `sha_reverify_after.txt`, `sha_reverify_final.txt` — frozen table `EB1A36CF…` unchanged; production sources = before-shas (never written); family aggregate unchanged; refactored shas: calc `605BE6E875C60A21…`, template `06591BE038E0B7DA…`, targets `E7E8ED6B63238304…`.
- Pre-images: `pre70dd/*.blob` (sha calc `98f2b591…`, template `e4593b14…`, targets `f8b6f073…`).

## Artifacts (attempt root)
`ORACLE.md` (step 1), `binding.json` (step 2), `commands.md` (step 3), `decision.md` (step 4), `changes.diff` (step 5, asserted exactly 3 files), `handoff.json` (step 6), evidence above (step 7), `recovery.md` (step 8). Scripts: `scan_ratchet.py`, `family_inventory.py`, `refactor_targets.py`, `diff_probe.py`, `mutation_green.py`, `compare_family.py`. Iso/scratch: `%TEMP%\rf-rest-a-iso2`, `scratch/` (scratch-only table pins, never shipped).
