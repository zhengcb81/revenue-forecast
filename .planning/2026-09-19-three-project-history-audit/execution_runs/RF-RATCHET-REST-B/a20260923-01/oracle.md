# ORACLE (frozen) — RF-RATCHET-REST-B / attempt a20260923-01

Frozen BEFORE the first judged run of this attempt. Pre-freeze activity is disclosed in §9.
Card = fix the THREE RF complexity-ratchet violations that THIS session's owner-authorized
promotions introduced (`ec307d20` B1 promotion → `revenue_core.py` + `revenue_publication.py`;
`5fd82de7` MODEL promotion → `model_registry.py`) — i.e. clear OUR debt — via CODE REFACTOR
DOWN ONLY. Parent ruling binding on every line of this attempt:

* complexity ratchets DOWN only: `FROZEN_MAX` / `NEW_FILE_MAX` are NEVER edited; no
  skip/xfail/baseline/marker additions anywhere;
* promotion contracts preserved at the BEHAVIOR level: the promotion cards' own test
  batteries must run BEFORE and AFTER with identical results;
* byte-lock pre-check FIRST (mandated by card): if a golden-hash/attestation lock pins the
  BYTES of one of the three files, the only compliant option is STOP that row
  BLOCKED-with-evidence (option ii). Findings: §4 — **no byte-lock exists → helper-split path
  (option i) is open for all three rows**;
* structurally-unreachable row → STOP BLOCKED-with-evidence, no bypass;
* sibling cards own the other rows: RF-RATCHET-FIX = `analysis/confidence.py` + `model_extensions.py`;
  RF-RATCHET-REST-A = `forecast/calc.py` + `generate_input_template.py` + `research/targets.py`.
  This card touches EXACTLY its three `scripts/` files (changes.diff invariant §8).

## 1. Measurement contract (read from the test file itself, before anything else)

- Test = `tools/tests/test_complexity_ratchet.py` (sha256 `eb1a36cf…edd10a`, 3014 B — matches
  RF-RATCHET-FIX's binding pin; stable since 2026-08-13).
- **SRC root (line 14)**: `SRC = Path(__file__).resolve().parents[2] / "scripts"` → `<repo>/scripts`.
  Frozen keys are relative to `scripts/`.
- Per-function CC = `1 + _mccabe(ast.parse(source_segment))` over TOP-LEVEL `FunctionDef`s only
  (nested defs count inside their enclosing top-level segment; `test_*` names skipped).
  `_mccabe` adds +1 per If/For/While/And/Or/ExceptHandler/comprehension/Assert/With NODE —
  BoolOp's `op` operand IS visited as a child, so `a and b` = +2 — plus +len(values)-1 per BoolOp.
  **All CC numbers in this attempt are produced by importing the test module's own
  `_mccabe`/`_max_complexity`, cross-checked by a fully inlined re-implementation.**
  Consequence for the refactor: helpers must be TOP-LEVEL module functions (a nested helper
  would count inside its parent's segment), and every top-level function of a frozen file must
  land ≤ the file's cap, not just the current max.
- `test_frozen_files_do_not_worsen` iterates `sorted(FROZEN_MAX.items())`; the first failing
  `assertLessEqual` aborts → only the lexicographically-first violating row is reported per run
  (`analysis/confidence.py`, owned by sibling FIX — my rows are MASKED behind F1..F5).
  `test_new_files_stay_simple` likewise aborts at its first violating file
  (`model_extensions.py`, sibling FIX).

## 2. The three card-named rows (expected RED; measured pre-freeze, §9)

| # | file | actual CC | cap | max function (measured, §9 evidence) | introduced by |
|---|------|-----------|-----|--------------------------------------|---------------|
| R4 | `scripts/model_registry.py` | **28** | **9** | `calculate_registered_model` L374 = 28 (next: `_cohort_subscription` 7) | `5fd82de7` 2026-09-22 21:00 "promote(B-6c via MODEL-ORACLE-ALIGN): model_registry re-promotion (62f864b9 …)" — `git log -1 -- scripts/model_registry.py` = this commit |
| R6 | `scripts/revenue_core.py` | **23** | **6** | `_validate_attestation_response` L278 = 23; **second violator** `_run_attestation_provider` L203 = **19** (both must come ≤6) | `ec307d20` 2026-09-22 20:44 "promote(PROMOTION-EXEC B1-B2): revenue_core + revenue_publication + revenue_report (B1 I-08-C security fixes 8a761498/bc2bb4a3/212f0059)" — revenue_core +325 lines in that commit |
| R7 | `scripts/revenue_publication.py` | **16** | **10** | `validate_publication_attestation` L221 = 16 (next: `build_publication_receipt` 5) | `ec307d20`, same commit, +314 lines |

All three live production shas measured this attempt (byte-lock scan §4): model_registry
`62f864b9…985081`/30116 B, revenue_core `8a761498…ac883`/25842 B, revenue_publication
`bc2bb4a3…678fcd0`/24917 B — **exactly the promotion payloads' post-promotion pins**
(manifest `6759d1eb…`, PROMOTION-EXEC decision row B-1, MODEL-ORACLE-ALIGN decision §2).

Expected RED (judged runs, §7 sequence):
1. Full-row scan (import-based + inlined double-implementation) shows the 8 masked violations
   below including MY three rows — captured as `evidence/measure/scan_all_violations_before.txt`
   + `independent_crosscheck_before.txt` (both agree exactly) + per-function tables
   `measure_cc_before.txt`.
2. The real pytest run: `test_frozen_files_do_not_worsen` FAILS with
   `analysis/confidence.py max 32 > 23` (lexicographically-first row = sibling FIX);
   `test_new_files_stay_simple` FAILS with `model_extensions.py max 27 > 10` (sibling FIX)
   → **2 failed**. My rows are masked behind F1/F2/F3/F5 by the first-abort iteration —
   per-row RED evidence for my rows is the full-row scan, not the test's abort message.

## 3. Full-row scan (all 8 violations — defines GREEN's honest shape)

Measured pre-freeze with BOTH implementations (identical output):

| row | file | actual | cap | violating since | owner |
|-----|------|--------|-----|-----------------|-------|
| F1 | analysis/confidence.py | 32 | 23 | 70dd9f6e, 09-20 | RF-RATCHET-FIX |
| F2 | forecast/calc.py | 22 | 21 | 70dd9f6e, 09-20 | RF-RATCHET-REST-A |
| F3 | generate_input_template.py | 17 | 9 | 70dd9f6e, 09-20 | RF-RATCHET-REST-A |
| **F4** | **model_registry.py** | **28** | **9** | **5fd82de7, 09-22 (promotion)** | **THIS CARD** |
| F5 | research/targets.py | 114 | 88 | 70dd9f6e, 09-20 | RF-RATCHET-REST-A |
| **F6** | **revenue_core.py** | **23** | **6** | **ec307d20, 09-22 (promotion)** | **THIS CARD** |
| **F7** | **revenue_publication.py** | **16** | **10** | **ec307d20, 09-22 (promotion)** | **THIS CARD** |
| N1 | model_extensions.py (new-file cap 10) | 27 | 10 | 5db4734a, 09-20 | RF-RATCHET-FIX |

TOTAL frozen violations = 7, new-file violations = 1 (pre-freeze capture). The frozen table
itself has not changed since 08-13 (FIX oracle §1 corroborates; register §55 line 1245).

## 4. BYTE-LOCK PRE-CHECK (card-mandated, executed before any refactor decision)

Method (evidence `evidence/bytelock/bytelock_scan_before.txt`, produced by
`bytelock_scan.py` this attempt): (1) live re-hash of the three production files;
(2) full sha256 + 8-char + 12-char prefix literal search over `tests/` and `tools/`
(all text file types); (3) every line referencing the three file NAMES;
(4) every sha256/file-hashing call in `tests/` + `tools/`.

Findings:

1. **sha-literal hits = 0.** No test, gate, or fixture pins the bytes of any of the three
   files (full or prefix). Repo-wide corroboration: greps for the three full hashes over
   `tests/`, `tools/`, `assurance/` → no matches.
2. Name references = 15, all benign, three of them ASSERTION NEEDLES that the refactor MUST
   preserve (behavior-level locks, satisfiable by a helper split):
   - `tests/test_model_extensions_anchor.py:137-139` — `assertIn("build_extension_specs",
     model_registry_source)` (extension mount-point text must remain);
   - `tests/test_skill_documentation.py:116-123` — revenue_core source text must contain
     `"validate_published_forecast(result, data)"` at an index BEFORE
     `"build_publication_receipt("` (validate-before-sign ordering, literal positions);
   - `tests/test_structure_targets.py:25-29` — revenue_core.py line count ≤ 2500
     (currently 706; helpers add lines but stay far under).
   Remaining references: comments/docstrings (`test_model_economic_guardrails.py:27` cites
   `scripts/model_registry.py:410` **as a comment, not an assertion** — line numbers WILL
   shift; disclosed in decision.md), the ratchet table itself, and coverage floors
   (`tools/run_coverage_gates.py`: 70/70/80 — coverage gates, not byte pins).
3. Hashing calls (138 lines) all hash ARTIFACT/payload/vendored-guard data — enumerated in
   the scan output; `test_fc1307a` hashes `tools/host_assumption_guard.py` (not mine),
   `audit_baseline.py` hashes config files only, `release_gate.py` hashes report payloads.
   `tests/golden_behavior_hashes.json` (`4e68b98c…`) pins the canonical SHA of five
   **run_forecast RESULTS** — a BEHAVIOR lock (kept green unchanged = the primary
   zero-behavior proof), not a source-byte lock.
4. Promotion evidence pins (`8a761498…`/`bc2bb4a3…`/`62f864b9…` in REMEDIATION_REGISTER
   PROMOTION/GATE-OQ sections, `promotion_batch_manifest.md`, PROMOTION-EXEC/MODEL-ORACLE-ALIGN
   carriers) are **historical evidence hashes of the promotion payloads, re-read this attempt
   and matching today's production bytes**; no test or gate re-verifies them at runtime.

**VERDICT per file: NO byte-lock (tests or gates) on any of the three files → the card's
option (i) — split via top-level helpers — is COMPLIANT for all three rows. Option (ii)
(BLOCKED-with-evidence) is NOT triggered.** The honest-stop clause stays armed only if a
run-time lock surfaces later (it would manifest as an unexpected family failure; §6 lists
every family that could carry one).

## 5. Promotion contracts READ (binding pins; evidence files the batteries come from)

| evidence file (read this attempt) | sha256 | what it defines |
|---|---|---|
| `execution_runs/PROMOTION-PREP/a20260922-01/promotion_batch_manifest.md` | `6759d1eb…073aac` | B-1..B-6 per-cell before/after promotion hashes (incl. all three of my files) |
| `execution_runs/PROMOTION-EXEC/a20260922-01/oracle.md` | pinned in binding | B-1 verification = **I-08-C 13-node suite** `test_i08c_consumer_rejection.py` (13152 B / `3f83fdf2…`) with `RF_IMPORT_ROOT`; B-6c verification = **5-file model battery** (named §6 F3) |
| `execution_runs/PROMOTION-EXEC/a20260922-01/decision.md` | pinned | per-row outcomes, RUN-A/RUN-B frozen facts (13/13 vs {e11,e13} red), B-6c STOP→revert history |
| `execution_runs/MODEL-ORACLE-ALIGN/a20260922-01/commands.json` + `decision.md` | pinned | 5-file battery exact definition + expected **59 passed / 202 subtests / rc 0**; I-08-C 13/13 under full promotion; **verify_i10b.py after → 7/7**; interpreter/flags contract |
| `execution_runs/B1-I08C-product-fixes/a20260921-01/runner/regression_targets.txt` | pinned | **B1 (attestation/publication) promotion battery — 11 test files** (attestation, publication pipeline/registry, draft/formal, txn, output report, recognition bridge, validate-only gate, fc905b, schema SOT) |
| `REMEDIATION_REGISTER.md` | pinned | PROMOTION/GATE-OQ sections §30–§37 + line 1073 (`5fd82de7` incl. `model_registry.py=62f864b9`) — promotion-contract narrative |
| `execution_runs/I-08-C/a20260919-01/test_i08c_consumer_rejection.py` | `3f83fdf2…54fbb` (13152 B) | the 13-node suite file itself (self-isolating registry fixture; `RF_IMPORT_ROOT` override documented in its header) |

## 6. Test-family inventory (frozen; each family runs BEFORE on pristine bytes and AFTER on refactored bytes, identical commands)

| id | family (exact file set) | expected BEFORE | expected AFTER | source of expectation |
|----|--------------------------|-----------------|----------------|-----------------------|
| F0 | `tools/tests/test_complexity_ratchet.py` (both tests) | 2 failed (F1 abort + N1 abort, msgs exactly as §2) | **identical 2 failed, same first-abort messages** (my rows are behind the sibling rows; KEEP-RED-scoped) | first-abort semantics §1; sibling FIX oracle §4 precedent |
| F0m | full-row scan (import-based + inlined) over an iso tree of THIS card's refactored bytes | n/a (before = §3 table) | **my 3 rows ≤ caps; sibling rows unchanged (F1/F2/F3/F5/N1 byte-identical files → same numbers)** | §3 |
| F0d | derived 3-key diagnostic: the REAL test module's loop/`_max_complexity` with `FROZEN_MAX` filtered to my 3 keys, run against refactored bytes (labeled DERIVED, test file untouched) | n/a | passes all 3 sorted keys | derived harness, disclosed |
| F1 | **B1 promotion battery** = the 11 files in `B1-I08C-product-fixes/…/runner/regression_targets.txt` (test_attestation, test_publication_pipeline, test_publication_registry, test_zr701_f1_draft_formal, test_zr705_draft_formal_swap, test_zr710_publication_txn, test_output_report, test_recognition_bridge, test_zr704_validate_only_gate, test_fc905b_trusted_receipt, test_zr702_schema_source_of_truth) | all pass / rc 0 | **identical counts / rc 0** | B1 card runner; promotion payload = production bytes |
| F2 | **I-08-C 13-node**: `execution_runs/I-08-C/a20260919-01/test_i08c_consumer_rejection.py`, `RF_IMPORT_ROOT` = tree under test | 13 passed / rc 0 | **13 passed / rc 0** | PROMOTION-EXEC oracle B-1 RUN-A fact + MODEL-ORACLE-ALIGN `06_production_i08c13` |
| F3 | **5-file model battery**: `tests/test_model_{registry_contract,economic_guardrails,extensions,extensions_anchor,integration_bounds}.py` | 59 passed / 202 subtests / rc 0 | **59 passed / 202 subtests / rc 0** | MODEL-ORACLE-ALIGN commands.json (`05_production_battery`) |
| F4 | **I-10-B verify**: mirrored `verify_i10b.py after` over `<attempt>/iso/rf/scripts` (mirror layout per MODEL-ORACLE-ALIGN NR-3 boundary) | 7/7 / rc 0 | **7/7 / rc 0** | MODEL-ORACLE-ALIGN `07_i10b_verify_after` |
| F5 | `tests/test_golden_behavior_lock.py` (5 pinned result hashes) | pass | **pass, `golden_behavior_hashes.json` untouched** | behavior lock = zero-behavior primary proof |
| F6 | content-needle/structure: `tests/test_skill_documentation.py`, `tests/test_structure_targets.py`, `tests/test_input_construction_consistency.py` | pass | **pass** | needles §4.2 |
| F7 | `tests/test_models.py` | pass | **pass** | direct `calculate_model_path`/MODEL_SPECS consumer |
| F8 | adversarial direct importers: `tests/adversarial/test_anchor_attacks.py`, `tests/adversarial/test_receipt_attacks.py` | pass | **pass** | direct `revenue_publication` imports |
| F9 | `tests/test_backtest.py` (direct `revenue_publication` importer; ALSO in sibling FIX's family — overlap disclosed, read-only run, no file conflict) | pass | **pass** | grep §4.3 |

Inventory derivation evidence: grep of `from revenue_core import|revenue_publication|import
model_registry` over `tests/` (55 matches) reduced to (a) promotion-card batteries and
(b) direct importers/needle readers of exactly my three files; full-run suite beyond this
bounded union is the parent's push-gate obligation (same NR-2 posture as MODEL-ORACLE-ALIGN).

## 7. Zero-behavior-change contract + mutation non-vacuity + revert-probe (frozen methods)

Refactor = extract TOP-LEVEL module helpers; statements moved VERBATIM; identical outputs,
exceptions (same types + same message strings in the same check ORDER), side effects,
evaluation order; no signature changes, no new `global` statements (the two existing
`_ATTESTATION_LAST_FAILURE = None` dead-store assignments stay local exactly as today);
public names/`__all__` (revenue_core) untouched; needles §4 preserved.

Mutation non-vacuity (per file, on scratch copies of the REFACTORED bytes, never on delivery
copies): inject one redundant decision into that file's then-max top-level function so its
measured CC exceeds the frozen cap → full-row scan shows that row FAIL with the new number →
restore → row ok again. Exact injections + measured numbers recorded in decision.md
(expected shape: +2 CC per injected BoolOp clause). Counts: 3 mutations RED + 3 restores GREEN.

Revert-not-refactor probe (card: "test it, don't assume"): overlay the promotion
BEFORE-images (`PROMOTION-EXEC/recovery/before_images/B-1/{revenue_core,revenue_publication}.py`
= pre-promotion `1821fd2a…`/`183803bb…`; `MODEL-ORACLE-ALIGN/recovery/before_images/
registry_repromotion/model_registry.py` = `9ec65295…`) onto a pristine iso copy → run F2/F1/F3/F4
→ record the actual outcomes. The pre-promotion bytes ARE the promotion's before-state, so a
RED there proves revert-not-refactor would break the promotion contract (recorded sha256 of
each overlay byte-source in decision.md). If a probe unexpectedly passed GREEN for a file,
that row's revert option would be re-opened and DISCLOSED — results are whatever the runs say.

Environment: `C:\Miniconda\python.exe` 3.13.9 / pytest 9.1.1 (matches every promotion run);
all pytest: `-X utf8 -B -m pytest -p no:cacheprovider -q --no-header` + `--basetemp` under
`%TEMP%\rf-rest-b\basetemp*` + `PYTHONDONTWRITEBYTECODE=1` + `PYTHONPATH=<tree>\scripts;<tree>\tests`;
`REVENUE_PUBLICATION_REGISTRY` isolated by `tests/conftest.py` fixture and by I-08-C's own
fixture — no registry writes to production. Runnable iso trees live in `%TEMP%\rf-rest-b\`;
sources under `scripts/` are READ-ONLY for this card; pinned refactored copies +
`changes.diff` land in this attempt dir; git used READ-ONLY only (`status`, `log`, `show`);
zero git writes.

## 8. Invariants (checked before AND after; any breach = STOP)

1. `tools/tests/test_complexity_ratchet.py` sha256 before == after
   (`eb1a36cfd54a8b96e3b5dca6ca4b7a89ca6b1e1605d22eedb69f643245edd10a`); `FROZEN_MAX` /
   `NEW_FILE_MAX` literal block sha before == after (`1e9cce36…89074`).
2. `changes.diff` touched set == exactly `scripts/model_registry.py`, `scripts/revenue_core.py`,
   `scripts/revenue_publication.py` (3 sections, `a/`+`b/` headers).
3. Production writes by this card = none (porcelain before == after, attempt dir excluded;
   all runnable work in `%TEMP%`).
4. Family results BEFORE == AFTER for every family F1–F9 (F0 stays the same 2-failed
   KEEP-RED-scoped outcome with identical first-abort messages).
5. Full-row scan after: my 3 rows ≤ frozen (9/6/10); the other 5 rows byte-identical files →
   same numbers as §3 (drift would mean a sibling/outsider touched them → STOP).
6. Zero skip/xfail/baseline/marker additions in this attempt's diff.
7. Every top-level function of my three refactored files ≤ its file cap (not just the max).
8. Golden behavior hashes unchanged; `golden_behavior_hashes.json` untouched.
9. Promotion batteries F2/F3/F4 run in BOTH directions with the frozen expected counts;
   their evidence files' pins (§5) re-verified at binding time.

## 9. Pre-freeze disclosures (nothing here is a judged run)

- Reads: full text of the three target files, the ratchet test, REMEDIATION_REGISTER
  PROMOTION/GATE-OQ sections, PROMOTION-{PREP,EXEC} + MODEL-ORACLE-ALIGN carriers (oracle/
  decision/commands/manifest), B1 runner battery list, I-08-C suite file header, sibling
  RF-RATCHET-FIX oracle + binding (for protocol parity), `tests/conftest.py`,
  `verify_i10b.py`, needle tests, `audit_baseline.py`/`release_gate.py`/`fc1307a` (hash-call
  triage).
- Git reads only: `show -s`/`show --stat`/`log -1 -- <file>` for `ec307d20` and `5fd82de7`
  (attribution §2), `status --porcelain` (baseline captured in
  `evidence/integrity/porcelain_baseline.txt` — pre-existing dirty: REMEDIATION_REGISTER.md
  ` M` + pre-existing untracked planning/tmp entries; `scripts/`, `tests/`, `tools/` clean).
- Measurements before freeze: full-row scan ×2 implementations, per-function CC tables,
  byte-lock scan, 40 binding pins — all raw outputs saved under `evidence/measure/`,
  `evidence/bytelock/`, `scratch/binding_pins_raw.*`.
- Attempt dirs created (`evidence/*`, `refactored/`, `recovery/before_images/`, `scratch/`)
  and `%TEMP%\rf-rest-b\{iso_after,iso_revert,basetemp,pycache}` — no product/test file
  written anywhere.
- After this freeze the sequence runs: binding → commands (verbatim RED attempt + judged RED
  re-run) → iso build → refactor → GREEN families + scan → mutations → revert-probe →
  changes.diff → decision → handoff → evidence → recovery. The judged RED must match §2/§3.
