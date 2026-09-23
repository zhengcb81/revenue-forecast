# CFI14FR1-SAMPLE — decision.md (attribution, hook effects, disclosures)

- Card/condition: **CFI14FR1-SAMPLE** discharges **CF-I14FR1-3** 「repo-global hook ⇒
  broader company-wiki suite sampling before merge/at batch-4」 of I-14-F-R1's acceptance.
- Attempt: `execution_runs/CFI14FR1-SAMPLE/a20260922-01`; plan `2026-09-19-three-project-history-audit`.
- Oracle: `oracle.md` FROZEN FIRST (sha256 `126118e35315cc3cd02102d03efa607081246f891860203690bc440dbedfea99`,
  15332 B) — no pytest process of this attempt existed before that freeze.
- Status: `handoff.json.status = review_pending`; nothing here is self-signed or signed.
- Sample (oracle §1): **every** `tests/contract/test_*.py` (205) + `tests/unit/test_*.py` (63)
  = **268 files**, one pytest session; exclusions exactly as frozen (acceptance/e2e/
  integration/archive/root-level files/network-credential-dependent — none silently added
  or dropped; no `-m` marker filter).

## 1. Timeline (all times local; every step disclosed, nothing overwritten)

| when | label | what | outcome |
|---|---|---|---|
| pre-run | `CF-s0` | oracle.md frozen; `sample_set_freeze.txt` (268+4 entries, sha `7fcdf10b…`); baselines `00_baseline_lastfailed/nodeids` | ok |
| 22:52–22:55 | `01_with_hook` | **BURNED**: background shell ran from the session workspace instead of the CW root (my cwd-pinning omission; `workdir` not passed) | pytest usage error `file or directory not found: tests/unit` (revenue-forecast HAS `tests/contract`, so only the unit path errored), **rc=4**, 75 B `de8c5473…`; hook never loaded (no decision line); `revenue-forecast/.pytest_cache` mtime still `2026-07-12 23:30:51` ⇒ workspace untouched. Bytes kept write-once. |
| 22:56:57–23:06:02 | `01b_with_hook` | correct cwd; **INTERRUPTED**: the harness background-job tree was killed (job record vanished, completion notification lost) | raw output truncated mid-line at 8 % of the progress buffer (3173 B, `collected 2827 items` present, **no** summary line, no rc/meta); hook DID record its decision (jsonl captured); last basetemp dir mtime `23:06:02` = kill moment (listing preserved in `evidence/01b_basetemp_leftovers.txt`, later cleaned — own %TEMP% debris). Bytes kept write-once. |
| 00:13:41–01:05:02 | `02_rerun` | parent dispatch: full sample re-run, DETACHED (Start-Process) so a job-registry loss cannot kill it | **COMPLETE**: `14 failed, 2805 passed, 8 skipped in 3038.18s (0:50:38)`, wrapper rc=1, elapsed 3080.8 s — the authoritative sample output |
| 01:07:33–01:11:37 | `03_<stem>_rerun` ×5 | per-failing-file controls, hook redirect DISABLED (`CW_SHORT_BASETEMP_DISABLE=1`) | 4× rc=1 (same failures), 1× rc=0 (zr409) |
| 01:07:33–01:11:37 | `04_redirect_probe` | 84-char over-budget basetemp, hook ACTIVE | rc=0, **relocated=true + cleanup removed=true** (quotes §3) |
| ~01:14–01:16 | `05_zr409_hookactive_single` | 3rd arm: suspicious zr409 alone WITH hook | rc=0, 10 passed |
| ~01:15–01:17 | `06_parser_liveness_hookactive_single` | 3rd arm: parser_liveness alone WITH hook | rc=0, **20 passed** |
| 01:17+ | `CF-c4` | re-hash drift check + full CW tree mtime scan | see §5 |

**Label deviation (disclosed, `commands.json` NOT edited — it stays byte-frozen):**
`commands.json` pre-registered `01_with_hook` / `02_<stem>_rerun` / `03_redirect_probe`.
Reality renumbered them: `01_with_hook` burned → sample output lives at `02_rerun.*`
(name fixed by the parent's dispatch), controls at `03_*_rerun.*`, probe at `04_*`, plus two
unregistered-but-necessary attribution arms `05_*`/`06_*`. The RULES (argv, env, basetemp,
write-once, attribution logic) are unchanged from the frozen file; only label strings moved.
Two wrapper launches (run02, run03 attempt 1) died producing **zero artifacts** (PS 5.1
`-File` read the BOM-less UTF-8 wrapper as ANSI ⇒ the Chinese path mojibake'd) — no label was
burned by those; fixed by UTF-8-BOM wrappers, disclosed here.

## 2. Results (inventory — `evidence/summary.json`, reconciliation ok=true)

| root | files | passed | failed | skipped | errors |
|---|---|---|---|---|---|
| `tests/contract` | 205 | 2006 | **14** | 8 | 0 |
| `tests/unit` | 63 | 799 | **0** | 0 | 0 |
| **total** | **268** | **2805** | **14** | **8** | **0** |

- `collected 2827` == 2805+14+8 (sum of per-file counts == raw summary line; parser method:
  2827 progress chars + 14 short-summary nodeids; `evidence/02_rerun.lastfailed.json`
  (copy taken immediately after run 02, before any control) delta-computed against
  `00_baseline_lastfailed.json`).
- Skips (counts per file; reasons not printed by default `-r`): `test_r9_v1_removal_gate.py`
  ×4 (module skipif), `test_fc1204_coverage_ratchet.py` ×2, `test_dropbox_root_policy_fc501.py`
  ×1, `test_r4b03_stable_bytes.py` ×1 — the self-gating style the oracle pre-declared as
  "recorded, not excluded".
- **7 of the 14 failures were already in the PRE-RUN `lastfailed` baseline dated
  2026-09-19** (before `conftest.py` existed — the hook commit `ac4ebd0` is 2026-09-22):
  parser_liveness ×6 (`fast_parser`, `slow_parser`, `hung_parser`, `parser_exception`,
  `oversized`, `spawn_non_ascii`) + zr409 `c2_journey_dayu_only_real_sample`.

## 3. Hook-effect evidence — verbatim quote lines (oracle A2)

**a) Sample run = within-budget NO-OP branch (pre-computed at freeze: len 49 ≤ 60):**
`evidence/02_rerun.decision.jsonl` line 1 / `evidence/02_rerun.txt` line 1:

```
CW-BASETEMP-DECISION {"event": "decision", "requested_basetemp": "C:\\Users\\\u90d1\u66fe\u6ce2\\AppData\\Local\\Temp\\cf14fr1-with-hook", "requested_basetemp_len": 49, "cwd_len": 34, "threshold": 60, "win32_path_limit": 210, "generation_reserve": 150, "relocated": false, "reason": "within-budget"}
```

(line 2 of the same jsonl, len 58, is the contract test's own `test_configure_hook_within_budget_never_reroutes`
call writing through the same decision file — both branches exercised even inside the sample.)

**b) Redirect FIRING on the over-budget probe (84 > 60) — `evidence/04_redirect_probe.decision.jsonl`:**

```
{"event": "decision", ..., "requested_basetemp_len": 84, "cwd_len": 34, "threshold": 60, "win32_path_limit": 210, "generation_reserve": 150, "relocated": true, "reason": "resolved-basetemp-exceeds-budget", "effective_basetemp": "C:\\Users\\\u90d1\u66fe\u6ce2\\AppData\\Local\\Temp\\cw-pytest-basetemp\\20260923-001135-9b6efb68", "effective_basetemp_len": 75}
{"event": "cleanup", "dir": "...\\cw-pytest-basetemp\\20260923-001135-9b6efb68", "existed": true, "removed": true}
```

stdout echo lines are in `04_redirect_probe.txt` (head `CW-BASETEMP-DECISION …relocated: true…`,
tail `CW-BASETEMP-CLEANUP …"removed": true`); postcheck `04_redirect_probe.postcheck.txt`:
`basetemp04_len=84`, **`basetemp04_exists_after_run=False`** (the over-budget dir was never
created), fallback root contains ONLY the three pre-existing `20260921-*` leftovers of other
sessions (not this card's — untouched). Probe result itself: `15 passed`, rc=0 — the hook's
own contract test passes under a relocated basetemp.

**c) Controls prove the redirect was really OFF:** every `03_*.decision.jsonl` =
`"reason": "disabled-by-env"` (quintuple-checked, one per control file).

**d) 3rd arms:** `05`/`06` decision lines = `within-budget … relocated: false` (hook present,
still a no-op) with `10 passed` / `20 passed`.

## 4. FAILURE ATTRIBUTION TABLE (14 failures, 5 files — oracle A4)

| # | file (F in run 02) | control `03_*` (hook OFF) | 3rd arm (hook ON, single) | verdict + quoted delta |
|---|---|---|---|---|
| 1 | `test_fc1204_complexity_ratchet.py` — `test_complexity_ratchet_frozen_files_do_not_worsen` | **same 1 failed** (`1 failed, 1 passed`, rc=1), decision `disabled-by-env` | — | **pre-existing**: identical failing nodeid both arms. Quote: `AssertionError: archive_retired_evidence.py max complexity 19 exceeds frozen 7 … assert 19 <= 7` — a frozen-complexity gate tripped by the product-side `archive_retired_evidence` split; no path/basetemp shape anywhere. |
| 2 | `test_source_catalog_archive_retired.py` — `test_archive_exports_retired_evidence_with_row_reconciliation`, `test_archive_empty_when_no_retired_documents` | **same 2 failed** (`2 failed in 8.41s`, rc=1) | — | **pre-existing**: identical nodeids both arms; root cause quote (both nodes): `TypeError: archive_retired_evidence() missing 1 required keyword-only argument: 'now'` — product API drift, byte-identical with hook off. |
| 3 | `test_source_catalog_prune_retired.py` — `test_prune_dry_run_reports_span_volume`, `test_prune_apply_deletes_spans_when_due`, `test_prune_apply_within_retention_does_nothing` | **same 3 failed** (`3 failed in 15.82s`, rc=1) | — | **pre-existing**: identical nodeids both arms; same `TypeError: … missing … 'now'` quote — same product-API cluster as #1/#2 (one refactor, three symptom files). |
| 4 | `test_source_catalog_parser_liveness.py` — **7 nodes** (`fast`, `slow`, `hung`, `parser_exception`, `oversized`, `invalid`, `spawn_non_ascii`) | **2 failed** only: `test_slow_parser_keeps_parent_progress_live`, `test_invalid_parser_result_is_rejected` (`2 failed, 18 passed in 121.28s`); 5 nodes PASSED | `06_…` : **20 passed, rc=0** (hook ACTIVE) | **pre-existing (timing/context-flaky), NOT hook-induced.** (i) 6 of the 7 already failed in the **pre-hook 2026-09-19 baseline**; (ii) failure shapes are wall-clock: control quote `NormalizationTimeoutError: parser process 11668 exceeded 5.0s for …\cf14fr1-with-hook\test_slow_parser_keeps_parent_0\slow.txt` — a 5 s budget that full-suite load breaks; (iii) both single-file arms (hook ON and OFF) pass most of these nodes → the delta tracks LOAD/ORDER, and the hook is structurally a no-op here (§3a: `config.option.basetemp` never rewritten ⇒ its only mutation absent). Verdict: pre-existing flaky under load; **no hook mechanism exists for this delta** — recorded, not waved through: re-run under load could reproduce the 7. |
| 5 | `test_zr409_fourth_root_real_journeys.py` — `test_c2_journey_dayu_only_real_sample` | **PASSED** (`10 passed in 6.45s`, rc=0) | `05_…` hook ACTIVE: **10 passed, rc=0** | **pre-existing (order/state-dependent), NOT hook-induced.** Nodeid already in the pre-hook 2026-09-19 baseline (full-suite context). Delta quote — main run: `AssertionError: assert '552bc0f2df92…5aa51652479f9' == 'f4752b290221…03a0f0118d43d'` (portfolio shallow fingerprint after an earlier real journey in the same session); both single-file arms pass ⇒ failure needs full-suite state accumulated BEFORE this file, and reproduces with the hook absent (9/19 baseline, hook didn't exist) ⇒ full-suite-order pre-existing. |

**Attribution summary: 14/14 pre-existing (4 files identical across hook-ON/OFF arms;
1 file pre-existing flaky-under-load with 6/7 nodes failing pre-hook; 1 node pre-existing
order-dependent with a hook-ON single-file PASS). Hook-induced failures: 0.**
Suspicion triggers demanded by A4 (messages mentioning basetemp/`WinError 206`/path length):
**none** — zero failure mentions `WinError 206`, `ERROR_FILENAME_EXCED_RANGE`, `cw-pytest-basetemp`,
or path length. The only basetemp substring in any failure (parser timeout paths) is the
ordinary temp-dir path where the test put its own slow file — present identically in the
disabled control (§4.3 quote).

## A6/A7 父裁记录 (parent rulings, recorded after this attempt's r1 handoff)

**(a) A5 drift=2/268 REATTRIBUTED — authorized concurrent edit, NOT a defect.**
The parent ruled (2026-09-23): the 01:01 writes to the two `tests/unit` files were made by
the parent's own **authorized test-face fix card `CW-TEST-DEBT/a20260922-01`** (the
GUARD-MERGE condition-1 side card; its oracle frozen 2026-09-22 23:59:56, executed in a
%TEMP% mirror, holding write authority for exactly these two CW `tests/unit` files; edits
landed around 01:01). Three-way hash comparison — parent after-pin = this attempt's 01:17
record (`evidence/binding_check_after.txt`) = re-measured live at ruling time — **all
three equal**:

| file | parent after-pin (abbrev) | full sha256 (all three equal) | bytes / mtime |
|---|---|---|---|
| `tests/unit/test_prompt_injection_guard.py` | `d3bde1a3…eec3f` | `d3bde1a3d5ec2495474aae5b91595362b2caad4c8a0178c6927bf2d8023eec3f` | 13143 B / 2026-09-23 01:01:16.133 |
| `tests/unit/test_readiness_graph.py` | `a5db0c9c…368c2` | `a5db0c9c6959d9c8cbd68d606eec0dc9368ab09f93168a2b892e3fd459f368c2` | 14187 B / 2026-09-23 01:01:01.197 |

(The freeze-era bytes run 02 actually collected: 10568 B `c05e25fb…f9bae` and 14137 B
`71893f5d…e08a7`, per `sample_set_freeze.txt`.) ⇒ **Attribution solid: authorized
concurrent test-face edit by `CW-TEST-DEBT/a20260922-01`; A5's drift=2 re-recorded as
AUTHORIZED — zero unattributed drift remains.** Sampling impact stays NONE: the edits
landed ~46 min after run 02's 00:14–00:15 collection of the freeze-era bytes; both files
passed (unit root 799/0/0); no control/arm touches `tests/unit`. The §5.3
"ownership question raised" is CLOSED by this ruling (§5.3 text kept verbatim as the r1
record; this section supersedes its open question).

**(b) Side-effect disposition APPROVED (parent ruling b):** the `.pytest_cache`
cache-file rewrites and the `.source_catalog` sqlite `-wal`/`-shm` volatile companions
**stay in place** — deleting them would itself be a CW tree write, so the
`recovery/README.md` "nothing to revert" logic stands as ruled; anchor unchanged:
46.3 GB `catalog.sqlite3` mtime `2026-09-19 07:31:35.406`. `evidence/01b_basetemp_leftovers.txt`
listing retained.

(Check-script slip disclosed: one ad-hoc final-check line compared
`evidence/01b_with_hook.decision.jsonl` against `02_rerun`'s hash constant and printed a
false `match=False`; the file is untouched (280 B, sha256
`314821b053d5367a65d219d517a95efeddefc43d6a4086260c094db363e1be07`) and its authoritative
pin is the `evidence/SHA256SUMS.txt` entry — re-verified equal in this attempt's final
check.)

## 5. Boundary & write-impact audit (oracle A5) — honest accounting

Scan window `>= 2026-09-22 22:50` over the ENTIRE CW tree (`evidence/tree_scan_after.json`,
6 hits):

1. `.pytest_cache\v\cache\lastfailed` (live 3676 B @freeze → 4200 B after run 02 → 3309 B
   after controls/arms, last write 01:15:50) and `.pytest_cache\v\cache\nodeids`
   (306906 B) — **the disclosed pytest side effect**. Note: the `.pytest_cache` DIRECTORY
   mtime itself stayed `2026-07-18 14:09:05.073` (only inner cache files rewritten in
   place — mtime impact moved to the files, both recorded). Point-in-time copies used for
   analysis were taken BEFORE later sessions mutated the live cache (`00_baseline_*`,
   `02_rerun.*`).
2. `.source_catalog\catalog.sqlite3-wal` (0 B, created 00:59:38) and
   `.source_catalog\catalog.sqlite3-shm` (32768 B, touched 01:12:51) — volatile SQLite
   companions created/refreshed when tests OPENED the catalog during the runs.
   **The database itself was NOT written: `catalog.sqlite3` = 49 677 344 768 B,
   mtime `2026-09-19 07:31:35.406`** (before the window; absent from the scan). No product
   content write occurred. Left in place deliberately: deleting them would itself be a CW
   tree write, and they are transient by design (disclosed, not hidden; see recovery).
3. **`tests\unit\test_prompt_injection_guard.py` 10568 → 13143 B (mtime 01:01:16) and
   `tests\unit\test_readiness_graph.py` 14137 → 14187 B (mtime 01:01:01)** — DRIFT against
   the freeze manifest (`evidence/binding_check_after.txt`: checked=272, drift=2).
   **Not authored by this card**: no command in this session wrote either path; a repo-wide
   grep finds ZERO references to either filename in any `.py` (no test self-writes them);
   `tests\unit` DIRECTORY mtime moved to 01:01:16, the signature of an atomic save
   (temp+rename), i.e. an external editor/development session editing these files
   CONCURRENTLY with run 02 (heads: "ZR-302 gate tests…", "ZR-303 gate tests…" — active
   gate-test development). Impact on this card's results: **none** — run 02 imported both
   files at collection (00:14–00:15, freeze-era bytes); the 01:01 rewrites landed after
   import and these files never fail (unit root: 799 passed, 0 failed); no control/arm
   touches `tests/unit`. Both byte-states are pinned (freeze hashes in
   `sample_set_freeze.txt`, live hashes in `binding_check_after.txt`). **For the
   reviewer/owner: please confirm this concurrent edit belongs to your batch-4/ZR-302/303
   work** — this card will not touch it either way.
4. Everything else zero-drift: **all 4 anchors unchanged** (hook `conftest.py`
   `a908c9da…`, contract test `dfb7c6cd…`, `pytest.ini`, `tests/conftest.py`,
   `tests/contract/conftest.py`); **CW root `__pycache__` ABSENT before and after**
   (`PYTHONDONTWRITEBYTECODE=1` + `PYTHONPYCACHEPREFIX=%TEMP%\cf14fr1-pycache` — the prefix
   dir was never even created); **no git command of any kind**; no network; no credentials.
5. `%TEMP%` state: main basetemp `cf14fr1-with-hook` (own debris incl. the interrupted
   run's 120 test dirs) **removed at the end**; probe's over-budget dir never existed;
   hook fallback root contains only the three `20260921-*` leftovers **from other
   sessions (pre-existing, untouched by this card)**; hook-created fallback
   `20260923-001135-9b6efb68` self-removed (`removed: true`).

## 6. Disclosures register (nothing smoothed)

- D-1: label `01_with_hook` burned (cwd omission) — usage rc=4 kept write-once.
- D-2: label `01b_with_hook` interrupted by a harness job-tree kill; no rc/meta; buffer-
  truncated output kept write-once; full re-run as `02_rerun` per parent dispatch.
- D-3: label renumber vs `commands.json` (§1) — `commands.json` itself unedited.
- D-4: burned-01 wall clock anomaly: wrapper measured 154.1 s while pytest reported 0.04 s
  (cold interpreter/plugin autoload + whatever delayed the usage error); recorded verbatim
  in `01_with_hook.meta.txt`, unexplained, no impact (that run aborted before collection).
- D-5: wrapper launch failures (PS 5.1 ANSI read of BOM-less scripts) — zero-artifact, no
  label burned, fixed with BOM.
- D-6: inventory parser evolved during evidence generation — v1 mis-read Windows backslash
  paths and reported 0 files (caught by its OWN reconciliation gate, exit 2), fixed twice,
  final run exit 0 with `reconciliation.ok=true`; the raw byte streams it reads were never
  altered. Parser is an interpretation tool; the raw files + summary line are primary.
- D-7: external 2-file drift (§5.3) — recorded, not reverted, ownership question raised.
- D-8: `.pytest_cache` + `.source_catalog` companion effects (§5.1–5.2) — recorded with
  exact mtimes; main DB untouched.
- D-9: `dispatch commit ac4ebd0` unverified (git forbidden) — live hashes bound instead.

## 7. Verdict against the oracle (A1–A5)

- **A1 raw byte-exact**: every label's raw output on disk, pinned by
  `evidence/SHA256SUMS.txt`; write-once held (burned + truncated labels kept as-is). ✔
- **A2 hook-effect**: within-budget branch quoted (sample) + firing branch quoted (probe,
  decision **and** cleanup) + disabled-by-env quoted (controls). Both 150/60 branches
  evidenced against the live `conftest.py`. ✔
- **A3 inventory**: per-file/per-root pass-fail-skip for all 268 files, totals reconcile
  with the raw summary line, lastfailed delta computed from a pre-run baseline. ✔
- **A4 attribution**: 14/14 attributed with quoted deltas and third arms where the first
  delta was suspicious; 0 hook-induced; suspicion-trigger scan empty. ✔
- **A5 boundary**: no product write by this card; disclosed side effects and the external
  drift fully listed with evidence; anchors stable; no git. ✔ (drift=2 is external — see
  §5.3; A5's own expectation "zero drift" therefore records a TRUE deviation, attributed.)

**Condition posture (not self-signed):** the sampling obligation of CF-I14FR1-3 has been
PERFORMED with evidence; whether it discharges the condition is the reviewer/owner's call
(`handoff.status = review_pending`).
