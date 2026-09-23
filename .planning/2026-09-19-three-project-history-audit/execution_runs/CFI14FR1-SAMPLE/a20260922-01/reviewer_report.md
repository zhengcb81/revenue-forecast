# CFI14FR1-SAMPLE — independent reviewer report

- Card: **CFI14FR1-SAMPLE** · Attempt: `a20260922-01` · Plan: `2026-09-19-three-project-history-audit`
- Reviewer: independent session dispatched by parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`; review after the card's handoff and after the commissioned A6/A7 append (parent clarification received mid-review: A6/A7 was written by the card side — I verify it, I did not write it).
- Method: sampled independent re-measurement per the dispatch's 7 sections. Tools: `read` / `grep` / `pwsh` only; no product writes, no state-changing git (no git at all), no network; `%TEMP%` rule observed (this review executed no pytest — the only process run was the REM-79 self-check on this report, read-only) （域：read/grep/pwsh 3 tools）.
- The implementer handoff stays unsigned (`status=review_pending`, `signed=false`, `disclosure_adaptation=unmapped`, `accuracy=unproven` — verified live). This report is the reviewer's acceptance instrument.

## VERDICT: `accepted_scoped` — CF-I14FR1-3 = DISCHARGED by this evidence

The broader-suite sample was performed with the repo-global 150/60 hook ACTIVE over 268 files / 2827 nodes; both hook branches are quoted from raw bytes; all 14 failures are attributed pre-existing with hook-OFF controls and hook-ON third arms; hook-induced = 0; the suspicion scan is empty; the boundary held with exactly 2 drift files, independently confirmed three ways as the authorized `CW-TEST-DEBT` test-face edit. Every pin, manifest entry, total and disclosure named in the dispatch was re-measured; findings are 6 non-blocking entries. Acceptance is scoped by the *Scope of acceptance* section (域：6 scope conditions + 6 findings).

---

## 1. Deliverables & freeze chain — VERIFIED by independent re-hash

| artifact | my live measurement | pin claimed | result |
|---|---|---|---|
| `oracle.md` | `126118e35315…edfea99`, 15332 B, mtime 2026-09-22 22:48:02.268 | `126118e3…` frozen-first | MATCH |
| `commands.json` | `54f538dfee29…f23e405a`, 8571 B, mtime 22:51:39.291 (pre-run, unedited) | `54f538df…` byte-frozen | MATCH |
| `decision.md` | `9320461b0845…fe7c629e`, 20157 B | `9320461b…` (r1 `f5797965…`/17500 B retained in binding as history — per parent clarification, verified non-drift) | MATCH |
| `handoff.json` | `55af2fc02c28…f84f65`, 12486 B; review_pending/unmapped/unproven/signed=false | `55af2fc0…` unchanged | MATCH |
| `binding.json` | `857f526c0baf…4b96139`, 8538 B, mtime 01:28:46.432 = last prose carrier | written last, pins all carriers （域：8 attempt files） | MATCH |
| `recovery/README.md` | `b8040a56985d…491a1a89`, 2109 B — "nothing to revert" | `b8040a56…` | MATCH |
| scratch (3 files) | `f54656bc…`/11156, `c200d9fe…`/2021, `6c0c4104…`/3770 | binding pins | MATCH 3/3 |

- **Freeze-first ordering (local = UTC+1, consistent across all carriers):** oracle 22:48:02 → manifest `generated_utc 2026-09-22T21:51:33Z` (mtime 22:51:38) → commands 22:51:39 → first pytest of this attempt finished `21:55:39Z` (22:55:39 local). Baselines copied pre-run with source mtimes preserved (`00_baseline_lastfailed` = 2026-09-19 09:43:09, i.e. pre-hook; `00_baseline_nodeids` = 22:22:59 from a pre-existing collection). ✔ （域：5 timestamped stages）
- **Checksum manifest fully re-verified:** `evidence/SHA256SUMS.txt` = `4befaaff1ba1…63770c8`, 5086 B, **46 entries → 46/46 sha256 exact, 46/46 declared byte-sizes exact, every one of the other 46 evidence files covered**; `evidence/` holds exactly 47 files (46 + the manifest itself). Method: parsed `<sha>  <name>  # N B` lines, re-hashed each file live （域：46 entries）.
- **Decision content:** §4 attribution table present with 5 clusters/14 rows-worth of nodeids; §3 verbatim hook lines (both match the raw jsonl/txt I read); §7 A1–A5 verdicts; `## A6/A7 父裁记录` section present with ruling (a) three-way table + ruling (b) disposition + the honest check-script-slip note (its claimed true value `314821b0…`/280 B = manifest entry for `01b_with_hook.decision.jsonl` — I verified the file: exact).

## 2. Totals — VERIFIED, arithmetic exact

- Authoritative raw `02_rerun.txt` = `e3ad00741f53…725dfc01`, 34269 B, 417 lines; **summary line (line 417): `14 failed, 2805 passed, 8 skipped in 3038.18s (0:50:38)`**; `rc.txt` = 1; meta `elapsed_seconds=3080.8`, `finished_utc 2026-09-23T00:05:02Z`; started `2026-09-22T23:13:41Z` with `hook=ACTIVE (CW_SHORT_BASETEMP_DISABLE absent)` （域：1 run）.
- `summary.json` = `15d893020a8a…a97261df`, 48469 B; **`reconciliation.ok=true`, `problems=[]`**; `collected_declared=2827`, `totals_sum=2827`, votes `progress_chars=2827` + `short_summary=14`, `files_seen=268`.
- Per-root split: contract **205 files / 2006 passed / 14 failed / 8 skipped**; unit **63 / 799 / 0 / 0**.
- My arithmetic: 2006+799=**2805** ✔ · 14+0=**14** ✔ · 8+0=**8** ✔ · 205+63=**268** ✔ · 2805+14+8=**2827**=collected ✔ · (2006+14+8)+(799+0+0)=2028+799=**2827** ✔.
- Cross-checks: `failed_nodeids` (14) == the 14 `FAILED` lines 403–416 of the raw ✔; lastfailed delta new=post−pre = **7** nodes (complexity 1 + archive 2 + prune 3 + parser `invalid` 1), pre_count 32 → post 37 (cleared 2) ✔; `reconciliation.informational` names exactly the **7-of-14** nodes already failing in the pre-run baseline ✔.

## 3. Attribution spot-check (3 of 4 cluster groups) — VERIFIED from raws

All five control raws' line 1 is the hook decision echo **`"reason": "disabled-by-env"`** (redirect provably OFF), and all 5 control `*.decision.jsonl` are byte-identical (`f1a6bd63…`, 282 B, in the manifest) （域：5 controls）.

- **complexity_ratchet (1F):** control `03_…fc1204…` = `1 failed, 1 passed`, rc=1 (rc-hash `f1b2f662…` group), failing nodeid identical to run 02; quote `AssertionError: archive_retired_evidence.py max complexity 19 exceeds frozen 7 … assert 19 <= 7`. No path/basetemp shape. → **pre-existing, identical both arms.**
- **archive (2F) + prune (3F):** controls `2 failed in 8.41s` / `3 failed in 15.82s`, nodeids identical to run 02; quotes `TypeError: archive_retired_evidence() missing 1 required keyword-only argument: 'now'` (×2) and `TypeError: prune_retired_evidence() missing 1 required keyword-only argument: 'now'` (×3) — one product-API `now` drift, byte-stable with hook OFF. → **pre-existing.**
- **parser_liveness (7F):** control = `2 failed, 18 passed in 121.28s` (only `slow_parser` + `invalid_parser`); wall-clock quote `NormalizationTimeoutError: parser process 11668 exceeded 5.0s for …\cf14fr1-with-hook\test_slow_parser_keeps_parent_0\slow.txt` (identical class in the disabled arm); third arm `06_…` hook-ON single = **20 passed, rc=0**; **`00_baseline_lastfailed.json` (mtime 2026-09-19, pre-hook) contains 6 of the 7 nodes** — `fast`, `slow`, `hung`, `parser_exception`, `oversized`, `spawn_non_ascii` present; only `invalid` absent （域：6 of 7 nodes）. → **pre-existing flaky-under-load, no hook channel** (hook a structural no-op here per §4 below).
- **zr409 (1F):** control hook-OFF = **10 passed, rc=0**; third arm `05_…` hook-ON single = **10 passed, rc=0**; baseline contains `…::test_c2_journey_dayu_only_real_sample` ✔; run-02 quote `AssertionError: assert '552bc0f2df92…5aa51652479f9' == 'f4752b290221…03a0f0118d43d'` (portfolio fingerprint, needs full-suite prior state). → **pre-existing order/state-dependent, not hook-induced.**
- **Suspicion scan:** grep over the raw containing all 14 failure texts for `WinError 206|ERROR_FILENAME_EXCED_RANGE|cw-pytest-basetemp|path length` → **ZERO hits** （域：4 patterns × 14 failure texts）. The single `cf14fr1-with-hook` substring in parser timeouts is the ordinary requested-basetemp path, present identically in the hook-OFF control.
- The 14 nodeids decompose 1+2+7+3+1 exactly as decision §4 and the parent's ledger split (1 complexity + 5 `now`-drift + 7 wall-clock + 1 fingerprint) ✔.

## 4. Hook effect — VERIFIED by reading every jsonl/txt raw （域：10 decision jsonl + 11 txt raws）

- **Sample = within-budget NO-OP branch:** `02_rerun.decision.jsonl` line 1 = `requested_basetemp_len: 49, threshold: 60, relocated: false, reason: "within-budget"`; line 2 = the contract test's own `cw-i14f-unit-within-budget` call at **len 58** (both branches exercised inside the sample) (域：2 decision lines). `02_rerun.txt` line 1 carries the same decision echo byte-for-byte as decision §3a's quote ✔.
- **Probe = FIRING branch:** `04_redirect_probe.decision.jsonl` line 1 = `requested_basetemp_len: 84` > `threshold: 60`, `relocated: true`, `reason: "resolved-basetemp-exceeds-budget"`, `effective_basetemp …\cw-pytest-basetemp\20260923-001135-9b6efb68`, `effective_basetemp_len: 75`; line 3 cleanup `existed: true, removed: true`. `04_redirect_probe.txt`: stdout decision echo (line 1), **`15 passed in 0.99s`**, cleanup echo (line 14). `.postcheck.txt`: `basetemp04_len=84`, **`basetemp04_exists_after_run=False`**, fallback root lists only 3 entries — the foreign `20260921-*` ones. rc-hash group = 0 ✔.
- **Controls:** 5/5 `disabled-by-env` (raw line 1 + jsonl, both channels). **Arms:** `05`/`06` decision lines = `within-budget, relocated: false` with hook ACTIVE, outcomes `10 passed` / `20 passed`.
- Live `conftest.py` constants confirmed by grep: `WIN32_PATH_LIMIT=210`, `GENERATION_RESERVE=150`, `BASETEMP_MAX_CHARS=…# 60`, `DISABLE_ENV="CW_SHORT_BASETEMP_DISABLE"`, `DECISION_FILE_ENV="CW_BASETEMP_DECISION_FILE"` — the recorded arithmetic matches the live file （域：5 constants）.

## 5. Hash stability & boundary (oracle A5 / parent ruling a) — VERIFIED

- **5 anchors live re-hash == freeze == binding:** `conftest.py` `a908c9da…`/9031 · contract test `dfb7c6cd…`/11366 · `pytest.ini` `013980c5…`/360 · `tests/conftest.py` `ab0dc93e…`/6715 · `tests/contract/conftest.py` `1f495987…`/2011 (all mtimes predate the run window) — 0/5 anchor drift （域：5 anchors）.
- **Full freeze-manifest re-hash by me (independent of the card's check):** all **272 entries** (268 test files + 4 anchors) re-hashed live → **270 exact, drift = exactly the 2 adjudicated files, missing 0** （域：272 entries）. This reproduces `binding_check_after.txt` (`checked=272, drift=2`) from scratch.
- **Parent ruling (a) — three-way equality CONFIRMED (I verified, did not re-litigate):** live re-hash equals BOTH sets:

| file | freeze (before) | parent after-pin | CW-TEST-DEBT's own recorded after-pins | live now |
|---|---|---|---|---|
| `tests/unit/test_prompt_injection_guard.py` | 10568 B `c05e25fb…f9bae` | `d3bde1a3d5ec2495…023eec3f` /13143 B /mtime 01:01:16.133 | `d3bde1a3d5ec2495474aae5b91595362b2caad4c8a0178c6927bf2d8023eec3f` in CW-TEST-DEBT `binding.json`/`handoff.json`/`changes.diff`/`evidence/raw/live_pins_after_edits.json`, before `c05e25fb…` | **identical** 13143 B, 01:01:16.133 |
| `tests/unit/test_readiness_graph.py` | 14137 B `71893f5d…4708a7` | `a5db0c9c6959d9c8…459f368c2` /14187 B /mtime 01:01:01.197 | `a5db0c9c6959d9c8cbd68d606eec0dc9368ab09f93168a2b892e3fd459f368c2`, before `71893f5d…` | **identical** 14187 B, 01:01:01.197 |

  ⇒ A5 drift=2/268 re-attributed to the authorized concurrent test-face edit (CW-TEST-DEBT), zero unattributed drift; sampling unaffected (run 02 collected the freeze-era bytes at 00:14–00:15 local, edits landed 01:01, unit root 799/0/0, no control/arm touches `tests/unit`).
- **Parent ruling (b) — volatile companions verified left in place:** live `.source_catalog/catalog.sqlite3` = **49 677 344 768 B, mtime 2026-09-19 07:31:35.406** (anchor untouched); `-wal` 0 B + `-shm` 32768 B present (as ruled); `.pytest_cache` DIRECTORY mtime still `2026-07-18 14:09:05.073` with inner `lastfailed` 3309 B @ 01:15:50 (the disclosed file-level rewrite). `tree_scan_after.json` = exactly the 6 disclosed hits (2 pytest cache, 2 sqlite companions, 2 drift files) ✔.
- **CW root `__pycache__`:** absent live and in `binding_check_after.txt` (`cw_root_pycache_exists=False`); `cf14fr1-pycache` prefix never created ✔.

## 6. Disclosures — VERIFIED against raws (D-1, D-2, D-3, D-6 + leftovers/fallbacks)

- **D-1 burned `01`:** 75 B `de8c5473…fa9110` (manifest), content `ERROR: file or directory not found: tests/unit` + `no tests ran in 0.04s`, `rc.txt`=4, meta `elapsed_seconds=154.1` (D-4 anomaly recorded verbatim); **workspace untouched** — live `revenue-forecast/.pytest_cache` directory mtime = `2026-07-12 23:30:51.473` (its inner `lastfailed` mtime 2026-09-22 09:23:38 predates the burned run at 22:55) ✔.
- **D-2 interrupted `01b`:** 3173 B `655969c7…49f` (manifest), line 1 decision within-budget(49), line 9 `collected 2827 items`, buffer ends inside the **8%** progress block with no summary/rc/meta files in evidence (write-once kept); kill moment `2026-09-22 23:06:02` corroborated by `01b_basetemp_leftovers.txt` header and the raw's mtime 23:06:01; **`02_rerun` detached Start-Process rerun per parent instruction** — `scratch/run02.ps1` header documents the detachment + rationale, `02_rerun.started.txt` records `launched_utc 2026-09-22T23:13:41Z / workdir=CW / hook=ACTIVE` ✔.
- **D-3 tag renumbering:** `commands.json` byte-frozen at pre-run hash (§1) — the frozen file still says `01_with_hook`/`02_<stem>_rerun`/`03_redirect_probe`; reality's `02_rerun`/`03_*_rerun`/`04_*` + arms `05/06` are disclosed in decision §1 and binding `open_disclosures` ✔.
- **D-6 parser v1 backslash bug self-caught:** `scratch/parse_inventory.py` contains the backslash-normalization block (lines 89–98) and the gate `return 0 if rec["ok"] else 2` (line 278) — exit 2 on mismatch is structural in the shipped code; the tool only `read_bytes()` the raws (never writes them); final `summary.json` = `ok=true` (域：1 gate). Raw byte streams remain pinned by the manifest ✔.
- **`01b_basetemp_leftovers.txt`:** 123 lines = 2 headers + **120 test-dir entries** + `# total_dirs=120` (pre-cleanup listing); main basetemp `cf14fr1-with-hook` now absent, `cf14fr1-deep` absent, `cf14fr1-pycache` absent ✔.
- **Three 9/21 fallbacks untouched (others'):** live `%TEMP%\cw-pytest-basetemp` holds exactly `20260921-190059-17c7658b`, `20260921-191555-955cf2e1`, `20260921-193155-314e23fc` with unchanged 2026-09-21 mtimes; this card's probe fallback `20260923-001135-9b6efb68` self-removed ✔.

## 7. Boundaries — VERIFIED (zero product writes / zero git verbs / no network)

- **Product writes by this card = 0:** 270/272 freeze entries byte-identical + the 2 drift files adjudicated above; the only in-window CW mutations are the 6 disclosed scan hits; the 46.3 GB catalog DB mtime anchor unchanged; root `__pycache__` never existed (域：6 scan hits).
- **Git verbs in command carriers = 0 invocations:** explicit scan of `commands.json` + all 3 `scratch/*.ps1|.py` for `\bgit\b|Invoke-WebRequest|Invoke-RestMethod|curl|wget|WebClient|Start-BitsTransfer` → the only hits are `commands.json`'s 2 occurrences inside its own prohibition declaration line (`"git": "NO git command of any kind…"`); the 3 scripts have 0 hits （域：4 command carriers）. Repository-wide grep likewise found `git`/URL strings only in prose declarations and in test-nodeid data inside evidence JSONs — never as a command.
- **Network:** no HTTP client verb in any carrier; suite is hermetic by `tests/conftest.py` (socket block, read at freeze by the card; constants re-confirmed live in §4).
- **This review's own writes = exactly 2 files** (`reviewer_report.md`, `reviewer_report.sha256`); everything else read-only; no state-changing git (no git at all); the REM-79 self-check was a read-only stdout run （域：2 written files）.

---

## Findings (numbered — 6 non-blocking)

**F1 (low, documentation nit).** `handoff.json`'s `failure_attribution.per_file` row for `test_source_catalog_prune_retired.py` quotes `TypeError: archive_retired_evidence() missing … 'now'`, but the raw control and main-run text say **`prune_retired_evidence()** missing 1 required keyword-only argument: 'now'`. Same root-cause class (one `now`-keyword refactor, 3 symptom files); `decision.md` §4 row 3 carries the correct elided quote. Quote-level mislabel in one carrier only; attribution verdict unaffected.

**F2 (info, honest observation for the ledger).** The truncated `01b_with_hook` buffer contains an `F` marker at `test_automation_cli` (~4%) that is **not** among run-02's 14 failures. The run has no summary line, so that marker is unattributable by construction; both arms ran the identical within-budget no-op hook decision, so no hook channel exists for the difference — consistent with the load/order-flaky profile already documented for this suite. Recorded so the interrupted run's partial face is not silently ignored.

**F3 (info, timeline).** The commissioned A6/A7 append + binding re-pin landed at `01:28:18`/`01:28:46`, i.e. as this review began: my first directory listing saw the pre-append state (`decision.md` 17500 B, `binding.json` 7314 B) and my later measurements saw the final state (20157 B / 8538 B). Final bytes match the parent's clarified pins exactly — this is the documented append, not drift （域：2 carriers）.

**F4 (info, count wording).** The dispatch says "live re-hash all **6**" while listing 5 anchor files; I re-hashed the 5 anchors plus the freeze manifest (`sample_set_freeze.txt` `7fcdf10b…`/31467 B, 274 lines = 2 headers + 268 test + 4 anchors) to make 6 pins — all stable.

**F5 (info, structural).** `binding.json` cannot pin itself; its integrity rests on this review's measurement (`857f526c0baf…4b96139`, 8538 B) and on the fact that each pin it states about other carriers re-measured exact (§1).

**F6 (info, parser artifact).** `summary.json.skipped_nodeids` is `[]` although `skipped=8`; skip counts are present per file and per root (r9 gate ×4, fc1204 ×2, dropbox-root ×1, r4b03 ×1 per decision §2, summing to 8 across 4 files), because `-q` prints no per-skip lines for the parser to harvest. Reconciliation (`ok=true`) compares counts, not skip ids; no verdict impact （域：8 skips / 4 files）.

## Scope of acceptance (binding — read together with the verdict)

1. **CF-I14FR1-3 = discharged by this evidence:** a broader-suite sample (every `test_*.py` under `tests/contract` + `tests/unit` = 268 files / 2827 nodes, one session, no marker filter) ran with the repo-global hook ACTIVE; both 150/60 branches are quoted from raw bytes (within-budget 49/60 on the sample; firing 84>60 → effective 75 + cleanup `removed:true` on the probe); controls prove the redirect OFF; 14/14 failures pre-existing; hook-induced = 0; suspicion scan empty; boundary held.
2. **The 14 pre-existing failures are separate pre-existing debt, NOT this condition's scope** — parent's ledger list (域：14 failures): **complexity ratchet 1** (`test_fc1204_complexity_ratchet`, frozen-complexity gate) · **archive/prune `now` API drift 5** (2 + 3, keyword-only `now` refactor) · **parser_liveness wall-clock 7** (5.0s budget under full-suite load; 6 of 7 pre-date the hook) · **zr409 fingerprint 1** (order/state-dependent portfolio shallow fingerprint). Fixing this debt is out of CF-I14FR1-3.
3. **Volatile-companion handling per parent ruling (b):** the `.pytest_cache` cache-file rewrites and `.source_catalog` `-wal`/`-shm` companions stay in place; deleting them would itself be a CW write and must be its own sanctioned action (`recovery/README.md` logic stands).
4. **Label renumbering (D-1..D-3) and the two extra arms `05/06`** are accepted as disclosed: the frozen rules in `commands.json` (argv/env/write-once/attribution logic) are unchanged; merely label strings moved, and `commands.json` itself is byte-frozen at `54f538df…`.
5. **This verdict does not rest on unverifiable context:** dispatch commit `ac4ebd0` and batch-4 remain unverified (git forbidden); the binding uses live hashes instead, which is what the oracle pre-declared.
6. **The flake-shaped attributions (parser_liveness, zr409) are evidence-bounded:** they rest on the pre-hook baseline + both single-file arms + identical hook state across arms; a future high-load full-suite run could re-display the 7 wall-clock failures — they remain disclosed debt with that carry-forward risk, not "fixed" by this review.

## Not verified / limits of this review (unverified list)

1. Dispatch context `ac4ebd0` (CW commit) and batch-4 (revenue-forecast push) — **not verified**; git is forbidden by this card's boundaries, live hashes used instead.
2. The harness job-tree kill of `01b` (job record vanished, notification lost) — the kill itself is taken as disclosed; its material traces (8% truncation, missing rc/meta, 23:06:02 mtimes) are verified.
3. **D-4** wall-clock anomaly (154.1 s wrapper vs 0.04 s pytest) — read verbatim, remains unexplained, accepted as disclosed with no impact.
4. **D-5** two zero-artifact wrapper launch failures — no artifact exists to check (that is the claim); disclosure accepted.
5. **D-6**'s historical v1 exit-2 run — no retained stderr artifact; I verified the shipped gate's exit-2 structure, the final `ok=true`, and that raws are manifest-pinned.
6. Negative claims (**0 product writes / 0 git / 0 network by the card**) are supported by the hash/scan/verb evidence above but are not provable to certainty from repository state alone.
7. I did **not** independently re-parse all 2827 progress characters; totals were verified via the raw summary line, `summary.json` (`ok=true`), the 14-line short summary, and the lastfailed delta arithmetic — the parser remains an interpretation tool over primary raw bytes （域：2827 nodes）.
8. The 2026-09-19 baseline's producing run was not reconstructed; its pre-hook date rests on mtime + content consistency (both pre-date the hook).
9. `CW-TEST-DEBT`'s write-authority claims (oracle freeze time, mirror execution) were **not** audited beyond its recorded pins — the parent pre-verified those; I verified pin equality across both cards' records plus live bytes (§5).

## Reviewer boundaries (this review)

- Files written: exactly **2** — this `reviewer_report.md` and its sidecar `reviewer_report.sha256`, both inside the attempt. No plan file, product file, evidence file, oracle, decision, binding, handoff, or git state was modified （域：2 files）.
- No git of any kind; no network; no pytest re-run of CW; the one process executed by this review is the REM-79 self-check: `PYTHONIOENCODING=utf-8 python <REM79 attempt>\tools\check_domain_assertions.py reviewer_report.md` → **rc 0, 0 violations** (re-run after the final edit, result recorded in the message to the parent).
- Implementer handoff remains unsigned; acceptance authority for this attempt rests with this report, not with the implementer handoff.

— reviewer, independent session, `session-bfecd191…` dispatched; VERDICT `accepted_scoped` (CF-I14FR1-3 discharged, scoped by the 6 conditions above).
