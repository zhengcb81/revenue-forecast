# decision.md — RF-RATCHET-REST-B a20260923-01 (LIVING DOCUMENT — incremental)

Status: IN PROGRESS (delivery-first per parent directive 2026-09-23: living docs landed
within the first hour; every run's evidence appended as it completes; one file's
RED→GREEN→mutation finishes before the next file starts; a death-at-dump must leave this
attempt self-consistent).

Authority: card RF-RATCHET-REST-B (fix3 of the 8 masked complexity-ratchet violations —
the three introduced by owner-authorized promotions `ec307d20` + `5fd82de7`); parent ruling
refactor-DOWN only, no frozen-cap change; byte-lock pre-check first with honest-stop clause.

## A. Completed milestones (append-only)

### A0. Oracle frozen FIRST (deliverable)
- `oracle.md` sha256 `98dcb0a8fdd05b81fb437b1ce750d359da3d29f2f93648598ca95e580c606f4d`
  (20053 B), frozen 2026-09-23T20:16:08Z before any judged run.
- Contains: 3 rows + measured numbers, 8-row full-scan table, family inventory F0–F9 with
  frozen expectations, byte-lock pre-check findings + verdict, promotion-contract evidence
  files read, invariants, pre-freeze disclosures.

### A1. Byte-lock pre-check (oracle §4, evidence written)
- `evidence/bytelock/bytelock_scan_before.txt`: sha-literal hits over tests/+tools/ for the
  three files = **0**; 15 name-references (3 assertion needles enumerated); 138 hashing-call
  lines all artifact/guard/config-level, none over the three files.
- Live production hashes == promotion payload pins (62f864b9/8a761498/bc2bb4a3).
- **Verdict: no byte-lock → helper-split path (card option i) compliant for all three rows;
  option (ii) STOP not triggered.**

### A2. Binding (deliverable)
- `binding_before.json` (11431 B): 40 pins (3 targets + ratchet test + 26 family/battery
  test files + SKILL.md + golden hashes + promotion-contract carriers), frozen-table block
  sha (explicit extraction rule `78c06a87…`; sibling FIX's `1e9cce36…` used a different
  undocumented rule — both anchor the same full test-file sha `eb1a36cf…` = authoritative),
  three-row before-numbers, pre-freeze evidence shas, byte-lock verdict, disclosed git reads.

### A3. Commands step — RED captured (evidence written immediately)
- Verbatim-style command `python -m pytest tools/tests/test_complexity_ratchet.py -q
  --basetemp … -B` → **rc 4, "unrecognized arguments: -B"** (interpreter-flag quirk,
  disclosed exactly as sibling FIX) → `evidence/red/ratchet_red_verbatim.txt`.
- Judged form `python -X utf8 -B -m pytest tools/tests/test_complexity_ratchet.py -q
  -p no:cacheprovider --basetemp …` → **rc 1, 2 failed** with first-abort messages
  `analysis/confidence.py max 32 > 23` (sibling FIX row) + `model_extensions.py max 27 > 10`
  (sibling FIX row) → `evidence/red/ratchet_red_judged.txt`. Matches oracle §2 exactly.
- Full-row RED for MY rows (masked behind F1/F2/F5 in the real test by first-abort
  iteration): `evidence/measure/scan_all_violations_before.txt` (import-based) +
  `independent_crosscheck_before.txt` (inlined re-implementation, identical output:
  7 frozen + 1 new violations; my rows 28>9 / 23>6 / 16>10) + `measure_cc_before.txt`
  (per-function tables; revenue_core has TWO functions over cap: 23 + 19).

### A4. Before family runs (COMPLETED 2026-09-23, evidence `evidence/families_before/*_stdout.txt` + `summary.json`; runner `scratch/run_families.py`; production tree, read-only)

| family | rc | result (BEFORE, pristine production bytes) |
|--------|----|--------------------------------------------|
| F0 ratchet | 1 | **2 failed** — exactly the oracle §2 first-abort messages (confidence 32>23, model_extensions 27>10), sibling rows |
| F1 B1 promotion battery (11 files) | 1 | **1 failed, 99 passed** — `test_attestation.py::test_configured_provider_means_host_signed_publication` (see pre-existing note) |
| F2 I-08-C 13-node | 0 | **13 passed** ✓ frozen expectation |
| F3 model 5-file battery | 0 | **59 passed, 202 subtests** ✓ frozen expectation |
| F5 golden behavior lock | 0 | **1 passed** ✓ |
| F6 needles (3 files) | 0 | 9 passed, 18 subtests ✓ |
| F7 models | 0 | 9 passed, 31 subtests ✓ |
| F8 adversarial (2 files) | 1 | **1 failed, 5 passed** — `test_receipt_attacks::test_context_fabrication_is_rejected_by_final_validation` (see pre-existing note) |
| F9 backtest | 0 | 17 passed ✓ |

(F4 verify_i10b runs separately against the mirror layout; pending.)

**Oracle-expectation deviation, DISCLOSED (honesty over silence):** oracle §6 froze F1/F8
expectation as "all pass/rc 0" (inferred from promotion-time GREEN). The measured BEFORE
baseline shows the two failures above. Corroboration that BOTH are pre-existing at HEAD and
NOT caused by this card (independent runs by the parent's RF-STEP9-TRIAGE card, byte-copied
into `evidence/families_before/external_corroboration/`):
- `win_head_tests_test_attestation_py.out` — same test, same assertion, `1 failed, 6 passed`,
  PYTEST_RC=1 on production HEAD;
- `win_head_tests_adversarial_test_receipt_attacks_py.out` — same test, same E27
  `ForecastInputError: attestation_missing_record … requires a publication_attestation
  record (E27)` raised inside `build_publication_receipt`, `1 failed, 2 passed`, RC=1 at HEAD;
- `wsl_atEc3_*` twins show the same two outcomes under WSL (cross-platform determinism).
Diagnosis: (1) `attestation_capability()` with `REVENUE_ATTESTATION_PROVIDER=sys.executable`
cannot complete the REM-01 signing handshake on this host (spawned interpreter produces no
protocol response / no trusted signer configured) — the I-08-C 13-node suite's own e1 test
documents this exact post-B1 behavior and asserts the honest `unattested` label instead
(F2 green); (2) `test_context_fabrication` predates this card and fails at the promotion's
build-time E27 fail-closed check — the test is not in any promotion battery (B1
`regression_targets.txt` excludes `tests/adversarial/`). **Both stay untouched (zero-behavior
rule); the governing invariant for F1/F8 is BEFORE == AFTER with identical pass/fail sets
and counts. Routing: these two pre-existing REDs are NOT this card's rows — flagged to parent
in the final report for sibling/parent disposition.**

### A5. Per-file refactor + scan + mutation (one file at a time)

#### File 2/3 — scripts/revenue_publication.py: **16 → 5 (cap 10) GREEN**
- Method: `validate_publication_attestation` split into 4 top-level check-group helpers
  (`_require_attestation_field_set` 3, `_require_attestation_identity_fields` 4,
  `_require_attestation_hex_fields` 5, `_require_attestation_signature_fields` 5) + thin
  main 3; every `require()` message string and the check ORDER (field set → schema/domain/
  algorithm → issuer/key → fingerprint → request_id → signed_at → signature → payload
  binding → rebuild request → verify) preserved; the E27 `record is None` branch and the
  binding/verify tail stay in the main function. Script: `scratch/refactor_revenue_publication.py`.
- CC table AFTER: `evidence/green/measure_cc_revenue_publication_after.txt` (FILE_MAX=5).
- Literal parity after docstring restore: **missing=0**, added=4 (the four NEW helper
  docstrings, enumerated in `evidence/green/literal_diff_all3.txt`).
- Mutation: `or False` appended to the fingerprint condition in the scratch tree →
  row **FAIL actual=11 > 10** (`evidence/mutation/mut2_revenue_publication_scan_red.txt`);
  restore → **ok actual=5** (`mut2_..._restored_scan_green.txt`). 1 RED + 1 GREEN.

#### File 3/3 — scripts/revenue_core.py: **23 → 6 (cap 6) GREEN** (split attestation functions)
- Method: PROGRAMMATIC SLICING (`scratch/refactor_revenue_core.py`) — every condition,
  comment and message string CUT from the promotion payload text at anchors asserted
  unique, never retyped. `_run_attestation_provider` (19) → resolve/spawn/exit-classify/
  output-parse helpers + thin main; `_validate_attestation_response` (23) → six check
  helpers (field set 5, echo 4, signer 6, fingerprint 4, signature 5, signed_at 4) + thin
  main 1. One nested block needed mechanical 4-space dedent (`_record_provider_exit_failure`,
  CC 6) — disclosed in commands.json; messages byte-untouched (proved by literal parity).
  Per-helper LOCAL imports of `PUBLICATION_ATTESTATION_*` + `verify_ed25519_signature`
  replace the single function-local import block (the revenue_core↔revenue_publication
  import cycle forbids module-level imports; reshape disclosed).
  The two `_ATTESTATION_LAST_FAILURE = None` dead-store assignments remain LOCAL exactly
  as in the payload (no `global` introduced anywhere).
- CC table AFTER: `evidence/green/measure_cc_revenue_core_after.txt` —
  FILE_MAX=6; every top-level fn ≤6 (four at exactly 6).
- **Literal parity: 283 → 283, missing=0, added=0** (perfect; `evidence/green/literal_diff_all3.txt`).
- Mutation: `or False` on the algorithm condition (parse-guarded) → row
  **FAIL actual=8 > 6** (`evidence/mutation/mut3_revenue_core_scan_red.txt`);
  restore → **ok actual=6** (`mut3_..._restored_scan_green.txt`).
  **Vacuous first attempt DISCLOSED**: appending after the colon produced a SyntaxError and
  the scan's `SyntaxError → 0` path fake-passed as `actual=0`; superseded by the parse-guarded
  attempt (`mut3_vacuous_first_attempt_note.txt`). Method lesson recorded: mutations must parse.

#### Cross-file prose/comment invariants (evidence `evidence/green/`)
- String-literal multiset diff (production vs iso): **LITERAL_PARITY — missing=0 on all
  three**; added = exactly 12 new-helper docstrings (8 registry + 4 publication),
  enumerated; revenue_core added=0.
- Comment multiset diff (tokenize COMMENT): **COMMENT_PARITY — 27/27, 37/37, 40/40,
  missing=0, added=0** (the retyped I-10-B comment block matched byte-exact).
- `py_compile` of all three: `PYCOMPILE_OK3`.
- Row scan after all three (`evidence/green/scan_after_all3.txt` + independent crosscheck):
  **model_registry ok 8≤9, revenue_core ok 6≤6, revenue_publication ok 5≤10**;
  remaining rows = sibling-owned F1 (32>23), F2 (22>21), F3 (17>9), F5 (114>88), N1 (27>10)
  — byte-identical files → numbers unchanged; totals 4 frozen + 1 new.

#### File 1/3 — scripts/model_registry.py: **28 → 8 (cap 9) GREEN** (recorded after files 2–3; delivery-first incremental log)
- Method: splice `calculate_registered_model` (CC28) into 10 top-level module helpers
  (`_resolve_model_spec` 2, `_validated_base_revenue` 2, `_validated_years` 8,
  `_validated_year_order` 3, `_validate_driver_sets` 3, `_driver_series` 6,
  `_normalized_driver` 3, `_normalized_drivers` 2, `_checked_model_path` 6,
  thin orchestrator `calculate_registered_model` 2); statements/conditions/messages moved
  verbatim; validation-stage ORDER identical (spec → base → years → year-order →
  Mapping → driver-sets → per-driver normalize → calculator → length/sign checks).
  Script: `scratch/refactor_model_registry.py` (splice anchored at
  `def calculate_registered_model(` to EOF; nothing else in the file touched).
- CC table AFTER: `evidence/green/measure_cc_model_registry_after.txt`
  (FILE_MAX=8; every top-level fn ≤8 — all under the frozen 9).
- Row scan AFTER file1: `evidence/green/scan_after_file1.txt` —
  `ok model_registry.py actual=8 frozen=9`; other rows unchanged (F1/F2/F3/F5/N1 files
  byte-identical → same numbers; totals 6 frozen + 1 new).
- Mutation non-vacuity (scratch tree `%TEMP%\rf-rest-b\mut_tree`, delivery bytes untouched):
  redundant `if True and (…)` into `_validated_years` → row flips
  **FAIL actual=10 > 9** (`evidence/mutation/mut1_model_registry_scan_red.txt`),
  restore → **ok actual=8** (`evidence/mutation/mut1_model_registry_restored_scan_green.txt`).
  1 RED + 1 GREEN.

### A6. After family runs + revert-probe + changes.diff (COMPLETED; evidence written per run)

- **F4 verify (I-10-B own verifier)**: BEFORE 7/7 rc0 (`evidence/families_before/F4_*`) →
  AFTER 7/7 rc0 on final bytes (`evidence/families_after/F4_i10b_stdout_final.txt`).
- **Families AFTER (final bytes incl. the two-annotation fix)**: per-family rc identical to
  BEFORE for all nine (F0=1, F1=1, F2=0, F3=0, F5=0, F6=0, F7=0, F8=1, F9=0); stdout
  identity after stripping volatile timing only — see §D.
- **Derived 3-key diagnostic (F0d)**: real-test loop over my 3 sorted keys →
  `ok 8≤9 / ok 6≤6 / ok 5≤10`, rc 0 (`evidence/green/derived_3key_after.txt`).
- **Revert-not-refactor probe**: run + verdict in §F.
- **changes.diff**: 23626 B, sha256 `bcca2498…6731e9`, exactly 3 sections;
  `refactored/` pins + `manifest.json` (before/after shas, hunk counts 2/9/2).
- **After-invariants**: frozen ratchet test sha before==after `eb1a36cf…`; frozen literal
  block sha before==after `78c06a87…`; production shas of all three files == promotion
  payloads (zero production writes); scoped porcelain check
  (`evidence/integrity/porcelain_scoped_check.txt`): 0 product-surface entries in baseline
  and after; the 46 new porcelain lines are concurrent parent/sibling planning activity
  (RF-STEP9-TRIAGE files, AUDIT-*/RF-RATCHET-FIX-2 dirs, OWNER_DECISIONS/RESPONSES ` M`),
  none under `scripts/ tests/ tools/ config/ e2e/`; my card added no line outside its
  attempt dir.
- **Type/lint gates**: mypy errors before=69 (== MYPY_BASELINE) → after=69, error sets
  IDENTICAL (an intermediate +1 `zip(years, object)` regression in `_normalized_driver` was
  caught by this comparison and fixed with two `list | tuple` annotations — runtime-inert
  under `from __future__ import annotations`; disclosure: annotations are the ONLY
  post-family-run byte change, and families were RE-RUN on the final bytes afterwards);
  ruff rc0 on the three final files (`evidence/green/{mypy_before,mypy_after,ruff_after}.txt`).

## B. Per-row CC before→after (final)

| row | file | before | after (final bytes) | verdict |
|-----|------|--------|---------------------|---------|
| F4 | scripts/model_registry.py | 28 (cap 9) | **8** (max helper `_validated_years`) | **GREEN ≤9** |
| F6 | scripts/revenue_core.py | 23 (cap 6) | **6** (four fns at exactly 6; both original violators split: `_validate_attestation_response` 23→1+helpers, `_run_attestation_provider` 19→6+helpers) | **GREEN ≤6** |
| F7 | scripts/revenue_publication.py | 16 (cap 10) | **5** | **GREEN ≤10** |

No BLOCKED-with-evidence rows: the byte-lock stop-clause never fired (§C, oracle §4).

## C. Byte-lock verdict per file (final — unchanged from oracle §4; no runtime lock surfaced in any family run)

| file | byte-lock in tests/gates? | verdict |
|------|---------------------------|---------|
| scripts/model_registry.py | NO (0 sha hits; needle `build_extension_specs` PRESERVED — F3's anchor test green both runs) | refactor COMPLIANT |
| scripts/revenue_core.py | NO (needles preserved: validate-before-sign text order [F6 green], ≤2500 lines [706→~760, green]) | refactor COMPLIANT |
| scripts/revenue_publication.py | NO (0 sha hits; no needle) | refactor COMPLIANT |

## D. Family results (before vs after) — FINAL

| family | BEFORE (production bytes) | AFTER (refactored final bytes) | identical? |
|--------|---------------------------|--------------------------------|------------|
| F0 ratchet (real test) | rc1, 2 failed: `analysis/confidence.py max 32 > 23` + `model_extensions.py max 27 > 10` | **same rc, same two messages, byte-identical stdout** | YES |
| F1 B1 promotion battery (11 files) | rc1: 1 failed, 99 passed (`test_attestation::configured_provider…`, PRE-EXISTING) | **same rc, same failed test, same counts, stdout identical** | YES |
| F2 I-08-C 13-node | rc0, 13 passed | **rc0, 13 passed** | YES |
| F3 model 5-file battery | rc0, 59 passed / 202 subtests | **rc0, 59 passed / 202 subtests** | YES |
| F4 verify_i10b after | rc0, 7/7 | **rc0, 7/7** | YES |
| F5 golden behavior lock | rc0, 1 passed (5 pinned result hashes) | **rc0, 1 passed** | YES |
| F6 needles | rc0, 9 passed / 18 subtests | **rc0, 9+18** | YES |
| F7 models | rc0, 9 passed / 31 subtests | **rc0, 9+31** | YES |
| F8 adversarial | rc1: 1 failed, 5 passed (`test_receipt_attacks::context_fabrication…`, PRE-EXISTING) | **same rc, same failed test, same counts**; stdout identical after normalizing timings AND traceback source line refs (`revenue_publication.py:396 → 416` — the only line shift; helpers inserted above) | YES |
| F9 backtest | rc0, 17 passed | **rc0, 17 passed** | YES |

Machine comparison: `evidence/families_before_after_identity.txt` (+ the F8 line-ref
normalization check recorded in commands.json). Oracle §6's "all pass" expectation for
F1/F8 was disproven by the measured BEFORE baseline and DISCLOSED in §A4 with independent
RF-STEP9-TRIAGE corroboration; the governing invariant (identical results both directions)
holds for every family.

## E. Mutation non-vacuity per file (summary; scratch trees only, delivery bytes untouched)

| file | injection | scan result | restore |
|------|-----------|-------------|---------|
| model_registry | `True and (…)` into `_validated_years` | **FAIL 10 > 9** | ok 8 (GREEN) |
| revenue_publication | `or False` on fingerprint condition | **FAIL 11 > 10** | ok 5 (GREEN) |
| revenue_core | `or False` on algorithm condition (parse-guarded) | **FAIL 8 > 6** | ok 6 (GREEN) |

3 RED + 3 GREEN. First revenue_core attempt was VACUOUS (mutation after the colon →
SyntaxError → scanner's `SyntaxError→0` fake-passed `actual=0`); disclosed with a method
lesson and superseded by the parse-guarded attempt (`evidence/mutation/mut3_*`,
`mut3_vacuous_first_attempt_note.txt`).

## F. Revert-not-refactor probe (tested, not assumed)

Method: `iso_revert` = pristine production tree + pre-promotion BEFORE-images of exactly my
three files (overlay shas verified live == promotion before-images `1821fd2a…` / `183803bb…`
/ `9ec65295…`); ran F1/F2/F3/F7 + F4 against it.

| check | revert tree | current bytes | meaning |
|-------|-------------|---------------|---------|
| F2 13-node (promotion's own B-1 verification) | **rc1: test_e11 FAILED, 12 passed** | rc0: 13/13 | revert breaks the owner-approved re-freeze suite |
| F4 verify_i10b `after` | **rc3: 5/7 — R-B1-N1 (omitted optional must raise) + R-B2-N1 (sign-role) FAILED** | rc0: 7/7 | revert resurrects I-10-B defect-1/defect-2 behavior — the exact semantics the promotion delivered |
| F1 B1 battery | rc0: 100 passed (extra pass vs baseline = the RETIRED file-existence capability REM-01(b) killed) | rc1: 99+1 pre-existing fail | revert changes observable attestation behavior |
| F3 model battery / F7 models | rc0 green | rc0 green | aligned caller-side tests pass on both — not dispositive (disclosed) |

**VERDICT: revert-not-refactor DISPROVEN for revenue_core + revenue_publication (F2 RED)
and for model_registry (F4 RED). The pre-promotion bytes are the promotion's BEFORE-state;
landing them would break the promotion contract and restore retired insecure semantics.
Refactor was the only compliant path (as the card anticipated).**

## G. Honest routing

- **This card's three rows: GREEN** (28→8≤9, 23→6≤6, 16→5≤10), zero behavior change
  (identical families both directions + golden lock + literal/comment parity + mypy/ruff
  parity), delivered as `changes.diff` = exactly `scripts/{model_registry,revenue_core,
  revenue_publication}.py`.
- **Remaining masked rows are NOT this card's**: F1 `analysis/confidence.py` (32>23) and
  N1 `model_extensions.py` (27>10) → sibling **RF-RATCHET-FIX**; F2 `forecast/calc.py`
  (22>21), F3 `generate_input_template.py` (17>9), F5 `research/targets.py` (114>88) →
  sibling **RF-RATCHET-REST-A**. Their files were never written here; every scan shows
  their numbers byte-stable. Until all five land, the real ratchet test stays KEEP-RED on
  their rows (first-abort) — that is honest layering, not an attempt failure.
- **Two pre-existing HEAD REDs flagged for parent disposition (not mine, not touched)**:
  `tests/test_attestation.py::test_configured_provider_means_host_signed_publication`
  (stale vs REM-01(b) handshake semantics; fails at production HEAD per RF-STEP9-TRIAGE
  win_head + wsl evidence copied in `evidence/families_before/external_corroboration/`)
  and `tests/adversarial/test_receipt_attacks.py::test_context_fabrication_is_rejected_by_final_validation`
  (predates/parallels promotion E27 build-time fail-closed; same corroboration). Governing
  invariant here: identical BEFORE==AFTER.
- Handoff status: `review_pending`, unsigned; delivery acceptance `unproven`; dispatch
  `unmapped` (this card does not self-sign).

## F-1 erratum (landing)

LAND-TIME CORRECTION — 2026-09-23, carrier-landing pass, per reviewer finding F-1
(`reviewer_report.md` L200–L212, MEDIUM, evidence-integrity; delivery unaffected).
§E's original text above is RETAINED unchanged (erratum style); this note corrects
§E's revenue_core red→restore PAIRING only:

- The revenue_core `or False` mutation was NOT restored in the disposable scratch
  `mut_tree`: the reviewer's live scan of `%TEMP%\rf-rest-b\mut_tree` at check time
  still reports `FAIL revenue_core.py actual=8 > 6` (mutated file mtime 22:12:05) —
  the scratch was left mutated.
- The green raw cited in §E, `evidence/mutation/mut3_revenue_core_restored_scan_green.txt`
  (mtime 22:11:20), belongs to the EARLIER vacuous-attempt cycle, not the
  parse-guarded attempt: it PREDATES the cited red
  `mut3_revenue_core_scan_red.txt` (mtime 22:12:13), so §E's pairing of the two as
  one red→restore cycle is a chronology error.
- Correct red→restore pair for the successful (parse-guarded) cycle: RED =
  `mut3_revenue_core_scan_red.txt` @22:12:13 (`FAIL actual=8 > 6`); RESTORE =
  evidenced by the `refactored/` final bytes (`scripts/revenue_core.py` 23→6,
  `ok actual=6 ≤ 6`), confirmed by two independent implementations
  (`scratch/scan_all_violations.py` + `evidence/measure/independent_crosscheck.py`)
  and two independent family batteries (the card's BEFORE/AFTER pair and the
  reviewer's own re-run). A post-attempt-2 restore raw inside `mut_tree` was never
  captured.
- DELIVERY BYTES UNAFFECTED: neither `refactored/scripts/revenue_core.py` nor
  `changes.diff` ever contained the mutation; `mut_tree` is declared disposable in
  `recovery/README.md` (§ Scratch trees (disposable)), so its post-hoc state carries
  no evidentiary weight.
- No code rework (F-1's required action = this land-time correction).
