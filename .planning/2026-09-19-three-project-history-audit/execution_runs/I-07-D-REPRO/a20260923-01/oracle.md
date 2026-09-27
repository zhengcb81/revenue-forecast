# I-07-D-REPRO oracle.md — FROZEN BEFORE ANY JUDGED RE-RUN

Card `I-07-D-REPRO` (parent dispatch: substantive fix for AUDIT-DESIGN **D3**, owner order
「审计中出现的问题每一个都要修复」, REMEDIATION_REGISTER §76 responsibility table row
D3 + §72(3) evidence-retention new rule + **REM-93**). Attempt `a20260923-01`.
Frozen: 2026-09-23/24 (local), AFTER read-only evidence investigation and BEFORE the
first judged product run of this attempt. No expected value below was produced by running
the re-run tooling; every comparison value is a **transcription already recorded inside
I-07-D attempt `a20260923-01`** (its `decision.md`, `verdict.json`s, `commands.json`) or a
frozen expectation from I-07-D's own pre-run `oracle.md`. Those in-attempt transcriptions
are this card's comparison oracle; the runs they describe (judged-run raw bytes in
`%TEMP%\i07d\cases\`) are lost (AUDIT-DESIGN §5-R2: `f02v`/`f03v` FileNotFoundError on
`%TEMP%\i07d\cases\F02|F03\…2025年度報告.pdf`; `f04v` silent false ×3).

## 0. What this card fixes (D3, verbatim scope)

> D3（中高·不可复核证据）：I-07-D 故障矩阵 F02/F03/F04 的字节级判据依赖
> `%TEMP%\i07d\cases\` 工作树（已消失、attempt 目录未留存），判决**不可独立重算**
> —— `raw_preserved`/`raw_intact_after_recovery`/`provenance_committed` 不可独立重算。

**Fix = RE-RUN the three fault cases F02/F03/F04 under the SAME harness with their
documented argv, and PRESERVE the judged raw bytes in-attempt**, so that the three case
verdicts become re-computable from preserved bytes and byte-linked to I-07-D's in-attempt
transcriptions (its decision values = the comparison oracle).

Out of scope (recorded, never silently dropped): F01/F05/F06 (already re-computable per
AUDIT-DESIGN §6.1 footnote), F-F06-audit / F-F05-cause product findings (REMEDIATION
ledger, not this card), I-07-D F04 **attempt-1** overwrite history (its §7.1 transcription
remains the only surviving account of attempt-1 and is NOT re-created here — this card
re-runs the JUDGED runs, not the superseded attempt-1).

## 1. Frozen input pins (sha256, full values measured 2026-09-23 before any run)

I-07-D attempt `PLAN/execution_runs/I-07-D/a20260923-01` is **READ-ONLY reference**.
Comparison oracle = its in-attempt transcriptions:

| I-07-D file | sha256 | role here |
|---|---|---|
| `decision.md` | `ba6e4a1d0d1190f79c0c0519e61d16d6542cfab6e14184879897047c4c01f730` (31292 B) | **comparison oracle**: §2 rows F02/F03/F04, §4 delta rows, §6 kill evidence, §7.1 transcription (F04 attempt-1, historical) |
| `evidence/cases/F02/verdict.json` | `8d6e7a8b6236f87a2cb47996eaa3e4f6abdeca0c718629d5fb7eb6c36f097b94` (2780 B) | recorded measured values + check-key set F02 |
| `evidence/cases/F03/verdict.json` | `6f5b6e6f7a212e1eea364ea81d2de7c8c93ea91fe9bee41828e2a9c94c6b674d` (1498 B) | same, F03 |
| `evidence/cases/F04/verdict.json` | `f043c08014c21605a97fe3e6a71a9fb4826099ad300cc0982ecefcd2f8678c5f` (3636 B) | same, F04 |
| `oracle.md` (frozen pre-run) | `576ddfc57c2c949d6a9e5f875114d8c7e49c833d69b5bd8cd81bcf2417718846` (27211 B) | frozen per-case expectations (its §2 F02/F03/F04 + §3 trigger table + §4 delta table + §5 kill spec) |
| `commands.json` | `458c62c36824014c3f9552e46f4b0851d30242db8508da16e1c4a7e09ccce66e` (13107 B) | documented argv for the ORIGINAL runs (CMD-D-BUILD/WPROBE/F02/F03/F04/VERDICTS) |
| `harness/run_d_matrix.py` | `40b9f87a03bd8fd29c8187c2f51c3dfc339ddad7d0a852c2eee36f1c0f08334a` (77181 B) | harness re-used VERBATIM (byte-identical copy in this attempt; `common.ATTEMPT` = its own parent ⇒ evidence lands HERE) |
| `harness/run_case.py` | `aae0f21efb684d071aa704703b81f938d8a7d61c60c3726e2d18ff947269906c` | verbatim copy |
| `harness/common.py` | `79e36607db2aba407652eca12296f1bfbf609e4162a28a6acdd7cc77726ad7bc` | verbatim copy |
| `harness/build_iso.py` | `172ca0b3f1a1edc10eb876ce9aedb7cec105c6120b2dd418f7d5a1a222f8daac` | verbatim copy |
| `harness/hold_file.py` | `4a6cf71fb12b8348df3f78ccd43ebb7ae0335779218c64e0c20573c7fbb57fed` | verbatim copy (F02 share-none hold) |
| `harness/lock_catalog.py` | `af33d1b853e212f09b3079c486be182a6f3bf63687e368cd628b8f2a37aaed50` | verbatim copy (F03 BEGIN EXCLUSIVE hold) |
| `harness/spy/sitecustomize.py` | `7b3b9cbe8d0e463318f445033a9e907404f78f5a75610ef442b53e96d932508d` | verbatim copy (count-on-entry spy) |
| `fixtures/HK-XIAOMI-2025.provider.json` | `8215b3609b670f175c191910d5cb377a344c8cc483731b0fd2c5cd9c677567f8` | frozen sim provider metadata (F04) |

Copy fidelity: this attempt's `harness/run_d_matrix.py`, `run_case.py`,
`spy/sitecustomize.py`, `fixtures/HK-XIAOMI-2025.provider.json` re-hashed at binding time =
**byte-identical** to the pins above (recorded in binding.json).

Byte-identity constants (frozen; also I-07-D's `run_case.py IDENT` manifest values):

- HK-XIAOMI-2025 raw sha256 = `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c`
- HK-XIAOMI-2025 sidecar sha256 = `8228741d299164380bde36a83df1267b59e9b46721bea7d8efee857aeeb8da71`
- manifest raw name = `2026-04-28_hkexnews_12127452_2025年度報告.pdf`; canonical post-import
  name MAY differ (`…_小米集團－Ｗ 2025年度報告.pdf`) — I-07-B open item HK-3/D-3 carried.

## 2. Per-case frozen expectations (restate of I-07-D oracle §2/§3 — same harness, same argv)

Clause texts carried verbatim from I-07-D oracle §0 (exit + matrix L58): each triggered
point needs before-state, trigger (location + occurrence count ≥1), error evidence
(cause/code/retryability), after-clear retry deltas, recovery verdict — never "it threw".
F02–F06 scratch-only; no real production process termination / DB fault injection.

### F02 — point (c) scan错误 (raw提交后 scan 错误; HK-XIAOMI-2025, state2)

- Initial: raw+sidecar present (sha == `ffd73376…2da7c` / `8228741d…`), 0 registration rows.
- Injection: share-none `CreateFileW` hold on the cell raw across `cli scan`
  (scanner.py:964-976 → :1209).
- Expected: scan1 rc **0**, `scan_runs.status == completed_with_errors`, errors **==1**,
  `error_details[0].error` contains `PermissionError` (Errno 13) text on the raw PDF;
  follow-up entry (no `--allow-download`) refusal `not_found` + `not reusable` rc **3**,
  empty stdout (no consumable handle); hold window ⊃ scan1 (timing = record-only).
- Fault catalog delta shape = I-07-D's MEASURED shape (its recorded D-1 divergence:
  sidecar enumeration writes `documents+1 sources+1 locations+2 …` while raw unreadable —
  prediction miss recorded as model finding, row satisfied via non-reusable refusal).
- Recovery (holder released → same `cli scan`): scan2 rc **0**, `scan_runs.status ==
  completed`, registration `documents+1 locations+2 …`, **provider delta 0 both scans**,
  raw bytes unchanged; entry-after rc **3** refusal moves to review gate
  (`prompt injection not reviewed`).
- Verdict check-key set (14 keys, `all_ok=true`): trigger_scan_status_cwe,
  trigger_count_ge1, trigger_cause_text_recorded, fault_scan_rc0, hold_window_valid,
  raw_preserved, report_not_claiming_clean, nohandle_refusal, no_consumable_handle_at_fault,
  nohandle_zero_download, recovery_scan_rc0, recovery_scan_clean, recovery_usable,
  recovery_no_download, recovery_raw_unchanged; plus model_prediction_checks
  (`oracle_literal_zero_registration_rows_at_fault` = false, divergence recorded).

### F03 — point (d) DB事务内锁等待 (HK-XIAOMI-2025, state2, independent fresh cell)

- Injection: `lock_catalog.py` second connection `BEGIN EXCLUSIVE` on the CELL catalog
  75 s while product `BEGIN IMMEDIATE` under `busy_timeout=30000` ⇒ real in-transaction
  lock wait then `sqlite3.OperationalError("database is locked")` → catalog_busy.
- Expected: scan1 rc **1**, elapsed **≥25 s** (frozen gate; actual duration timing-only),
  stderr `{"error": "database is locked", "error_type": "catalog_busy", "retryable": true,
  "status": "failed"}`, stdout EMPTY, catalog delta **{}** (no partial write),
  `lock/hold.json` acquired-before / released-after the scan window; raw sha unchanged.
- Recovery (lock released → same `cli scan`): scan2 rc **0**, `documents+1 locations+2
  sources+2`, **provider delta 0 both runs**, raw unchanged.
- Verdict check-key set (11 keys, `all_ok=true`): trigger_rc1,
  trigger_lock_wait_elapsed_ge25, trigger_error_catalog_busy, lock_held_across_scan,
  no_partial_write_at_fault, fault_stdout_empty, raw_preserved, recovery_scan_rc0,
  recovery_registered, recovery_no_download, recovery_raw_unchanged.

### F04 — point (b) raw提交后scan前 (HK-XIAOMI-2025, state3: raw ABSENT initially)

- Injection: entry `--allow-download` + frozen sim provider (`I07D_FAULT=kill_before_scan`);
  spy barrier at `canonical_writer.py:185` (raw committed :181-184, scan not started):
  target self-registers `pid_<pid>.json` (argv contains cell config path AND cwd = cell
  cwroot) + `barrier_<pid>.json`; orchestrator kill gate (manifest ∧ path-in-argv ∧
  path-in-cwd ∧ alive) → `TerminateProcess(pid, 4242)`.
- Expected trigger: exactly 1 barrier + 1 pid manifest + kill ok, alive_after=false,
  released-marker absent (count 1). Kill ONLY the manifest-registered PID (clause5).
- Product error chain: kill visible as `…exited 4242…` → entry stderr
  `{"error_code":"upstream","error":…4242…}` rc **3**; stdout has NO record JSON.
- State at fault: raw COMMITTED at canonical path (content sha == `ffd73376…2da7c`;
  filename may differ from manifest — carried open item) + `<raw>.source.json` provenance
  present; catalog delta **{}** (no scan_runs row — scan never started).
- Recovery (NEW process `cli scan`, arm cleared): rc **0**, registers
  (`documents+1 locations+2 sources+2`), **provider delta 0 (不重下raw)**, raw sha intact;
  entry-after rc **3** at review gate with provider 0.
- Verdict check-key set (14 keys, `all_ok=true`): trigger_barrier_and_kill,
  kill_gate_path_ok, released_marker_absent, product_sees_kill_rc4242, entry_rc3,
  no_consumable_stdout, raw_committed_before_kill, provenance_committed,
  no_registration_at_fault, fault_download_happened, recovery_scan_rc0, recovery_registered,
  recovery_no_download, raw_intact_after_recovery, after_entry_usable_no_dl.

## 3. Comparison oracle — I-07-D decision transcribed values (frozen target values)

These are the authoritative recorded values of the LOST judged runs. Source = I-07-D
`decision.md` §2 verdict table rows F02/F03/F04 + §4 delta rows + §6 kill evidence +
`§7.1` (its F04-attempt-1 transcription, historical) and the `verdict.json` measured
fields, all pinned in §1. Re-run values are compared against THESE.

**F02 (decision §2 row F02 + §4 row + verdict.json 8d6e7a8b…):**
- scan1 rc `0` with `scan_runs.status=["completed_with_errors"]`, report `errors:1`,
  `error_details[0].error = "PermissionError: [Errno 13] Permission denied: '<cell raw path>'"`,
  `relative_path="小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf"`,
  `root_id="company_raw"`, count 1.
- hold record: `ok:true, label:"f02", share_mode:0, released_by:"release marker"`;
  (window `17:19:07.86→17:19:20.82`, `held_seconds 12.956` — TIMING, record-only).
- `fault_catalog_delta = {document_entities:1, documents:1, entities:1, locations:2,
  roots:1, scan_runs:1, sources:1}` (D-1 divergence shape, recorded in verdict).
- entry_nohandle rc `3`, refusal `not_found` + `source is not reusable` (decision text:
  `not_found / source is not reusable: missing / no_existing_source_satisfies_request`),
  stdout empty (no consumable handle).
- scan2 rc `0`, status `completed`, registrations `documents+1 locations+2 sources+2 …`;
  entry_after_recovery rc `3` at review gate (`prompt injection not reviewed`).
- `raw_rcs = {scan_fault:0, entry_nohandle:3, scan_recovery:0, entry_after_recovery:3}`;
  provider delta 0/0 both scans (新增下载0); raw sha `ffd73376…` unchanged throughout.
- verdict: `all_ok:true`, 15 checks true, `model_prediction_checks.oracle_literal_zero_registration_rows_at_fault:false`.

**F03 (decision §2 row F03 + §4 row + verdict.json 6f5b6e6f…):**
- scan1 rc `1`, `elapsed ≥25 s` (measured `34.515 s` — TIMING, record-only),
  `error_doc = {"error":"database is locked","error_type":"catalog_busy","retryable":true,
  "status":"failed"}`, stdout EMPTY, `catalog delta {}`.
- `lock/hold.json`: `hold_s 75.0`, `lock:"BEGIN EXCLUSIVE acquired (isolation-only target)"`,
  `ok:true`, locked_at ⊃ scan window ⊂ released (overlap_ok true);
  (timestamps `17:29:31.74 locked → 17:30:46.74 released` — TIMING).
- scan2 rc `0`, `documents+1 locations+2 sources+2`, provider 0/0, raw unchanged.
- `raw_rcs = {scan_fault:1, scan_recovery:0}`; verdict `all_ok:true`, 11 checks true.

**F04 (decision §2 row F04 + §6 + §4 row + verdict.json f043c080…):**
- run1 entry rc `3`, armed fault `kill_before_scan`, `counter provider delta ≥2 (sim
  discover+fetch)`, catalog delta `{}` at fault, raw committed + provenance present
  (content sha `ffd73376…`), kill_record `killed` count **1**, gate checks all true
  (`manifest_present, manifest_path_in_argv, manifest_path_in_cwd, alive_before true,
  alive_after false`), `released_marker_present:false`, `kill {ok:true, exit_code_set:4242}`,
  `timed_out:false`; manifest `point:"scan_catalog:after_raw_commit_before_registration"`,
  `armed:"kill_before_scan"`; stderr contains `4242` (product's own `…exited 4242…` chain);
  `raw_rcs = {entry_fault:3, scan_recovery:0, entry_after:3}`.
- scan2 rc `0`, `documents+1 locations+2 sources+2`, provider 0 (不重下raw), raw intact;
  entry_after rc `3`, provider 0.
- verdict `all_ok:true`, 14 checks true; `committed_raw_path` = cell
  `…\raw\financial_reports\annual\2026-04-28_hkexnews_12127452_小米集團－Ｗ 2025年度報告.pdf`
  (canonical filename ≠ manifest name — carried open item, content sha asserted).
- **§7.1 historical transcription (F04 attempt-1, NOT a re-run comparison target)**:
  `kill_record={killed:{}, timed_out:true, barrier_files_at_timeout:[]}` (TIMEOUT shape,
  barrier never fired, nothing killed) — carried for context only; this card re-runs the
  JUDGED (rebuilt-cell) execution whose values are the F04 block above.

## 4. Comparison rule (FROZEN BEFORE RUNNING)

Per parent dispatch: 「比较规则=§7.1 权威值的『不变量字段』比对——错误类/retryable/rc/delta
形态，非计时数」. Fault semantics may be timing-sensitive (notably F03 lock-wait duration and
F02 hold window), so:

1. **INVARIANT fields (gating — MATCH/DIVERGE per case):**
   (a) error class & cause text: F02 `PermissionError: [Errno 13] Permission denied` on the
   raw PDF + `completed_with_errors`; F03 `"database is locked"` +
   `error_type:"catalog_busy"` + `retryable:true` + `status:"failed"`; F04 kill marker
   `4242` inside the product's own error chain + `error_code:"upstream"`;
   (b) product rc table: F02 `{0,3,0,3}` · F03 `{1,0}` · F04 `{3,0,3}` (per §3 blocks);
   (c) delta SHAPES: provider deltas (F02: 0 fault / 0 recovery; F03: 0/0; F04: ≥1 sim at
   fault / 0 at recovery), registration deltas (recovery `documents+1 locations+2`,
   `sources+2`), fault registration delta (F02 = the recorded D-1 sidecar-enumeration
   shape; F03/F04 = `{}`), `raw_unchanged`/`raw sha == ffd73376…2da7c` everywhere;
   (d) verdict structure: identical check-key sets with every check true and
   `all_ok:true`, `model_prediction_checks` false for F02 (D-1 stays visible);
   (e) trigger proof shapes: hold record `ok:true share_mode:0 released_by:"release marker"`
   (F02); `hold.json` overlap + rc1 + elapsed ≥25 s (F03); barrier+manifest+kill
   `alive_after:false`, `released_marker_present:false`, `timed_out:false` (F04).
2. **TIMING/EPHEMERAL fields (record-only — never gate):** timestamps, hold windows and
   `held_seconds` (F02 ~12.956 s recorded), F03 lock-wait `scan_elapsed` (34.515 s
   recorded; only the frozen ≥25 s gate gates), PIDs, elapsed seconds, catalog run_id
   values, absolute `%TEMP%` paths (identical layout by construction), counts of
   processes in censuses. A divergence here is reported in the table as
   `MATCH(invariant)/timing-differs (recorded)` — honest, non-gating.
3. **Verdict per case:** `MATCH` iff every invariant field equals the §3 transcription.
   `DIVERGE` otherwise → recorded honestly, classified: (i) timing-family (non-gating),
   (ii) semantics-affecting (becomes a finding; the case may still be individually
   re-computable but the transcription link is annotated).
4. **Re-computability criterion (the point of D3):** a case verdict is
   **re-computable from preserved raws = YES** iff, with `%TEMP%\i07d` scratch ABSENT (or
   ignored), `run_d_matrix.py f0Xv` reads ONLY (i) this attempt's `evidence/cases/<CASE>/`
   evidence and (ii) this attempt's preserved raw bytes, and reproduces the verdict
   (`all_ok:true`, identical check values) — demonstrated by running the recompute with
   `TEMP` redirected to this attempt's preservation root. Otherwise NO (per case).

## 5. Preservation plan (§72 / REM-93 new rule — the point of D3)

> 证据留存政策新则（后续卡强制）：judged-run raw 必须入 attempt/evidence，%TEMP% 仅 scratch。

1. `%TEMP%\i07d\**` = SCRATCH ONLY (MAX_PATH isolation per build_iso.py rationale);
   every judged byte is copied INTO `ATT/evidence/preserved/` **in the same
   `%TEMP%-mirroring relative layout** `evidence/preserved/temp/i07d/cases/<CASE>/cwroot/…`
   so `TEMP=<ATT>/evidence/preserved/temp` makes the frozen harness recompute read the
   preserved tree instead of scratch.
2. Per case, preserved immediately after that case's driver run (before the next case):
   the whole cell `cwroot` judged surface = `companies/**` (raw PDF + `.source.json`
   provenance/sidecar) + `.source_catalog/catalog.sqlite3` (+`-wal`/`-shm` if non-empty)
   + `config/*.yaml`, and `initial_state.json`/`iso_snapshot` already in
   `evidence/cases/<CASE>/`. Harness transcripts (argv/stdout/stderr/evidence.json/
   scan_runs.json/hold records/state barrier+pid manifests/counters) are written by the
   verbatim harness directly into `ATT/evidence/cases/<CASE>/` (in-attempt by construction).
3. Every preserved file is inventoried with the §72 lesson-11 triplet
   `(sha256, version-domain, preservation-site)` in `evidence/raws_manifest.json` —
   version-domain = this re-run's cell (`a20260923-01` re-run of I-07-D F02/F03/F04
   judged semantics), preservation-site = the in-attempt path.
4. Byte-link to I-07-D's transcriptions: preserved raw sha256 must equal the manifest /
   I-07-D-recorded `ffd73376…2da7c` (and sidecar `8228741d…`) — that equality is the
   byte-link between my preserved bytes and I-07-D's §3 transcribed `raw sha` values.
5. If any case cannot be re-run because the harness needs deleted temp context → that
   case is recorded **BLOCKED-with-evidence** (never a fake pass). Frozen pre-check says
   the three cases need only: production sample assets (read-only copies from CW), the
   product source trees, and fresh scratch cells — all available; no deleted `%TEMP%`
   context is required (the lost tree is OUTPUT of the runs, not an input).

## 6. Ground rules (carried from I-07-D oracle §1, binding for this re-run)

R1 real entries only (frozen I-00-B argv forms, verbatim commands.json argv);
R2 scratch only — writes ⊆ `ATT/**` ∪ `%TEMP%\i07d\**`; production writes = 0; no git; no
network (F04 provider = frozen sim metadata); R3 product-isomorphic cells (product's own
`CatalogStore._initialize` + read-only production copies with recorded provenance);
R4 counters = count-on-entry spy (wprobe must prove zero-INSERT before judged runs);
R5 trigger-or-invalid (occurrence ≥1 + location, else BLOCKED, never a fake trigger);
R6 exit honesty (five evidence elements per cell). Kill scope (clause5): only
manifest-registered PIDs of this attempt's scratch tree; census before/after; no real
worker touched.

## 7. Reviewer attack list (frozen before results)

1. Re-hash preserved raw/sidecar of each case against `ffd73376…`/`8228741d…` and against
   `raws_manifest.json` triplets — the D3 core check.
2. Re-run `f02v`/`f03v`/`f04v` yourself with `TEMP=<ATT>/evidence/preserved/temp` after
   deleting/renaming any `%TEMP%\i07d` scratch: verdicts must recompute.
3. Attack trigger evidence: F02 hold window ∩ scan1 window; F03 lock overlap + elapsed;
   F04 barrier+manifest+kill gate checks and census (any killed PID not in a manifest
   invalidates everything).
4. Diff my transcripts against I-07-D's §3 transcriptions field by field (invariants vs
   timings per §4) and check the MATCH/DIVERGE table is honest both ways.
5. Verify this attempt wrote nothing outside `ATT/**` + `%TEMP%\i07d\**` (changes.diff =
   empty product-diff assertion + anchor re-hash).
