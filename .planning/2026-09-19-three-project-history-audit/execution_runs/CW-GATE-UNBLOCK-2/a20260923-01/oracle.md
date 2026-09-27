# ORACLE — CONTINUATION (frozen FIRST in this attempt, before any new judged run)

Card: **CW-GATE-UNBLOCK-2** (SUCCESSOR of `CW-GATE-UNBLOCK/a20260923-01`) ·
Attempt: `a20260923-01` · CW = `C:\Users\郑曾波\Projects\company-wiki` (sources READ-ONLY;
delivery via `changes.diff` only).

Predecessor attempt dir (READ-ONLY, preserved untouched, cited never written):
`C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\CW-GATE-UNBLOCK\a20260923-01`
— its frozen `oracle.md` sha256 =
`017C41BD58D071667F6FFA817441A14D13E59761332D373563A4B68D2CB05C39` (frozen 2026-09-23).

Predecessor death disclosure: died mid-work of a **subagent infrastructure failure, NOT a
process violation**. At death: RC-1 gate fix DONE, archive split DONE, observability →6
DONE, prompt_injection →15 DONE (all in its iso, families unchanged); prune refactor
PARTIAL (main still 17>12; its half-written PR4 batch-loop extraction left F821 undefined
names `absent` (line 605) / `deleted` (line 630) — diagnosed from its
`24-ruff-three.log` + `24-CC-prune-AFTER.log` + `20-ratchet-ALL-violations-GREEN.log`).

---

## §0 — BASE: predecessor's frozen oracle text, VERBATIM (sha cited above)

```
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
```

---

## APPEND A — CONTINUATION PLAN (dated 2026-09-23, frozen BEFORE any new judged run of this attempt)

Successor mandate = COMPLETE the FULL successor mandate with all prior authorizations
(the §0 base oracle is superseded only where APPEND A explicitly extends it; RC-2 scope
grew from 1 row to the 4-row same-table family via the interim same-table
auto-authorization; frozen table row values below are MEASURED from the pinned table).

### A.0 Frozen invariants (sha before == sha after, checked at close)

| invariant | value (sha256) |
|---|---|
| frozen complexity table `tests/contract/test_fc1204_complexity_ratchet.py` | `BCD01361E3025F99A78D8DB8452116D05D81DE685A4895D7B6FF34D7E93BB3F2` — table values: archive_retired_evidence.py 7, observability.py 6, prompt_injection.py 15, prune_retired_evidence.py 12 |
| coverage floor `tests/contract/test_fc1204_coverage_ratchet.py` (archive floor 95) | `FA0001209BB43BF49E63CA9B9D9463485E6F35B1B8ACCB69D0E7F78DEFE31C85` |
| CW git HEAD / origin-master | `bf0c8b27e83c3ee7e533c6031fefad8e27e5e121` / `f39bd5a64224cd0c7aa098f23f64bf3811fa8939` (read-only) |

NO frozen value increase. NO coverage threshold change (95 stays 95). NO baseline
additions. NO step bypass. Production writes ZERO.

### A.1 RC-2 4-row family — final spec (pure function splits ≤ frozen, ZERO behavior change)

| row | file | frozen | predecessor end-state (evidence) | this attempt's job |
|---|---|---|---|---|
| RC-2a | `src/company_wiki/source_catalog/archive_retired_evidence.py` | ≤7 (split achieved ≤6 in predecessor iso) | FIXED-in-iso (sha ISO `2A236072…`) | RE-VERIFY (CC + own family) + MUTATION (inline hot split → RED, restore → GREEN) |
| RC-2b | `src/company_wiki/source_catalog/observability.py` | ≤6 | →6 GREEN (predecessor iso sha `D398F921…`, family 23==26 unchanged) | RE-VERIFY + MUTATION |
| RC-2c | `src/company_wiki/source_catalog/prompt_injection.py` | ≤15 | →15 GREEN (predecessor iso sha `815691D1…`) — GUARD-MERGE face: hot `_disposal_gate` decomposition, semantics frozen (CW-TEST-DEBT-era unit tests + fc906a family must stay green) | RE-VERIFY + MUTATION |
| RC-2d | `src/company_wiki/source_catalog/prune_retired_evidence.py` | ≤12 | PARTIAL: main 17>12 (`20-ratchet-ALL-violations-GREEN.log`), F821 `absent`/`deleted` undefined (prune iso lines 605/630 — predecessor's half-written PR4 batch-loop extraction) | COMPLETE PR4 batch-loop replacement + fix the two F821 names (diagnosed: locals that the extracted `_plan_todo`/`_delete_batches` split stopped initializing — restore as proper local initializations, zero behavior change), RED(all-rows)/GREEN/mutation |

Frozen table sha before==after for every row. RED = all-rows ratchet scan
(`20-ratchet-ALL-violations`-style enumeration + the exact test), GREEN = all rows ≤ frozen,
mutation = merge one split → row turns RED → restore → GREEN.

### A.2 Test-face lanes (each red/green/mutation; ZERO product-source edits outside the 5 files: 4 product + `tools/pre_push_gate.py`)

1. `tests/contract/test_fc906a_producer_binding_metadata.py` — fix per NEW writer
   contract (`evidence_payload` etc.) — gate step-6 file.
2. `tests/contract/test_source_catalog_archive_retired.py` — adapt (`now=`-face / stale
   API) — archive family.
3. `tests/contract/test_source_catalog_prune_retired.py` — adapt `now=` (RED already
   captured in predecessor `23/26-families-*.log`: `missing 1 required keyword-only
   argument: 'now'` ×3) — prune family.
4. **6 stale contract tests** (final stale list = repo-wide grep `record_prompt_injection_review(`, contract tier, excluding fc906a above): `test_fc905_receipt_envelope.py`,
   `test_gp003_llm_exit_receipt_privacy_gate.py`, `test_r4b05_metadata_provenance.py`,
   `test_source_catalog_focus_admission.py`, `test_source_catalog_worker.py`,
   `test_zr1003_shadow_assertions.py`.
   `tests/unit/test_prompt_injection_guard.py` + `tests/unit/test_stage_taxonomy.py`
   (the two tests/unit faces) are already adapted/green → UNTOUCHED.

### A.3 Coverage lane (archive_retired_evidence NEW exception paths)

- BEFORE (predecessor measured, CI-equivalent): 85.38% (`16b-archive-coverage-numbers.log`;
  per mandate "85.4%<frozen 95"); missing lines 64, 96, 100-103, 120, 124, 133, 154, 199,
  206, 222, 302 (`16c`).
- Job: ADD TESTS (own file or into the existing archive family) covering the refactored
  file's NEW exception paths until the coverage ratchet metric is ≥95 under the
  CI-equivalent measurement (command pinned from `.github/workflows/ci.yml` +
  `test_fc1204_coverage_ratchet.py` semantics — measured, not trusted).
- Report before/after numbers. Floor 95 is FROZEN — never lowered; structurally-unreachable
  remainder → BLOCKED-with-evidence, no self-lowering.

### A.4 RC-1 re-verification (predecessor-done, reused)

Predecessor's RED (`01-gate-crash-RED.log`) + GREEN (`06-gate-crash-GREEN.log`) reused;
this attempt re-verifies GREEN repro on its own iso copy (rc propagation == 3) and keeps
the fix (encoding-safe print, `utf-8`/`errors='replace'`; step-failure rc still propagates).

### A.5 Gate full-run + CI prediction

- `tools/pre_push_gate.py` FULL default invocation → all 6 steps GREEN in iso/harness
  (with RC-1 fix in place), whole-gate rc 0; per-step status table.
- Read `.github/workflows/ci.yml`; predict each test-bearing step (contract/unit/coverage/
  e2e) post-fix pass/fail with basis.

### A.6 Change-file allowlist (successor-expanded; §0 allowlist superseded by mandate)

1. `tools/pre_push_gate.py` (RC-1)
2. `src/company_wiki/source_catalog/archive_retired_evidence.py` (RC-2a)
3. `src/company_wiki/source_catalog/observability.py` (RC-2b)
4. `src/company_wiki/source_catalog/prompt_injection.py` (RC-2c)
5. `src/company_wiki/source_catalog/prune_retired_evidence.py` (RC-2d)
6. test faces (≈9): the 3 lane-2 files + the 6 stale contract tests (A.2)
7. optional: 1 new coverage test file (A.3) or additions into the existing archive family
   — exactly one of the two, never both.
Total expected changed files: 5 product/tool + 9 test + 0-1 coverage = 14-15 (listed
exactly in changes.diff and decision.md).

### A.7 Hard constraints (inherited + successor)

- Predecessor attempt dir READ-ONLY (cite, never write). Its `%TEMP%\cwgu1\repo` iso is
  treated as frozen predecessor state; this attempt works on a COPY
  `%TEMP%\cwgu2\repo` (sha-verified identity at copy time).
- CW production writes ZERO; RF/FF untouched; no network; no git mutations (read-only git
  for pins + `git diff --no-index` + scratch-repo apply-check only); %TEMP% scratch.
- Strictly incremental; every judged run's raw output written to evidence/ at run time.
- Any NEW blocker (different species) → STOP-and-report per standing rule.
