# I-07-D decision.md — 故障矩阵与断点恢复 (F01–F06)

Card `PLAN/execution_v2/card_I-07-D.md` (sha256 `b54f4bc8…2c553`) · Attempt
`a20260923-01` · Owner face 独立故障验收者 (review follows separately; implementer
never signs acceptance).

## 0. Exit rule (binding, verbatim) and how this attempt answers it

> 退出：「每个触发点有前后状态、错误与恢复证据；不能以单一"抛了异常"通过。
> 无可靠注入能力先 blocked。」
> matrix L58（逐字）：「F02—F06均仅scratch执行。不得使用真实生产进程终止/DB故障注入。
> 每个变体必须有实际触发位置证据，没触发不算"负例通过"。」

Every one of the six clause-2 injection points **fired** (occurrence count ≥1, location
recorded) and every cell carries before-state / trigger / error evidence /
after-clear retry deltas / recovery verdict — no cell passes on "it threw".
**BLOCKED cells: none** (every injection point proved reachable with scratch-only
tools: adapter-config fixture, share-none file hold, second-connection DB lock,
registered-PID barriers, harness err-hooks). Killed PIDs: only this attempt's
manifest-registered processes; census diff shows **0 real source_catalog processes
gone** (`evidence/census_diff.json: real_source_catalog_gone=0`).

## 1. Inputs (frozen pins; full list `evidence/input_pins_raw.txt`)

| input | sha256 (prefix) |
|---|---|
| matrix `execution_v2/scenario_matrix.md` (F01–F06 = L47–58) | `0dec23cd…` (same pin as I-07-B/I-07-C) |
| card_I-07-D.md | `b54f4bc8…` |
| card_I-09-C.md (primary dedicated oracle, P-C1..P-C5 fault table) | `59e9d71d…` |
| I-09-C oracle.md (F1–F12 fault table transcribed + rc semantics) | `ccd1ea51…` |
| I-09-A decision.md §7 (F-table origin) / oracle / addendum | `94a27b8a…` / `d7f6b102…` / `de7fa1f3…` |
| card_I-04-E.md (HTTP403 semantics: upstream code/retryable preserved verbatim) | `9f98b194…` |
| I-07-B oracle.md + handoff (REGFAIL/catalog_busy precedent, spy wiring) | `b92b6650…` / `e43cf258…` |
| I-00-B binding/commands/oracle (argv contract) | `fdb2a598…` / `f8a397ec…` / `e9c82fe4…` |
| sample_manifest.json | `d5d0bb92…` |
| this attempt's oracle.md (frozen BEFORE first judged run) | `576ddfc57c2c949d6a9e5f875114d8c7e49c833d69b5bd8cd81bcf2417718846` (27211 B) |

卡面六点↔F 行对照 (frozen in oracle §0.1): (a)provider=F01 · (b)raw后scan前=F04 ·
(c)scan错误=F02 · (d)事务锁等待=F03 · (e)producer=F05 · (f)发布边界=F06 (three
sub-boundaries). scenario_matrix L60-64 cross-scenarios = I-07-E/I-13 scope, not this
card (parent ruling carried).

## 2. F01–F06 verdict table (the card's clause-5 exit face)

| cell | before-state | trigger (location + occurrence count) | error evidence (cause/code/retryability) | after-clear retry deltas (from ORIGINAL entry) | recovery verdict |
|---|---|---|---|---|---|
| **F01** (a) provider返回 · CN · all_ok=**true** | fresh cell state3: raw ABSENT, 0 registration rows; cell `source_acquisition.yaml` cn command → scratch fixture `fixture_403_adapter.py` (product's own json_command_v1 config seam) | `adapter_process.py:155-178` (rc≠0 → structured stderr parse). fixture_log: **fetch=1, discover=1 inside run1 window** (frozen bound 1..3; total 3 across the 3 chain-capture runs, 1 per run); spy provider delta 2/2/2 per fault run | origin: fixture stderr `{"code":"http_403","retryable":true,"message":"HTTP 403 Forbidden from provider (frozen I-07-D fault fixture)"}` → wiki stderr `{"error":…403…,"error_type":"fatal","retryable":false,"status":"failed"}` → FF stdout envelope `{status:"fatal","error_code":"fatal","retryable":false,"stage":"ensure","attempts":1,"calls":3,"downloads":0,"error":"…http_403…"}` rc2 → client stderr `{"error_code":"fatal","error":"filing-fetch exited 2: …http_403…","retryable":false}` rc2 → entry stderr `{"error_code":"upstream","error":"filing-fetch client exited 2: …http_403…"}` rc3. **`http_403` + `retryable:true` survive at hops 1→2→3→4→5 verbatim (text)**; the top-level `retryable` is re-derived false (403 ∉ filing-contracts retry set — recorded, not hidden) | fault run: downloads **0** (raw stayed absent, catalog delta {}), provider CALLS ≥1 (trigger) · recovery (fault cleared, frozen-sim provider): provider +1, raw lands sha256=`01819e1c…f343d` (manifest match), registration documents+1 locations+2 sources+2 roots+1 scan_runs+1, then review-gate refusal (`not_reviewed`) rc3 — **gap stays visible, never claimed “无缺口”** | **PASS** (row expectations + clause3/4 met; see §5 findings for the retryable re-derivation observation) |
| **F02** (c) scan错误 · HK · all_ok=**true** (+1 prediction divergence) | fresh state2: raw+sidecar present (sha `ffd73376…`), 0 registration rows | **share-none CreateFileW hold on the raw during `cli scan`** → `scanner.py:964-976` per-file `except OSError` → `scanner.py:1209`. scan_runs.status=**`completed_with_errors`**, report `errors:1`, `error_details[0].error="PermissionError: [Errno 13] Permission denied: '…年度報告.pdf'"` — **count 1**; hold window 17:19:07.86→17:19:20.82 (12.956 s) ⊃ scan1 (17:19:07.99→17:19:20.46) | report/scan_runs carry the cause text end-to-end (PermissionError quoted above); product rc0 with a report that **discloses errors=1** (no looks-fine claim); follow-up entry rc3 `not_found / source is not reusable: missing / no_existing_source_satisfies_request` — **no consumable handle** | fault: provider 0 (no download ever) · recovery (holder released → same registration entry `cli scan`): rc0, `scan_runs.status=completed` (errors 0), registrations land (documents+1 locations+2 …), **provider delta 0 both scans (新增下载0)**, raw bytes unchanged; entry after → refusal moves to review gate (chain past 資格 ⇒ usable) | **PASS** + recorded prediction divergence (see §5 D-1: sidecar enumeration writes rows while raw unreadable, but the source stays non-reusable ⇒ matrix row satisfied) |
| **F03** (d) DB事务内锁等待 · HK · all_ok=**true** | fresh state2 (independent cell, no F02 state reused — per-cell initial_state.json) | second connection `BEGIN EXCLUSIVE` on the CELL catalog (hold 75 s, I-07-B REGFAIL technique) while product writes via BEGIN IMMEDIATE under `busy_timeout=30000` (`store.py:990/:994/:1018`). **in-transaction lock wait = 34.515 s** then failure; hold.json locked_at 17:29:31.74 ⊃ scan window, released 17:30:46.74; **count 1** | scan1 raw rc **1**, stderr `{"error": "database is locked", "error_type": "catalog_busy", "retryable": true, "status": "failed"}` (product's `error_taxonomy` emission), stdout EMPTY, catalog delta **{}** (no partial write) | fault: provider 0 · recovery (lock released → same `cli scan`): rc0, registrations documents+1 locations+2 sources+2, **provider delta 0 (释放锁后幂等恢复，不重下raw)**, raw sha unchanged | **PASS** (elapsed≥25 s proves the wait was a real lock-wait, not an instant error) |
| **F04** (b) raw提交后scan前 · HK · all_ok=**true** | fresh state3: raw ABSENT; entry armed `I07D_FAULT=kill_before_scan` + frozen-sim provider | spy barrier at `canonical_writer.py:185` call boundary (raw committed L181–184, scan body not started): process self-registers `pid_42124.json` (argv contains cell config path AND cwd = cell cwroot) + `barrier_42124.json`; orchestrator gate (manifest ∧ path-in-argv ∧ path-in-cwd ∧ alive) → `TerminateProcess(42124, 4242)`; post: alive_after=**false**, released-marker absent → **count 1** | the product itself reports the kill: chain error `…exited 4242…` surfaces as entry stderr `{"error_code":"upstream","error":…4242…}` rc3; stdout has no record (no半合格handle); catalog delta **{}** at fault (scan never started — no scan_runs row) | raw COMMITTED before kill: canonical-path file (filename ≠ manifest — I-07-B open item, content sha256 = `ffd73376…2da7c` ✓) + `.source.json` provenance ✓ · recovery (NEW process `cli scan`): rc0 registers (documents+1 locations+2 sources+2), **provider delta 0 (不重下raw)**, raw sha intact; entry-after rc3 at review gate with provider 0 | **PASS** |
| **F05** (e) producer执行 · CN · all_ok=**true** (+cause finding) | fresh state2 → product `cli scan` registers doc → production_observation_copy of the `normalized` artifacts row + derived `normalized.md` (sha verified, paths relocated), **summary ABSENT by construction** (`evidence/cases/F05/f05_seed.json`) | share-none hold on the CELL `normalized.md` during `cli summarize` → `summarizer.py:165` `read_text` raises → `:168-170` `failed+=1`. ProcessingReport fault = **`{operation:"summarize", completed:0, failed:1, …}`**, `summary` artifacts row 0, `summary.md` absent, `normalized` row+file byte-identical; spy producer delta 1; hold 1.744 s ⊃ run; **count 1** | report discloses failed=1 (rc0 but no success claim — not pseudo-qualified). **cause-survival = FAIL → finding F-F05-cause**: `summarizer.py:168` swallows the OSError with `except (OSError, UnicodeError): failed += 1` — no error text/code/retryability is persisted anywhere (pre-registered risk in oracle §2/§7; NOT hidden, NOT treated as pass) | fault: provider 0 · recovery (lock released → SAME entry `cli summarize`): report **`completed:1, failed:0`**, artifacts **summary +1 only**, `producer_events` +1 (summary), **normalize NOT called (producer calls: fault=1, recovery=1 — no rebuild)**, normalized row sha+created_at unchanged, provider 0. Single variable between runs = the lock | **PASS** on row/clause3-no-伪合格/clause4; **clause3 cause-preservation FAIL recorded as product finding F-F05-cause** (owner: CW producer track) |
| **F06A** (f) registry边界 · all_ok=**false** (kept red) | seed P0 clean publish rc0 → fresh reader: P0 consumable, P1 rows 0, chain ok | harness err-hook at `publication_registry.py:_append` entry (before any byte): real OSError `I-07-D injected registry failure`; hook_trace `err_raised op=append_registry` **count 1**; marker in writer stderr ✓ | writer raw rc **2** (product `error: [Errno 13] …registry failure` line — plain text, production has no JSON envelope on this path, recorded as measured); registry P1 rows **0**; P1 json/markdown **absent** (registration precedes writes) — reader: p1 consumable **false**, p0 consumable **true**, chain ok; no mixed package; no tmp | recoveries (clean publish same P1 input): rc0/rc0, p1 consumable true, rows seed **1 → rec2 3** (append-only +1+1, **history never deleted**), p0 json/md sha byte-identical across seed→rec2, chain ok, `audit` problems = ONLY the F-F06-audit false positives (no conflict:/corruption lines ⇒ same-input reruns produced **no result-hash conflict**) | row expectations PASS; **cells stay RED on frozen `audit_problems==0`** because of product finding **F-F06-audit** (§5) — I-09-C F12 precedent: no re-gating to green |
| **F06B** (f) 第二输出文件边界 · all_ok=**false** (kept red) | same seed pattern (fresh registry+state) | err-hook at `revenue_forecast.py:_atomic_write_text` **2nd member** (`err:replace:output_markdown`): real OSError; hook_trace `err_raised op=replace role=output_markdown` **count 1**; marker in stderr ✓ | writer rc **2**; registry P1 row **+1** (appended before members, by production order), json member **present**, markdown member **absent**; fresh reader: p1 rows_for_input=1, json_exists=true, md_exists=false, **consumable=false (不见可消费半发布)**, `is_registered(p1)=true` (ordering disclosed), p0 consumable, audit-with-p1 shows only the F-F06-audit false positives | recovery rc0 ×2: markdown written, p1 consumable true, rows seed **1 → 4** (+1 fault row stays, +1+1 recoveries, append-only), p0 intact, chain ok | row expectations PASS; RED on **F-F06-audit** only |
| **F06C** (f) commit边界 · all_ok=**false** (kept red) | same seed pattern | kill barrier at `revenue_forecast.py:main return:before` (after both members durable, before caller ack): writer self-registers pid manifest (argv+cwd inside ATT) → gate passes → `TerminateProcess(pid,4242)`; hook_trace `return:before` **count 1**; killed=true; **fault writer exit record ABSENT** (clean runs' exit records listed separately); no stdout ack | writer raw rc **4242** (kill marker); after-state: registry P1 row + BOTH members durable/verified → fresh reader p1 consumable **true** (complete, never half), p0 consumable, chain ok; caller received nothing | recovery rc0 ×2, is_registered stays true, no conflict (audit problems only the F-F06-audit false positives), rows seed **1 → 4** append-only, members atomically replaced with identical hashes, p0 byte-identical | row expectations PASS; RED on **F-F06-audit** only |

Aggregate (`evidence/verdicts.json`): **trigger counts F01=1 F02=1 F03=1 F04=1 F05=1
F06A=1 F06B=1 F06C=1 · blocked=[] · all_ok=false (sole red cause: F-F06-audit on the
three F06 cells)**.

## 3. clause-3 pseudo-qualified proofs (best three, with full error chains)

1. **F01 — nothing consumable at fault, cause chain intact 5 hops.** Fault entry
   stdout = EMPTY (no `reuse_receipt`/`source_id`/`resolution_envelope` marker;
   `stdout_has_consumable_record=false`), raw ABSENT (no fake raw: `raw_sha_before=None,
   raw_sha_after=None`, catalog documents/locations delta {}), downloads 0 — while the
   fixture log proves the fault really fired. The error chain, quoted end-to-end from
   raw files: origin fixture stderr (`http_403`/`retryable:true`/message) → wiki cli
   stderr (same 403 JSON embedded, `error_type:"fatal"`) → `fetch_filing` stdout
   envelope (`stage:"ensure", attempts:1, calls:3, downloads:0`, full 403 text in
   `error`) → client stderr doc (`error_code`, `retryable`, full text) → entry stderr
   (`error_code:"upstream"`, client doc embedded). Evidence:
   `evidence/cases/F01/run{1..4}*/{stdout,stderr}.txt` + `fixture_log.jsonl`.
2. **F02 — scan reports failure honestly; registered-but-unusable never becomes a
   handle.** `cli scan` rc0 but `scan_runs.status=completed_with_errors` with
   `error_details=[{error:"PermissionError: …年度報告.pdf", relative_path, …}]`
   (cause text preserved into `scan_runs.report_json`), and the follow-up entry
   refuses `not_found / source is not reusable` (rc3, empty stdout) — i.e. no
   consumable handle even though sidecar enumeration wrote rows; after clearing the
   fault the SAME entry moves past 資格 to the review gate, proving the difference is
   the fault, not the request.
3. **F06B — half-published package is visible as files but NOT consumable.** At the
   fault: registry row exists + json exists + markdown missing; independent fresh
   reader computes `consumable=false` (member completeness fails) while p0 stays
   consumable and the chain verifies — no state where a consumer can take the new
   package as complete; recoveries then complete it idempotently (audit shows zero
   `conflict:` lines — same deterministic `result_sha256`).

## 4. clause-4 delta accounting (measured; masking rule honored)

Recovery always re-issued ONLY the original faulted entry (no bulk rebuild anywhere):

| cell | metric | fault phase | recovery phase |
|---|---|---|---|
| F01 | provider calls / downloads / registrations | 2 calls (discover+fetch) / **0 downloads** / **0 rows** | +2 calls (sim discover+fetch) / **+1 download** (sha ok) / documents+1 locations+2 sources+2 roots+1, then review refusal (gap visible) |
| F02 | provider calls (fault scan, no-handle entry, recovery scan, after entry) | **0 / 0** | **0 / 0** (registration-only recovery, 新增下载0) |
| F03 | provider calls | **0** (lock; delta {}) | **0**, registrations land |
| F04 | provider / raw / registration | +2 (sim discover+fetch), raw committed, **0 rows** (killed pre-scan) | **provider 0**, raw sha unchanged, registrations land |
| F05 | producer calls / artifact rows / files | summarize **1 call**, summary **+0**, normalized unchanged | summarize **+1 only**, **normalize +0**, summary **+1 only** (+producer_events +1), provider 0 |
| F06A/B/C | registry rows / members / history | A: +0 rows, no members · B: +1 row, json only · C: +1 row, both members | rc0×2; rows append-only 1→3 (A) / 1→4 (B,C); **no history deletion**; p0 byte-identical; no result-hash conflict; members hash-identical |

Masking exposure: had recovery rebuilt everything, per-counter deltas would have shown
re-download (F02/F03/F04 provider>0) or role re-production (F05 normalize>0 / normalized
row churn) — none occurred; conversely F01's recovery download is EXACTLY the authorized
frozen-sim re-fetch after a zero-download fault (never claimed “无缺口”: the review-gate
refusal still stands).

## 5. Findings (recorded, never absorbed)

- **F-F06-audit (PRODUCT, OPEN, keeps F06A/B/C red).** `scripts/publication_registry.py:229`
  — `if not isinstance(claimed, str) or claimed not in by_generation:` tests a STRING
  against dict keys that are TUPLES (typed L207, unpacked L216): membership can never
  match ⇒ `audit()` reports `unregistered claim … never registered` for EVERY result
  file, directly contradicted in the same fresh reader process by
  `is_registered(p0)=true / is_registered(p1)=true` (and `registry_path_match=true`,
  `chain.ok=true`). Intended check must be anchor-level. Consequence for this card:
  frozen `audit_problems==0` unmet ⇒ three F06 cells stay red (I-09-C F12 precedent —
  no retry-to-green, no re-gating); all OTHER F06 row expectations measured PASS and
  are listed per cell above. Route: owner / publication-registry track.
- **F-F05-cause (PRODUCT, OPEN).** `company-wiki summarizer.py:168` swallows
  `OSError` (`failed += 1; continue`) without persisting cause/code/retryability
  anywhere (report carries counts only) — clause-3 cause-survival FAIL at the F05
  origin. Trigger/recovery evidence itself is complete (hold window + single-variable
  control: fault `failed:1` vs recovery `completed:1`). Route: CW producer track.
- **D-1 (model-prediction divergence, F02, non-gating, disclosed in the cell verdict).**
  Oracle §2 mechanism prediction “documents/locations delta 0 at fault” MISSED: with the
  raw unreadable, the product still enumerates the sidecar and writes rows
  (documents+1 sources+1 locations+2) — but the source is **non-reusable**, so the
  entry refuses `not_found` and the matrix row's binding expectation (原件保留/注册阶段
  失败/不返回可消费handle) holds from the consumer's view. Per the oracle's own rule this
  is a finding about the model, not a rewrite of the oracle; the literal check is kept
  in `verdict.json.model_prediction_checks=false`.
- **D-2 (observation, F01).** Upstream `retryable:true` survives verbatim as TEXT in
  every hop, but each layer RE-DERIVES its top-level `retryable` from its own code set
  (filing-contracts retry set has no http_403 ⇒ false at FF/client) and `error_type`
  maps to `fatal`. Consistent with I-02/I-04-E contracts (upstream fields preserved
  verbatim; outer classification independent) — recorded, not judged as loss.
- **D-3 (carried open item, F04).** Canonical filename after import
  (`…_小米集團－Ｗ 2025年度報告.pdf`) differs from the manifest name
  (`…_12127452_2025年度報告.pdf`) — the SAME open item I-07-B recorded (HK-3); content
  sha256 asserted against the manifest value; recorded, not fixed here.
- **D-4 (observation, F01).** `close_gap` did NOT internally retry to 3 despite
  upstream `retryable:true` (measured attempts=1 per run; envelope `calls:3`) — within
  the frozen 1..3 bound; noted for the retry-budget owner.

## 6. clause-5 kill/PID scoping evidence

- Kills executed: **F04 pid 42124** (wiki child) and **F06C writer pid** (barrier
  `barrier_*.json` + self-written `pid_*.json` manifest). Gate (both): manifest present
  ∧ path-substring in manifest argv **and** cwd ∧ alive-before ⇒ `TerminateProcess(…,
  4242)`; after: alive=false; released/fault-writer-exit marker ABSENT (real death);
  F04's kill is corroborated by the product itself (`…exited 4242` in the entry error
  chain).
- F04 first attempt: gate failed (writer/wiki manifest lacked `cwd`/`argv` keys —
  harness bug) and only the launcher was killed as fallback; **no unregistered PID was
  ever killed** (gate failure ⇒ NOT killed, recorded in `gate_failed_not_killed`).
  Manifest fields fixed (writer.py now records `argv`+`cwd`); F04 cell rebuilt fresh
  and re-run. Supersession disclosure §7.
- Census: before 359 processes → after 349; **gone=25, real source_catalog gone=0**
  (`evidence/census_diff.json`) — every gone PID is either a transient child of this
  attempt or unrelated churn; **no real worker was touched or killed**; worker-pattern
  scan at start found no running source_catalog worker to begin with
  (`evidence/process_census_before.json`).
- No cell ever targeted a production DB: F03's `BEGIN EXCLUSIVE` was opened on
  `%TEMP%\i07d\cases\F03\cwroot\.source_catalog\catalog.sqlite3` only (hold.json
  records the path); production catalog main file bytes+mtime identical before/after.

## 7. Supersession / harness-fix disclosures (transparent, not hidden)

1. **F04 attempt-1 evidence overwritten.** The first F04 execution revealed the
   stale-binding bypass (see below); its evidence dirs were deleted before the corrected
   re-run instead of being preserved as `*.pre_*` (deviation from the retention
   precedent — recorded here because the original bytes are unrecoverable). Transcribed
   values from the attempt-1 records: `kill_record={killed:{}, timed_out:true,
   barrier_files_at_timeout:[]}`, wiring.json had NO `scan_catalog_barrier` entry,
   run1 counters `{provider:2, read:4}` with NO scan event, run1 registration COMPLETED
   (documents+1 locations+2 sources+2 scan_runs+1) and entry refused at the review gate
   — root cause: `canonical_writer` holds its own module-global binding of
   `scan_catalog` captured before/aside the spy's scanner-module wrap, so the direct
   canonical-import scan at `canonical_writer.py:185` never reached the wrapper (no
   count, no barrier). Fix: the spy now also wraps `canonical_writer.scan_catalog`
   (count + armed barrier). Cell rebuilt from scratch (state3) and re-run clean.
2. **F06C attempt-1 preserved** under `evidence/cases/F06C/*.pre_gate_fix` (gate-failed
   run: launcher killed as fallback, fault-writer NOT killed through the gate); rerun
   with fixed manifest passes the gate (`killed:true`).
3. **Verdict-only recomputes (harness logic fixes, product evidence untouched):**
   F01 `f01v` (stat-at-verdict-time → evidence-based raw-absence checks; true run-window
   attribution for the 1..3 fetch bound), F02 `f02v` (hold loaded from
   `hold_record_f02.json`; status read from `scan_runs` table; `after` run captured),
   F03/F05/F06 verdict recomputes from persisted evidence files. No product run was
   repeated to change a verdict (F01/F02/F03/F05 product runs each executed once —
   except F04's disclosed rebuild and F06C's disclosed rerun).
4. Two early driver crashes left no verdicts (F02 first attempt crashed on hashing a
   holder-locked raw before scan1 evidence was written; holder cleaned, raw re-hashed
   `ffd73376…` unchanged, state dir reset, run re-executed) — recorded as harness
   incidents with the lock released and no product state polluted (cell had produced
   nothing yet).

## 8. Before/after hashes (production untouched)

- `evidence/snapshot_before.json` vs `snapshot_after.json`: **26/26 anchors identical**
  (changed=[]), 3/3 sample raw+sidecar `all_match=true` both sides
  (`evidence/snapshot_verdict.json`: anchors_identical=true, samples_identical=true).
- `changes.diff`: `anchors_identical: 20, anchors_changed: []`; production catalog main
  `bytes=49677344768, mtime_ns=1789799495406919100` identical before/after; `-wal`
  bytes+mtime identical; **only `-shm` mtime changed (bytes 32768 unchanged)** —
  disclosed as the read-only WAL reader-attachment side effect (every open used
  `mode=ro` + `PRAGMA query_only=ON`; zero data writes).
- Product writes by this attempt: **0** (RF/CW/FF trees byte-identical; isolated config
  diffs only, listed in changes.diff; all case state under `%TEMP%\i07d\cases` +
  attempt dir).

## 9. Missing inputs / inherited notes / stop conditions

- **Missing inputs: NONE.** Matrix found and pinned (`scenario_matrix.md` L47–58,
  sha `0dec23cd…`, corroborated by the parent's transcription). Per-card oracles
  consumed: I-09-C card+oracle (F-table via I-09-A §7 + addendum), I-04-E (403
  semantics), I-07-B (REGFAIL/catalog_busy + spy wiring + F1/F2/F3 carries), I-00-B
  (argv contract). No cell required BLOCKED-with-evidence status.
- **Inherited carries still open upstream** (not this card's surface): I-07-B F1
  (entry never scans — registration is `cli scan` only; F04's recovery uses `cli scan`
  exactly because of this), F2 (refusals lack structured actionable-recovery), F3
  (no review CLI ⇒ no RevenueSourceRecord; F01/F02/F04 entry-after refusals all land
  at `not_reviewed`), I-09-C F12/F5, I-07-B J6 anchor drift (this binding uses current
  hashes), production I-16/I-17 pending, disclosure_adaptation=unmapped,
  accuracy=unproven.
- **Stop conditions:** none triggered — no kill outside a manifest gate; no production
  write; no git; no network (all provider traffic = local fixture/frozen sim); no real
  worker touched (census proof).
- **Unverified/limits:** F06 reader independence rests on THIS card's recompute
  implementation (fresh process, own canonical_sha256 call — not re-derived by a
  reviewer yet); F01 fixture candidate fields were lifted from production metadata
  observation (I-07-B dump), not re-validated against a live provider (C level only);
  F05 normalized row copy path-relocation was asserted by seed evidence but the
  row's byte-level schema equality vs production is asserted only via
  content_sha256+row dict in `f05_seed.json`; share-none holds rely on Win32
  CreateFileW semantics (observed working: PermissionError raised in the product).

## 10. Disposition

status = **review_pending** (implementer never signs). First unfinished action =
independent review: re-run any cell via `commands.json` driver ids, attack
`oracle.md §8` items (rehash a cell raw; read `harness/spy/sitecustomize.py` +
`harness/d_hooks.py`; recompute F02 hold-window ∩ scan1; kill-gate audit of
F04/F06C manifests + census; diff the F01 five-hop chain; recompute F05 deltas),
then rule on (i) the three red F06 cells w.r.t. F-F06-audit (blocking vs
non-blocking, per I-09-C F12 precedent) and (ii) F-F05-cause routing.

---

## FR-1 erratum (landing)

Recorded at carrier landing under reviewer finding **FR-1 (P2, disclosure accuracy —
landing condition)**, source `reviewer_report.md` (sha256
`1a1d1c0500e959012888a6c9f2d367d51412d6532a2822c813869eb08ac9a933`) §5/§8/§9. This is an
**erratum-style gap marker**: §6's original text above is retained **untouched** — nothing
is silently rewritten.

1. **§6's F04-attempt-1 paragraph MIS-ATTRIBUTES F06C-attempt-1 mechanics.** The account
   in §6 ("gate failed … only the launcher was killed as fallback … recorded in
   `gate_failed_not_killed` … Manifest fields fixed (writer.py now records `argv`+`cwd`)")
   describes **F06C attempt-1**, not F04 attempt-1. The gate-failed + launcher-kill +
   `writer.py`-manifest story belongs to F06C: the sole raw `gate_failed_not_killed`
   record anywhere in this attempt is
   `evidence/cases/F06C/fault_writer.pre_gate_fix/result.json`
   (`gate_failed_not_killed=[{pid:44784, checks:{argv:false, cwd:false}}]` +
   `launcher_kill={pid:49348, 4242}`), and `writer.py` does not appear anywhere in F04's
   execution path.
2. **§7.1's transcription is authoritative for F04 attempt-1**:
   `{killed:{}, timed_out:true, barrier_files_at_timeout:[]}` — a TIMEOUT shape: the
   barrier **never fired** and **nothing was killed**. **No `gate_failed_not_killed`
   record exists for F04** — zero F04 gate-fail records survive (confirmed absent by the
   reviewer's §5 search).
3. **F04 attempt-1 bytes are unrecoverable** — disclosed overwrite (§7.1): its evidence
   dirs were deleted before the corrected re-run; the original values were **transcribed
   into §7.1 at execution time** and that transcription is the only surviving account.
4. The **rebuilt F04 cell is internally consistent and unaffected** by this erratum — the
   reviewer independently verified the kill-gate checks 4/4 true, counters
   `{provider:2, scan:1}`, the 4242 kill visible in the product's own error chain, and the
   recovery deltas (provider 0, registrations land, raw+provenance intact, entry-after
   rc3). The `gate_failed_not_killed` record for F04 is confirmed ABSENT; this gap marker
   says so explicitly.

## FR-2 annotation (landing)

Reviewer finding **FR-2 (P3, claim precision)**. Original claim in §8 above is **retained
as superseded-with-note**, not rewritten.

- Cause: `harness/snapshot.py` computed the 6 plan anchors under `ATT.parents[1]`
  (= `execution_runs`) instead of `parents[2]` (= the PLAN root), so those 6 plan anchors
  are `missing:true` in **BOTH** snapshots.
- Therefore the earlier "26/26 anchors identical" claim = **20 hashed anchors + 6
  missing==missing (vacuous)**; it is superseded by this note.
- The honest count = `changes.diff`'s `anchors_identical=20`.
- **Reviewer's correction figure: independently re-hashed all 26 intended files at the
  corrected paths = 0 mismatches (6/6 match their binding/input_pins)** ⇒ landed wording
  "20 hashed + 6 pin-verified by reviewer". Product-untouched conclusion stands (0 product
  anchor changed).

## FR-3 annotation (landing)

Reviewer finding **FR-3 (P3, transcription)**. The handoff's `exit_declaration_verbatim`
deviates from the card by **one ASCII space** in its final clause: card
`execution_v2/card_I-07-D.md` L14 records 「…无可靠注入能力**先blocked**。」 while the
handoff string reads 「…无可靠注入能力**先 blocked**。」 (one ASCII space, handoff form
first: `先 blocked` vs card `先blocked`). The first quoted sentence (「每个触发点有前后
状态、错误与恢复证据；不能以单一“抛了异常”通过。」) is **byte-exact**, and
`matrix_l58_rule_verbatim` == scenario_matrix **L58 byte-exact**. The verbatim declaration
inside `handoff.json` is **NOT altered** — it is what the card recorded at execution; only
this note records that the intended card form differs from that recorded string by that
single ASCII space.

## FR-4 annotation (landing)

Reviewer finding **FR-4 (info, wording)**. `oracle.md` §4's F01 recovery cell (line 298)
reads "**+1 sim fetch / +1 download**" while the **measured** provider delta is **+2**
(1 sim discover + 1 sim fetch); `decision.md` §4 reports it honestly as "+2 calls (sim
discover+fetch)". Downloads are exactly **+1** as frozen. Wording ambiguity only, no
masking. **The oracle is untouched (frozen-first preserved)** — annotation lives in
decision.md only.
