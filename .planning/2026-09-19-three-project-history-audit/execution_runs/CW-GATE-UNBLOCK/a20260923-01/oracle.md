# ORACLE (frozen FIRST — before any repro, pin, measurement, or fix)

Card: **CW-GATE-UNBLOCK** · Attempt: `a20260923-01` · CW = `C:\Users\郑曾波\Projects\company-wiki`
(fcap ahead3 vs origin/master: ac4ebd0, 5d72529, bf0c8b2 — parent live-verified both root causes
below before dispatch; this file restates them as falsifiable expectations, frozen pre-execution).

CI root-fix protocol: root cause only, NO bypass, NO baseline/frozen-cap raise.

---

## RC-1 — Gate tool encoding crash (`tools/pre_push_gate.py`)

- **Claimed root cause (live-verified by parent, to be reproduced by this attempt):**
  `_run()` does `tail = (proc.stdout)[-2000:] + (proc.stderr)[-1000:]` then `print(tail)`
  (observed at `tools/pre_push_gate.py:54`, triggered by the FC-1204 ratchet step's output).
  On a GBK stdout (Windows console, cp936), `print(tail)` raises
  `UnicodeEncodeError: 'gbk' codec can't encode '\u05a3'` when the child step's output
  contains characters outside GBK — the gate crashes instead of reporting the step result.
- **RED spec (must observe on the CURRENT, unmodified gate file):**
  tiny repro that (a) imports the gate module, (b) forces stdout encoding to `gbk`
  (simulating the Windows console), then (c) invokes the SAME print path —
  `pre_push_gate._run(...)` with a synthetic child whose stderr contains `'\u05a3'`
  and whose exit code is non-zero (e.g. 3) → must CRASH with `UnicodeEncodeError`
  ('gbk' codec can't encode …) → repro exits abnormally (≠ child rc), payload not printed.
- **GREEN spec (same repro against the FIXED gate file):**
  repro prints the payload (encoding-safe, `errors='replace'` acceptable) AND exits with
  the child's rc — **rc semantics preserved: a step-failure rc must still propagate**
  (repro exit code == child exit code == 3). No step semantics, labels, order, or
  gate list changed — fix is output-printing/encoding safety only, tool-side.
- **Fix shape (allowed):** encoding-safe output — e.g.
  `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` early / at the print site,
  or a safe writer. NOTHING else in the gate may change.
- **Non-regression check:** any CW test referencing `pre_push_gate` (grep) must stay green.

## RC-2 — CW complexity ratchet RED (real, pre-existing since ac4ebd0)

- **Claimed root cause (live-verified by parent, to be reproduced):**
  `tests/contract/test_fc1204_complexity_ratchet.py::test_complexity_ratchet_frozen_files_do_not_worsen`
  fails with `archive_retired_evidence.py max complexity 19 exceeds frozen 7`
  (file: `src/company_wiki/source_catalog/archive_retired_evidence.py`, frozen entry
  `"archive_retired_evidence.py": 7`).
- **RED spec (CURRENT file):** run that exact test → FAIL, assertion message contains
  `max complexity 19 exceeds frozen 7`. Per-function McCabe (the test's own AST counting:
  1 + decision points; If/For/While/And/Or/ExceptHandler/comprehension/Assert/With = +1,
  BoolOp = +1 and +(n-1)) must be measured and recorded BEFORE the fix; expected max = 19
  in top-level `archive_retired_evidence()` (to be measured, not trusted).
- **GREEN spec (refactored file):**
  1. `test_complexity_ratchet_frozen_files_do_not_worsen` PASSES — every top-level function
     in the file ≤ 7 (max complexity ≤ 7), via deliberate function splits (pure code motion
     into helpers), **ZERO behavior change**: same outputs/return values/exceptions
     (type+message)/side-effect order (temp→fsync→verify→publish→manifest)/cleanup semantics.
  2. The file's OWN existing test family passes with no regression: every test under
     `tests/` referencing `archive_retired_evidence` — at minimum
     `tests/contract/test_source_catalog_archive_retired.py`, plus the ratchet tests that
     name the file (`test_fc1204_complexity_ratchet.py`, and
     `test_fc1204_coverage_ratchet.py` since it carries a coverage floor for this file).
  3. **Frozen table rule:** NO frozen value may increase. The card's reading to be
     documented in decision.md: table update is only ever sanctioned DOWNWARD (re-record
     after a deliberate split); an update is REQUIRED only if the refactored max would
     otherwise exceed... — never; if new max ≤ frozen 7 the test passes with the table
     untouched. Re-recording a lower value is permitted (sanctioned direction) but must
     not be needed for GREEN; raising 7 is forbidden under all circumstances.
     (Frozen decision: expect NO table change to be required; if measurement shows new
     max ≤ 7, table stays as-is and decision.md records this reading explicitly.)
- **MUTATION spec (non-vacuous proof):** revert/merge ONE split in the refactored file —
  restore the hot write-loop path (inline `_write_rows` back into
  `archive_retired_evidence()`) → that function's complexity must jump above 7 →
  the ratchet test must turn RED again with `max complexity N exceeds frozen 7` (N ≥ 8).
  Then restore the fixed file → GREEN again. (Full-file revert to the original 19-complexity
  version serves as an additional mutation check if the single-split merge is ambiguous.)

## RC-3 — Discover the COMPLETE gate step set and every blocker

- Step list must be read from `tools/pre_push_gate.py` COMPLETELY (default invocation,
  i.e. WITHOUT `--skip-contract`). Extracted expected step list (frozen here from the
  source read; verify against binding pins):
  1. `ruff check src tests/unit tests/contract scripts`  (label: ruff CI WU-1.2 full scope)
  2. `<py> -m compileall -q src scripts tests`           (label: compileall)
  3. `<py> scripts/config_doctor.py`                     (label: config_doctor CI WU-7.1)
  4. `<py> -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q`
     (label: FC-1204 complexity ratchet — CI meta-gate)
  5. `<py> scripts/host_assumption_guard.py`             (label: host assumption guard FC-1307-a)
  6. `<py> -m pytest -q --timeout=180` + the six files:
     test_source_catalog_section_extractor, test_fc906a_producer_binding_metadata,
     test_legacy_observation, test_zr506_section_chunk_fact,
     tests/unit/test_writer_freeze, test_fc1307_host_assumption_gate
     (label: contract tests + meta gates)
  Gate stops at FIRST red; exit code = failing step's rc; all steps run in an iso copy of
  the CW working tree (post both fixes) so the parent gets the FULL blocker set.
- **Expected statuses (hypothesis frozen pre-run):** step4 RED before fix / OK after fix
  (RC-2); all other steps expected OK — UNVERIFIED. Any step besides step4 failing =
  newly discovered blocker → fix root cause in-card if a genuine in-scope defect
  (code/test fix, no bypass, no baseline additions); if out-of-scope (e.g. frozen-cap
  raise) → STOP that item, report BLOCKED-with-evidence, do NOT bypass.
- RC-1's fix must be in place for the step-run so a failing step's non-GBK output cannot
  crash the gate tool mid-run (rc of failing step must propagate).

## Change-file allowlist (changes.diff may contain ONLY)

1. `tools/pre_push_gate.py` (RC-1)
2. `src/company_wiki/source_catalog/archive_retired_evidence.py` (RC-2)
3. `[+ any genuinely-required in-scope fix with its own justification] — expect none
   unless a discovered blocker proves in-scope.

## Hard constraints

- CW production tree writes = ZERO (read-only source; all edits in iso copies under
  %TEMP%; changes.diff is the only vehicle out).
- RF/FF untouched; no network; no git mutations (read-only git for pins/verification in
  scratch only); %TEMP% scratch.
- Report must include: two root causes fixed w/ before/after shas, per-function CC
  before/after table, FULL gate step status table (every step), red/green/mutation
  counts, change-file list.
