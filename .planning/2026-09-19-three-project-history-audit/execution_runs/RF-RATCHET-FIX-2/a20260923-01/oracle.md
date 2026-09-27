# ORACLE (frozen) — RF-RATCHET-FIX / attempt a20260923-01

Frozen BEFORE the first judged run of this attempt. Pre-freeze activity is disclosed in §8.
Card = fix the two RF complexity-ratchet violations via CODE refactor only (ratchet doctrine:
complexity only ratchets DOWN; raising frozen caps = owner ruling NOT granted → FROZEN_MAX and
NEW_FILE_MAX are NEVER edited; no skip/xfail/baseline additions anywhere).

## 1. Measurement contract (read from the test file itself, before anything else)

- Test = `tools/tests/test_complexity_ratchet.py` (last touched `4750fecd` 2026-08-13, i.e. the
  ratchet test itself has been stable since 08-13 — register §55 line 1245 corroborates).
- **SRC root (confirmed by reading line 14)**: `SRC = Path(__file__).resolve().parents[2] / "scripts"`
  → `<repo>/scripts`. Frozen keys are relative to `scripts/`; the two named violations are
  `scripts/analysis/confidence.py` (frozen 23) and `scripts/model_extensions.py` (NEW_FILE_MAX 10,
  not in the frozen table).
- Per-function CC = `1 + _mccabe(ast.parse(source_segment))` over TOP-LEVEL FunctionDefs only
  (nested functions are counted inside their enclosing top-level segment; `test_*` names skipped).
  `_mccabe` adds +1 for each If/For/While/And/Or/ExceptHandler/comprehension/Assert/With NODE
  (BoolOp's `op` operand is visited as a child, so `a and b` = +2) and +len(values)-1 per BoolOp.
  **All CC numbers in this attempt are produced by importing the test module's own
  `_mccabe`/`_max_complexity` — no other linter is introduced.**
- `test_frozen_files_do_not_worsen` iterates `sorted(FROZEN_MAX.items())` and the first
  `assertLessEqual` failure ABORTS the test → only the lexicographically-first violating row is
  reported per run. `test_new_files_stay_simple` likewise aborts at its first violating file.

## 2. The two card-named violations (expected RED)

| # | file | actual CC | cap | origin (register §55) |
|---|------|-----------|-----|------------------------|
| 1 | `scripts/analysis/confidence.py` | 32 (`calculate_confidence`) | FROZEN 23 | `70dd9f6e` "[Checkout-checkpoint] from fcap to main" 2026-09-20 15:04 |
| 2 | `scripts/model_extensions.py` | 27 (`_validated_calculator`) | NEW 10 | `5db4734a` "owner-authorized: bring the extension model registry under version control" 2026-09-20 08:51 (4 min after last green #287) |

Expected RED on current code (exact card command):
- `test_frozen_files_do_not_worsen` FAILS: `AssertionError: 32 not less than or equal to 23 :
  analysis/confidence.py max 32 > 23` (confidence is the lexicographically first FROZEN key, so
  this is the message the current test emits).
- `test_new_files_stay_simple` FAILS: `AssertionError: 27 not less than or equal to 10 :
  model_extensions.py max 27 > 10`.
- → **2 failed**.

## 3. Full-row scan (8 violations total — disclosed here because it defines GREEN's honest shape)

Measured pre-freeze with the test's own `_max_complexity` (import-based scan
`evidence/measure/scan_all_violations.py` AND a fully inlined re-implementation
`evidence/measure/independent_crosscheck.py` — both agree exactly):

| row | file | actual | cap | violating since (git -1 of file) |
|-----|------|--------|-----|----------------------------------|
| F1 | analysis/confidence.py | 32 | 23 | 70dd9f6e, 09-20 15:04 (CAPSULE: card violation #1) |
| F2 | forecast/calc.py | 22 | 21 | 70dd9f6e, 09-20 15:04 |
| F3 | generate_input_template.py | 17 | 9 | 70dd9f6e, 09-20 15:04 |
| F4 | model_registry.py | 28 | 9 | 5fd82de7, 09-22 21:00 (promotion) |
| F5 | research/targets.py | 114 | 88 | 70dd9f6e, 09-20 15:04 |
| F6 | revenue_core.py | 23 | 6 | ec307d20, 09-22 20:44 (promotion) |
| F7 | revenue_publication.py | 16 | 10 | ec307d20, 09-22 20:44 (promotion) |
| N1 | model_extensions.py | 27 | 10 (new) | 5db4734a, 09-20 08:51 (CAPSULE: card violation #2) |

All 8 entered AFTER the last green run #287 (2026-09-20 07:47Z); the frozen table itself has not
changed since 08-13. F2–F7 are MASKED behind F1 by the first-abort iteration (that is why §55 saw
"棘轮 ×2" = 2 failing test METHODS, not 2 violating files).

**Scope ruling (parent, mid-attempt): this card fixes F1 + N1 ONLY. F2–F7 route to two new follow-up
cards REST-A (F2/F3/F5, the 70dd9f6e triplet) and REST-B (F4/F6/F7, the promotion trio). Do NOT
touch any third file to chase an overall-green.**

## 4. Expected GREEN shape (honest layering — per parent ruling, KEEP-RED family precedent)

- `test_new_files_stay_simple` → **fully GREEN** (N1 is its only violation) — report raw pass.
- `test_frozen_files_do_not_worsen` → reported PER ROW:
  - F1 row: PASS after refactor (CC 32 → ≤23), proven three ways: (a) the real test, iterating
    sorted keys, now passes F1 and proceeds to fail on F2 — a F2 failure message PROVES the F1
    assert executed-and-passed inside the real test; (b) full-row scan shows F1 actual ≤ 23;
    (c) mutation flip (§5) restores the F1 message on demand.
  - overall test: still RED on F2 (`forecast/calc.py max 22 > 21`) = **BLOCKED by 6 pre-existing
    masked rows, out of card scope, routed to REST-A/REST-B** — recorded as KEEP-RED/keep-red-
    scoped, NOT as an attempt failure.
- Frozen-table invariant: `tools/tests/test_complexity_ratchet.py` sha256 BEFORE == AFTER
  (expected `EB1A36CFD54A8B96E3B5DCA6CA4B7A89CA6B1E1605D22EEDB69F643245EDD10A`); FROZEN_MAX dict
  and NEW_FILE_MAX byte-unchanged; zero skip/xfail/baseline/pytest-marker additions anywhere.
- `changes.diff` touched set == exactly the two source files. RF production bytes == binding_before.

## 5. Expected MUTATION (non-vacuous, both directions)

1. confidence: merge refactored helpers back over cap (calculate_confidence > 23) → frozen test
   failure message flips back to `analysis/confidence.py max <X> > 23` → restore → F1 row green
   again (message moves back to F2). Counts: red→restore, judged as message-flip both ways.
2. model_extensions: merge helpers back (`_validated_calculator` > 10) → new-file test reds with
   `model_extensions.py max <X> > 10` → restore → **green** (full test). Counts: 1 red + 1 green.

## 6. Zero-behavior-change contract + test-family inventory (primary evidence)

Refactor = extract module-level helpers; identical outputs/exceptions/side-effects/evaluation
order; no signature changes; no frozen-value edits. Primary proof = full family runs BEFORE
(iso-pristine, byte == live per binding) and AFTER (iso-refactored), same environment:

Confidence-touching (17): tests/test_golden_behavior_lock.py (canonical full-result hash — the
behavior lock that covers confidence.py per its own docstring), tests/test_scenarios_confidence.py,
tests/test_backtest.py, tests/test_zr708_backtest_reverify.py, tests/test_buy_side_accuracy.py,
tests/test_management_targets.py, tests/test_growth_driver_tree.py,
tests/test_ca204_monthly_generalization.py, tests/test_zr712_confidence_policy.py,
tests/test_output_report.py, tests/test_publication_pipeline.py, tests/test_revenue_constraints.py,
tests/test_independent_targets.py, tests/adversarial/test_anchor_attacks.py,
tests/adversarial/test_receipt_attacks.py, tests/test_zr705_draft_formal_swap.py,
tests/test_zr1008_new_chain_cutover.py.

model_extensions direct importers (7): tests/test_model_extensions.py,
tests/test_model_extensions_anchor.py, tests/test_model_integration_bounds.py, tests/test_models.py
(imports EXTENSION_CASES from test_model_extensions), tests/test_generate_input_template.py,
tests/test_industry_end_to_end.py, tests/test_lifecycle_forecasts.py.

Union = 24 unique files (the "23" in the card dispatch was an arithmetic slip; both counts are
reported in decision.md; every listed file runs before AND after). Plus the ratchet test itself.
`grep` evidence for the inventory: tests importing `analysis.confidence` symbols directly = NONE
(consumers are scripts/revenue_core.py + scripts/revenue_report.py; tests reach confidence only via
run_forecast / validate_forecast_output recompute / result["confidence"] assertions); tests
importing model_extensions = the 7 above (grep evidence captured in decision.md).

Zero production writes: sources READ-ONLY; runnable iso in %TEMP%; pinned refactored copies +
changes.diff in the attempt dir; git mutations = none (read-only git verbs only).

## 7. Environment / invocation contract

- RED command per card, run verbatim first: `python -m pytest tools/tests/test_complexity_ratchet.py
  -q --basetemp %TEMP%\... -B` → pytest rejects trailing `-B` (exit 4, "unrecognized arguments").
  Disclosed; judged form = the interpreter-flag equivalent `python -B -m pytest
  tools/tests/test_complexity_ratchet.py -q --basetemp %TEMP%\<fresh>` (+ `-p no:cacheprovider`
  on family runs to keep the repo cache-clean). Both raws kept.
- WSL cross-check: OPTIONAL per card. Decision recorded in decision.md + evidence (Windows-only
  unless a WSL run is actually executed).

## 8. Pre-freeze disclosures (honesty; nothing here is a judged run)

- The card itself mandated reproducing RED first; before this file was frozen I executed (i) the
  verbatim RED command (failed on `-B`, exit 4 — saved), (ii) two working RED reproductions in the
  RF repo (2 failed, exact messages as §2 — saved), (iii) the two measurement scans of §3 and the
  per-function CC table of the two files. All raws are in evidence/red + evidence/measure.
- After this freeze the sequence re-runs cleanly: binding → judged RED re-run → iso copy →
  refactor → GREEN → mutation → restore. The judged RED re-run must match §2 exactly.
- Git reads used: log/-1/`ls-files` (read-only). RF working-tree baseline porcelain: REMEDIATION_REGISTER.md
  modified + untracked I-07-D/, RF-STEP9-TRIAGE/, .tmp-r41-mutation/, manifests/plan_inputs.json.bak
  (all pre-existing, none created by this attempt).

---

# APPEND A (2026-09-23 21:38 +01:00, dated continuation plan) — RF-RATCHET-FIX-2 / attempt a20260923-01

§0 above = VERBATIM frozen oracle of predecessor attempt `RF-RATCHET-FIX/a20260923-01`, which
DIED MID-WORK (subagent infra failure, EMPTY closing report — no dying analysis). Its attempt
directory is a READ-ONLY baseline: cited, never written. This appendix is frozen BEFORE any new
judged run of THIS attempt and supersedes §0 only where it says so explicitly.

## A0. What the predecessor actually left (baseline inventory, read-only — richer than the card's
~12-file estimate; 38 files under `RF-RATCHET-FIX/a20260923-01/`):
- RED evidence: `evidence/red/ratchet_red.txt`, `ratchet_red_iso_pristine.txt`, `ratchet_red_judged.txt`
  + `exact_command_note.txt` (verbatim `-B` trailing-flag rejection, exit 4, disclosed).
- Measurement: `evidence/measure/scan_all_violations.py` (import-based) + `independent_crosscheck.py`
  (fully inlined twin) — **method mandated for reuse**; `full_row_scan_after.txt` (iso, all 26 frozen
  rows + new-file scan) + `full_row_scan_final.txt`.
- Iso refactor work IN FLIGHT: `iso/confidence.py.orig|.fixed`, `iso/model_extensions.py.orig|.fixed`.
  `.orig` verified byte-identical to live sources at adoption time (sha256 E5C0B1AC…C5D7 confidence,
  9939480B…B911 model_extensions). `.fixed` = candidate helper-extraction refactors.
- GREEN/mutation raws in iso (`evidence/green/*`, `evidence/mutation/*`) and family before/after
  stdout (`evidence/families/*`, both = "2 failed, 283 passed, 149 subtests", same 2 PRE-EXISTING
  failures both sides).
- NOT delivered before death: oracle was frozen but `binding.json`/`decision.md`/`handoff.json`/
  `commands`/`changes.diff`/`recovery` were never written; no closing report.

## A1. Mandate under parent ruling (a) — TIGHT SCOPE (supersedes nothing in §3's row table):
fix exactly TWO rows: `scripts/analysis/confidence.py` 32→≤23 and `scripts/model_extensions.py`
27→≤10. The other 6 rows (F2–F7) = sibling cards REST-A (calc/template/targets) + REST-B
(model_registry/revenue_core/revenue_publication) — DO NOT TOUCH, do not chase overall green.
`changes.diff` = exactly those 2 files.

## A2. Continuation sequence (this attempt, judged runs only after this freeze):
1. `binding.json` — sha256 pins: both targets, `tools/tests/test_complexity_ratchet.py`, FROZEN_MAX /
   NEW_FILE_MAX values, whole `scripts/` tree manifest, git HEAD + porcelain baseline.
2. **Golden-lock gate FIRST for model_extensions** (card mandate): `tests/test_golden_behavior_lock.py`
   (pins `canonical_sha256(run_forecast(...))` per model family = BEHAVIOR byte-hash) and
   `tests/test_model_extensions_anchor.py` (reads `sha256(model_extensions.py bytes)` but asserts
   ONLY `len(digest)==64` — no pinned value). Verdict recorded in decision.md before refactoring;
   if a byte-lock had pinned values → model_extensions = BLOCKED-with-evidence. (Static reading says
   no pinned digest; runtime proof = both tests green before AND after.)
3. Judged RED in live RF repo (verbatim card command first — expect the disclosed exit-4 `-B`
   rejection — then `python -B -m pytest tools/tests/test_complexity_ratchet.py -q --basetemp
   %TEMP%\<fresh>`): must reproduce §2's two messages exactly.
4. Full-row scan (import-based + inlined twin must AGREE) re-measured on THIS HEAD (b7a6a116).
5. File 1 (confidence.py) in %TEMP% iso: helper extraction → per-function CC table → per-row GREEN
   proof (real test moves past `analysis/confidence.py` to the next failing row) → mutation flip
   both directions. Then File 2 (model_extensions.py), same shape. One file at a time.
6. Family runs (§6 union of 24 test files + ratchet) BEFORE (iso-pristine) and AFTER (iso-refactored),
   same environment; golden-lock + anchor included in the model_extensions family.
7. `changes.diff` (exactly 2 files) + frozen-sha proof + evidence pack + `recovery.md` → finalize
   `decision.md`/`handoff.json` (review_pending/unsigned) → report to parent.

## A3. GREEN reporting口径 (KEEP-RED family precedent, per parent ruling — unchanged from §4):
`test_new_files_stay_simple` = FULL green expected (N1 its only violation). `test_frozen_files_do_not_worsen`
= PER ROW: confidence row fixed + mutation flip proves non-vacuity; test overall remains RED until
sibling rows land → recorded honestly as "frozen-test overall GREEN = BLOCKED by 6 pre-existing masked
rows (sibling cards REST-A/REST-B)". NO third file is touched to force overall green.

## A4. Anti-death discipline: `decision.md` + `handoff.json` + `binding.json` written as LIVING docs
before the first judged run (status always current on disk); every run writes its evidence file
immediately. Zero behavior change: frozen table + test-file sha BEFORE == AFTER; no skip/xfail/cap
change; no git mutations; no network; scratch/basetemp/iso under %TEMP%.

## A5. Environment note: Windows, Python 3.13.9, RF HEAD b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb
(2026-09-23 19:51 +0100) at freeze time; RF working tree dirty with 55 porcelain lines (all
pre-existing planning/tmp artifacts, none from this attempt — recorded in binding.json).
