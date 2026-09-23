# I-07-D oracle.md — FROZEN BEFORE ANY JUDGED RUN

Card: `PLAN/execution_v2/card_I-07-D.md` (sha256 `b54f4bc8…2c553`, 1295 B) — 故障矩阵与断点恢复.
Attempt: `a20260923-01`. Frozen: 2026-09-23 (local), after code-map reading (step 3) and
BEFORE the first run of any judged product entry by this attempt. No expected value below
was produced by running the tooling under test; case identities come from
`execution_v2/scenario_matrix.md` (sha256 `0dec23cd10f00efd6ad82cf923552bd46c1763bcf9f7404
22f51f4973292299f`, verified) and operational facts about product behavior come from
READ-ONLY source reads + the accepted gate runs (I-07-B/I-09-C/I-00-B), never from an
outcome of the runs this oracle governs.

## 0. Binding texts (verbatim; exit + boundaries)

- 退出（card 逐字）：「每个触发点有前后状态、错误与恢复证据；不能以单一“抛了异常”通过。
  无可靠注入能力先 blocked。」
- 条款1：「每个故障单独attempt，恢复初始隔离状态，避免前一个case污染后一个。」
- 条款2：「分别在provider返回、raw提交后scan前、scan错误、DB事务内锁等待、producer执行、
  发布提交边界注入；记录实际触发位置和发生次数，没触发的测试无效。」
- 条款3：「检查失败时没有可消费的伪合格结果；已有raw保留，错误cause/code/retryability不丢失。」
- 条款4：「清除故障后从原入口重试；比对新增下载/写入/调用数，不能靠重建全部资产掩盖幂等缺陷。」
- 条款5：「杀进程只针对本case记录PID，确认进程归属隔离树；不操作真实worker。」
- matrix L58（逐字）：「F02—F06均仅scratch执行。不得使用真实生产进程终止/DB故障注入。
  每个变体必须有实际触发位置证据，没触发不算“负例通过”。」
- 输入冻结：matrix F01–F06 六行（L49–56）+ 各专属卡 oracle（见 binding.json input_pins：
  I-09-C card/oracle、I-09-A F-table + addendum、I-04-E 403 语义、I-07-B REGFAIL/wiring、
  I-00-B argv 契约）。与本卡行义冲突时以 scenario_matrix 本表为准（父方裁定照录）。

### 0.1 卡面六注入点 ↔ F 行对照（在 oracle 冻结时固化）

| 卡面点 (clause2) | matrix 行 | 注入对象 |
|---|---|---|
| (a) provider返回 | **F01** | provider HTTP403，C 级，离线 fixture |
| (b) raw提交后scan前 | **F04** | 隔离进程 raw 提交后、scan 注册前终止 |
| (c) scan错误 | **F02** | scan 返回 completed_with_errors |
| (d) DB事务内锁等待 | **F03** | 独立连接持 DB 写锁（产品 BEGIN IMMEDIATE 等待） |
| (e) producer执行 | **F05** | producer 失败/只完成部分角色 |
| (f) 发布提交边界 | **F06** | registry / 第二输出文件 / commit 边界分别失败（三个子边界） |

scenario_matrix L60-64 交叉场景 = I-07-E/I-13 卡面，不在本卡（父方边界注记照录）。

## 1. Ground rules (frozen)

- **R1 Real entries only.** Judged runs use the frozen I-00-B argv forms (binding.json
  cwd_and_argv_contract). No helper substitutes for the entry. cwd = attempt dir for entry
  runs, cell cwroot for cli runs, iso/rf for publication writer runs.
- **R2 Scratch only.** Writes ⊆ ATT/** ∪ %TEMP%\i07d\**. Production writes = 0. No git.
  No network (provider served by local fixtures/frozen sim only).
- **R3 Product-isomorphic state.** Cell catalogs created by the product's own
  `CatalogStore._initialize` (18 tables). State rows are either product-produced during a
  run or copied-from-production with recorded provenance + sha match (never hand-authored).
- **R4 Counters are call spies.** Every provider/scan/read/producer count comes from the
  sitecustomize count-on-entry spy (I07D_SPY_DIR); INSERT-derived counts are forbidden as
  counter evidence. W-probe must re-prove zero_insert wiring before the matrix runs.
- **R5 Trigger or invalid.** A cell passes ONLY with trigger location + occurrence count ≥1
  recorded (clause2 + matrix L58). No reliable injection ⇒ cell = BLOCKED + evidence, never
  a fake trigger, never a pass.
- **R6 Exit honesty.** The exit rule in §0 forbids passing on "it threw": every triggered
  point needs before-state, trigger, error evidence (cause/code/retryability), after-clear
  retry deltas, and recovery verdict — all five per cell.

## 2. Per-cell frozen plans (initial state → injection technique → trigger evidence)

### F01 — point (a) provider返回 — cell `%TEMP%\i07d\cases\F01` (CN-ZIJIN-2025, state3)

- **Initial state**: fresh cell, raw+sidecar ABSENT, 0 registration rows, security_master +
  rebound configs copied (build_iso state3). `initial_state.json` proves it.
- **Injection technique**: the product's own adapter config seam — cell
  `config/source_acquisition.yaml` cn-adapter `command` rebound to the scratch fixture
  script `harness/fixture_403_adapter.py` (json_command_v1 protocol; same seam as
  filing-fetch's own `tests/e2e_support/spy_adapter.py`). Fixture behavior: `discover`
  → OK with one valid candidate (fields per production candidate in
  prod_rows_dump metadata); `fetch` → exit 1 with LAST stderr line =
  `{"schema_version":"1.0","status":"failed","error":{"code":"http_403","retryable":true,
  "message":"HTTP 403 Forbidden from provider (frozen I-07-D fault fixture)"},
  "adapter":{"name":"stockinfo-cninfo","version":"1.1.0"}}` — `retryable:true` mirrors the
  frozen CN403 precedent semantics of card_I-04-E (F-E2: upstream retryable=true must be
  preserved, never rewritten to false). Fixture appends one JSON line per invocation to
  `evidence/cases/F01/fixture_log.jsonl` (trigger counter).
- **Runs**: (1) entry fault run (frozen argv, `--allow-download`, no sim env);
  (2) direct `fetch_filing.py` run, same fault — captures the FULL stdout envelope
  (chain-capture diagnostic, I-00-B documented argv class); (3) direct
  `filing_fetch_client.py` run, same fault — captures the FULL stderr doc (entry embeds
  only last 800 chars); (4) recovery: entry run with fault cleared by serving the frozen
  simulated provider (`I07D_SIM_FROZEN_META` = fixtures/CN-ZIJIN-2025.provider.json — the
  I-07-B S-*-3 authorized arm, labelled simulated).
- **Expected trigger**: fixture_log fetch lines ≥1 (frozen bound: 1..3 — close_gap
  `attempts >= 3 or not retryable` bound, close_gap.py:397); spy `provider` counter ≥1 on
  each fault run; trigger location = `adapter_process.py:155-178` (rc≠0 → error_code
  parsed) inside runs 1–3.
- **Expected error chain (hops recorded raw; loss at any hop = FINDING, never hidden)**:
  origin fixture stderr (http_403/true/cause) → wiki CLI failure doc (record actual) →
  fetch_filing stdout envelope {error_code, retryable, stage, attempts, error} rc2 →
  client stderr `{error_code, error, retryable}` rc2
  (filing_fetch_client.py:270-286) → entry stderr `{"error_code":"upstream","error":
  "filing-fetch client exited 2: <client stderr tail>"} ` rc3
  (source_preparation.py:109-113,221-224). Frozen invariant: the marker `http_403` and a
  `retryable` field/text appear in hops 1,3,4,5 (hop 2 recorded as measured).
- **Pseudo-qualified (clause3) checks**: entry run-1 stdout contains NO record JSON (no
  `reuse_receipt`/`source_id` success doc); cell raw stays ABSENT (无伪raw — no file at the
  canonical path, catalog `documents/locations` delta 0); downloads = 0.
- **Recovery (clause4)**: run 4 from the SAME entry after clearing the fault. Frozen deltas:
  provider +1 (sim fetch), raw appears with sha256 == manifest
  `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d`, registration
  documents+1 / locations+2 / roots+1 / sources≥1 (I-07-B S-CN-3 measured shape), then the
  chain refuses at the review gate (`not_reviewed`, rc3) — the gap REMAINS VISIBLE; the
  recovery may NOT be described as "无缺口" (matrix F01 清除列).
- **clause5**: no kill in F01.

### F02 — point (c) scan错误 — cell `%TEMP%\i07d\cases\F02` (HK-XIAOMI-2025, state2)

- **Initial state**: raw+sidecar present (sha == manifest `ffd73376…2da7c`), 0 registration
  rows, entities+catalog_meta only.
- **Injection technique**: genuine I/O fault at the scan boundary — a scratch holder
  process opens the cell's raw PDF with Win32 `CreateFileW(ShareMode=0)` (share-none) and
  holds it across the scan; the scanner's read raises `PermissionError` (OSError) →
  product's own per-file path `scanner.py:964-976` (errors+=1, error_details, continue) →
  `scan_runs.status = completed_with_errors` (`scanner.py:1209`). Holder writes
  `evidence/cases/F02/lock/hold.json` (ready/release timestamps) = trigger evidence.
- **Expected trigger**: scan1 product rc **0** (CLI reports, cli.py:1560), report
  `errors ≥ 1` (frozen: exactly 1 file error, 1 error_detail with `PermissionError` text),
  `scan_runs.status == "completed_with_errors"` (row re-read after run) — trigger location
  scanner.py:964-976 → :1209, count 1.
- **Expected state at fault**: catalog `locations/documents/sources` delta 0 (file NOT
  registered; `roots` +1 root upsert is expected and is NOT a handle), raw sha unchanged,
  sidecar unchanged.
- **No-handle proof (clause3)**: follow-up entry run WITHOUT `--allow-download` (frozen
  argv) → refusal `not_found`-class (I-07-B measured S-*-1/S-*-2 shape: rc3,
  error_code upstream, stdout empty) = 不返回可消费可 handle. Report must NOT claim
  `errors=0`/`completed` while the file is unregistered (that would be pseudo-qualified).
- **Error cause survival (clause3)**: `error_details[0].error` contains the
  `PermissionError` text and survives into `scan_runs.report_json` (quoted end-to-end).
- **Recovery (clause4)**: holder released → `cli scan` (original registration entry) run 2.
  Frozen deltas: rc 0, `scan_runs.status == "completed"`, documents+1 / locations+2 /
  sources≥1 (REGFAIL-HK measured shape), **provider delta 0 both runs (新增下载0)**, raw
  bytes unchanged.

### F03 — point (d) DB事务内锁等待 — cell `%TEMP%\i07d\cases\F03` (HK-XIAOMI-2025, state2)

- **Initial state**: as F02 (independent fresh cell).
- **Injection technique**: `harness/lock_catalog.py` (I-07-B REGFAIL precedent, i07d path) —
  second sqlite connection takes `BEGIN EXCLUSIVE` on the CELL catalog for 75 s; the
  product's writers use `BEGIN IMMEDIATE` under `busy_timeout=30000`
  (store.py:994/:1018) ⇒ genuine **in-transaction lock wait ≈30 s** then raw
  `sqlite3.OperationalError("database is locked")` → `error_taxonomy.py` → catalog_busy.
- **Expected trigger**: scan1 (started ~2 s after lock) product rc **1**, elapsed ≥ 25 s
  (lock-wait evidence), stderr `{"error": "database is locked", "error_type":
  "catalog_busy", "retryable": true, "status": "failed"}` (error_taxonomy structured_error,
  cli.py:1551-1559); `hold.json` shows BEGIN EXCLUSIVE acquired BEFORE scan start and
  released AFTER scan end; catalog delta {} (no partial write); stdout empty.
  Trigger location = store.py BEGIN IMMEDIATE wait path; count 1.
- **Pseudo-qualified**: rc1 + empty stdout + zero registration ⇒ no looks-fine output.
- **Recovery (clause4)**: lock released → `cli scan` run 2: rc 0, documents+1/
  locations+2/sources≥1, **provider delta 0 both runs (释放锁后幂等恢复，不重下raw)**,
  raw sha unchanged.

### F04 — point (b) raw提交后scan前 — cell `%TEMP%\i07d\cases\F04` (HK-XIAOMI-2025, state3)

- **Initial state**: raw+sidecar ABSENT, 0 registration rows.
- **Injection technique**: entry run with `--allow-download` + frozen sim provider
  (`I07D_SIM_FROZEN_META`) so fetch stages bytes; inside the same wiki subprocess,
  `canonical_writer.import_staged` commits raw (`_atomic_copy` :182 + provenance :184)
  and THEN calls `scan_catalog` (:185). The spy's scan wrapper, armed with
  `I07D_FAULT=kill_before_scan`, fires exactly in that window: writes
  `pid_<pid>.json` (pid/ppid/argv/cwd) + `barrier_<pid>.json` into I07D_STATE_DIR and
  sleeps forever. The orchestrator polls, verifies (pid registered ∧ cmdline/cwd ∈ F04
  cell ∧ alive), and `TerminateProcess(pid, 4242)` (KILL_EXIT_CODE; finally does not run).
- **Expected trigger**: 1 barrier file, 1 pid manifest, kill executed on the registered PID;
  post-checks: target gone, no `pid_<pid>.released.json` (barrier never resumed), no
  normal-exit marker. Trigger location = `canonical_writer.py:185` call boundary (after
  :184, before scan body), count 1.
- **Expected state at fault (clause3)**: raw file PRESENT at canonical path (raw committed
  before the barrier) with sha == manifest + `.source.json` provenance present;
  catalog `documents/locations/roots/scan_runs` delta 0 (scan never started ⇒ 无半合格
  handle); entry fails rc3 (`error_code=upstream` from killed wiki child via
  fetch_filing:234-241), entry stdout has NO record JSON.
- **Recovery (clause4)**: NEW process `cli scan` (arm cleared) → rc 0, registers the
  orphan (documents+1/locations+2/sources≥1), **provider delta 0 (不重下raw)**, raw sha
  unchanged (原件不损坏), spy scan counter +1.
- **clause5**: PID scoping evidence per kill (manifest + cmdline/cwd assertion + census:
  no pre-existing process killed).

### F05 — point (e) producer执行 — cell `%TEMP%\i07d\cases\F05` (CN-ZIJIN-2025, state2 + product scan + production normalized copy)

- **Initial state** (frozen construction): fresh cell; raw+sidecar copied (sha verified);
  `cli scan` (product) registers the document; THEN copy the PRODUCTION `artifacts` row
  with role `normalized` (production catalog, read-only SELECT) with its derived file
  `…\.source_catalog\derived\01\01819e…\normalized.md` relocated into the cell (paths
  relocated, content sha re-verified; provenance label `production_observation_copy`);
  role `summary` ABSENT **by construction** (this is the partial-roles input state,
  analogous to I-07-B's state2 "unregistered by construction"). Build fails hard (cell
  BLOCKED with evidence) if the production row/file is missing, status ≠ completed, or the
  document_id does not equal the scan-produced urn.
- **Injection technique**: share-none holder on the CELL `normalized.md` across
  `cli summarize`; product reads it at `summarizer.py:165` → `PermissionError` →
  `except (OSError, UnicodeError): failed += 1; continue` (:168-170) → report
  `ProcessingReport("summarize", …, failed=1)` (:270), NO summary artifact INSERT.
- **Expected trigger**: summarize-fault run product rc **0** with report
  `failed == 1, completed == 0`, `summary` artifacts row count 0, `summary.md` absent;
  trigger location summarizer.py:163-170, count 1 (spy `producer` summarize +1).
- **No pseudo-qualified output (clause3)**: the report must disclose failed=1 (a report
  claiming completed≥1 or failed=0 with no summary row = pseudo-qualified FAIL). The
  successful role stays真实状态: `normalized` artifact row (sha/created_at) and file bytes
  unchanged.
- **Cause survival (clause3) — pre-registered risk**: summarizer.py:168 swallows the
  OSError without recording its text; frozen criterion = IF neither the report/stdout nor
  any catalog row carries the PermissionError cause, verdict for clause3-on-F05 =
  **FAIL recorded as finding F-F05-cause** (product defect surface, routed — never hidden,
  never "it threw ⇒ pass"). Trigger proof otherwise stands on hold.json (lock held within
  the run window) + single-variable control below.
- **Control/recovery (clause4)**: release lock → rerun THE SAME original entry
  `cli summarize`: frozen deltas `completed == 1, failed == 0`, `summary` artifacts +1
  (exactly the missing role), `producer_events` +1 for summary, **normalize NOT called**
  (spy producer normalize delta 0) and `normalized` row/file byte-identical (成功角色不
  重复生成), provider delta 0, file inventory +summary.md only. Single variable between
  fault and control runs = the lock (I-09-C F12 A/B attribution pattern).
- **Demand traceability**: during the fault state the missing role is derivable from
  artifacts (absence + DAG summary:[normalized]) and the failed attempt is disclosed by
  the report's failed counter; RF-side `producer_events` needs-list is in-memory only
  (processing_demand.py:47 Pure-memory queue — recorded as a disclosed limitation, not a
  pass claim).
- **clause5**: no kill in F05.

### F06 — point (f) 发布提交边界 — three sub-cells (fresh state+registry each), iso/rf

All three sub-cells: `ATT/iso/rf` = read-only copy of current RF (scripts/config/
references); writer spawns the harness writer process (PID manifest first, hooks only when
`--fault != none`); per-sub-cell registry `evidence/cases/<sub>/state/registry/publications.jsonl`
via `REVENUE_PUBLICATION_REGISTRY`; inputs = common.make_input_docs (P0/P1, byte-identical
to I-09-C's); a FRESH `d_reader.py` process observes after seed/fault/recovery1/recovery2
(current-registry schema: chained `line_sha256`/`prev_line_sha256`, `input_sha256`,
`result_sha256`, …; NO publication_id/commit-state in production — reader defines
consumable = json member exists ∧ markdown member exists ∧ recomputed input_sha256 matches
the json claim ∧ a registry row carries the same input+result pair ∧ chain verifies; product
authorities `is_registered`/`audit` cross-checked in the same fresh process).

**Boundary mapping note (frozen)**: current production orders registry append BEFORE member
writes (revenue_core.py:479 → revenue_forecast.py:114/:118) and has NO `commit_publication`
(I-09-C's H6 target is absent); therefore the three matrix sub-boundaries are injected as:
(1) registry persistence = `err:append_registry` before any byte; (2) 第二输出文件 =
`err:replace:output_markdown` (2nd `_atomic_write_text` call, role by call order);
(3) commit边界 = `kill:return:before` (after both members durable, before main returns =
before any caller acknowledgement). This is recorded as the scenario_matrix row-meaning
mapping; the binding invariant across all three = 「不见可消费半发布」+ P0 intact.

- **Seed (each sub-cell)**: clean P0 publish (`--fault none`) → rc 0 → fresh reader
  `reader_after_seed_p0`: P0 consumable, P1 rows 0, chain ok.
- **F06a_registry** — fault `err:append_registry` (real OSError before `orig_append`):
  frozen = writer rc **2**, stderr contains the injected cause text
  (`registry failure` marker — revenue_forecast.py:120-122 `error:` line; no JSON envelope
  in production — recorded as measured), registry P1 rows **0**, P1 json/markdown members
  **absent** (registration precedes writes), hook_trace `err_raised op=append_registry`
  count 1, reader: p1 consumable **false**, p0 consumable **true**, chain ok, audit (no
  result files) problems 0. Recovery1/2 (clean publish same P1 input): rc 0 each, p1
  consumable true, audit problems 0, p0 untouched (hash-identical), registry rows grow
  append-only (P1 row +1 per clean run — disclosed per I-09-C P-C2 "允许历史行数不误报
  重复bug"; conflict impossible with the same deterministic result_sha256), chain ok.
- **F06b_second_output** — fault `err:replace:output_markdown` (2nd member, real OSError):
  frozen = writer rc **2** + cause text on stderr, registry P1 row **+1** (appended before
  members), json member present, markdown member **absent**, hook_trace
  `err_raised op=replace role=output_markdown` count 1; reader: p1 consumable **false**
  (member incomplete ⇒ no consumable half-publish), is_registered(p1)=true (ordering
  disclosed), audit with `--result p1.json` problems **0** (claim IS registered), p0
  consumable true, chain ok, no mixed package (json+registry agree; markdown simply
  missing). Recovery1/2: rc 0, markdown written, p1 consumable true, audit 0, p0 intact,
  no history deletion.
- **F06c_commit** — fault `kill:return:before`: writer killed for real on its registered
  PID (`TerminateProcess 4242`), writer-exit record ABSENT, hook_trace
  `point=return:before` count 1, barrier file present; frozen after-state = registry P1 row
  present + BOTH members durable & hash-verified → reader sees the COMPLETE new package
  (p1 consumable **true** — complete, never half), p0 consumable true, chain ok; caller
  received NO acknowledgement (no rc, no stdout ack). Recovery1/2 (clean retry same
  input): rc 0, is_registered stays true, audit problems 0 (same result_sha256 ⇒ no
  conflict), p0 + all prior history rows preserved (never deleted), members atomically
  replaced with identical hashes (deterministic engine), chain ok.
- **clause5 (F06c)**: writer registers `pid_<pid>.json` BEFORE any work (writer.py order);
  kill gated on manifest ∩ barrier ∩ alive ∩ cmdline/cwd ∈ attempt/iso-rf tree; census
  assertion unchanged.

## 3. Frozen trigger-count table (minimum evidence per clause2)

| cell | trigger location (file:line) | technique | required count evidence |
|---|---|---|---|
| F01 | adapter_process.py:155-178 (fixture fetch rc≠0) | adapter-config fixture script | fixture_log fetch lines ≥1 (≤3), spy provider ≥1 per fault run, per-hop raw docs |
| F02 | scanner.py:964-976 → :1209 | share-none raw lock during scan | scan_runs.status=completed_with_errors + errors≥1 (==1), hold.json window ⊃ scan1, spy scan +1 |
| F03 | store.py BEGIN IMMEDIATE wait → error_taxonomy catalog_busy | 2nd connection BEGIN EXCLUSIVE 75 s | hold.json acquired-before/released-after, scan1 elapsed ≥25 s, stderr catalog_busy, spy scan +1 |
| F04 | canonical_writer.py:185 boundary (after :184) | spy barrier + TerminateProcess on registered PID | barrier + pid manifest + kill-ok + no released-marker, count 1 |
| F05 | summarizer.py:163-170 | share-none normalized.md lock during summarize | report failed==1 + hold window ⊃ summarize + spy producer +1; control run completed==1 |
| F06a | publication_registry.py:95-113 (_append entry) | harness err hook (real OSError) | hook_trace err_raised op=append_registry ==1, rc2 |
| F06b | revenue_forecast.py:33 (2nd member os.replace scope) | harness err hook role=output_markdown | hook_trace err_raised role=output_markdown ==1, rc2 |
| F06c | revenue_forecast.py:123 (main return) | barrier + kill on registered PID | hook_trace return:before + barrier + kill-ok + exit-record absent, count 1 |

Untriggered ⇒ cell INVALID (matrix L58) and recorded as such, not passed.

## 4. Frozen delta-accounting table (clause4 — recovery from the ORIGINAL entry)

| cell | metric | fault phase | recovery phase (frozen) |
|---|---|---|---|
| F01 | spy provider / downloads | discover 1 + fetch 1..3 / **0** | **+1 sim fetch / +1 download**; registration +documents1+locations2+roots1; then review-gate refusal remains (gap visible) |
| F02 | spy provider / registration | 0 / +roots1 only | **0 / +documents1+locations2** (registration-only recovery, 新增下载0) |
| F03 | spy provider / registration | 0 / {} | **0 / +documents1+locations2** (no re-download) |
| F04 | spy provider / raw / registration | +1 sim fetch / raw committed / {} | **0 / raw sha unchanged / +documents1+locations2** |
| F05 | producer calls / artifact rows | summarize 1, normalize 0 / summary +0, normalized unchanged | summarize +1, **normalize +0** / **summary +1 only** (normalized row sha+created_at identical), provider 0 |
| F06a/b/c | registry rows / members / audit | per sub-cell above | rc0×2, audit problems 0, **no history deletion**, members hash-identical, P0 byte-identical |

Masking rule: recovery NEVER issues bulk-rebuild commands; any unexpected re-download,
re-produce, or duplicate successful-role artifact surfaces in these deltas as a FINDING.

## 5. Frozen PID-kill spec (clause5)

Kills: F04 (wiki child), F06c (writer child). Gate = pid manifest written by the TARGET
itself before the barrier + barrier file + alive + cmdline/cwd ∈ this case's scratch tree;
hard kill = TerminateProcess(4242); post = gone ∧ no released-marker ∧ no normal-exit
record; process census (pid+cmdline) before/after the whole matrix ⇒ every killed PID is
manifest-registered and no pre-existing (real worker) process died.

## 6. Per-clause frozen verdict criteria (how each cell can FAIL honestly)

- **C1 isolation**: each cell has its own catalog/state; initial_state hashes per cell;
  before/after snapshots equal on production anchors+samples ⇒ FAIL if any cross-cell
  state reuse or production byte change is found.
- **C2 triggers**: any cell missing trigger location+count ⇒ INVALID/BLOCKED (R5), never
  pass.
- **C3 pseudo-qualified**: per-cell checks in §2; additionally the exit forbids
  "it threw" — a cell with only an exception and no before/after/recovery evidence fails.
  Error-chain hop loss (F01) and cause swallow (F05) are recorded per §2 as findings if
  measured.
- **C4 deltas**: measured vs §4 table; deviation = finding (e.g., re-download on recovery
  = idempotency defect exposed, not absorbed).
- **C5 kill scope**: any kill outside the manifest gate, or any non-manifest process dead
  afterwards ⇒ FAIL immediately (clause5/stop condition).

## 7. Hand-reasoned predictions (frozen; measured values go to decision.md unchanged)

- F01: fault entry rc3/upstream, client rc2, ff rc2; fixture fetch 1..3; raw absent;
  recovery downloads 1 (sim) + registration + review refusal (not_reviewed) — the exact
  I-07-B S-*-3 authorized shape; `http_403` visible at hops 1/3/4/5 unless a hop drops it
  (then: finding, quoted per hop).
- F02: scan1 rc0 + completed_with_errors(errors=1) + no registration; entry refusal
  not_found-class; scan2 rc0 registers, provider 0/0.
- F03: scan1 rc1 catalog_busy elapsed≥25 s, delta {}; scan2 rc0 registers, provider 0/0.
- F04: barrier fires once; kill ok; raw present unregistered; entry rc3 no stdout record;
  scan-recovery registers with provider delta 0.
- F05: summarize-fault report failed=1 completed=0 rc0, no summary row/file; control
  completed=1; cause text likely NOT persisted (summarizer.py:168) ⇒ pre-registered
  finding candidate F-F05-cause.
- F06a rc2 + zero P1 anything; F06b rc2 + registry row + json only; F06c kill with complete
  durable package; recoveries rc0, audit 0, P0 untouched.

## 8. Reviewer attack list (frozen before results)

1. Re-hash one cell's raw/sidecar + initial_state yourself; confirm cells are independent.
2. Read spy/sitecustomize.py + d_hooks.py: confirm count-on-entry and that hooks never
   edit product files; confirm `--fault none` installs nothing.
3. Attack trigger counts: pick F02 and F04 — recompute status/hold/barrier/pid evidence
   from raw files; a count of 0 invalidates the cell.
4. Attack F01 chain: diff the four hops; say exactly where `http_403`/`retryable` survive
   or are lost.
5. Attack F04/F06c kill scope: verify manifests, cmdlines, census; try to find any killed
   PID not in a manifest.
6. Attack clause4: recompute recovery deltas from events.jsonl + catalog counts; look for
   any re-download/re-produce masked by a rebuild.
7. Attack pseudo-qualified: for each fault run, ask whether ANY stdout/report/row claims
   success while the system was broken.
