# I-07-B independent review — reviewer_report.md (attempt a20260923-01)

Reviewer: independent review subagent (parent session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`),
signed by the reviewer only, N=1 signer (the implementer did not and cannot self-sign; `handoff.json`
`status=review_pending`, `implementer_signed=false` re-verified live).
Method: read / grep / pwsh + two reviewer re-runs into `%TEMP%`; RF and CW product trees READ-ONLY
(production catalog: `Get-Item` stat only — N=0 opens by this reviewer); no product writes; the only
writes inside the attempt directory are this file and `reviewer_report.sha256`; no state-changing git
(the one RF porcelain probe used `git --no-optional-locks status --porcelain=v1`, which writes no index
state, and was required by the review brief).

## 0. Verdict

**ACCEPTED_SCOPED** — the nine-step delivery is reproducible, its measurements hold under independent
re-derivation, its disclosures are backed by artifacts, and its exit-honesty face is intact. Acceptance
carries the conditions and carry-scope in §11 (one non-blocking pin-annotation defect, reviewer finding
F5, settled with the report; F1/F2/F3/F4 carried downstream as parent/parent-upstream scope — not this
card's fix surface; I-00-B anchor-table refresh is a dispatcher/parent action).

Basis (N=12 independently measured, details below): 12/12 handoff-pinned deliverable+evidence hashes
re-computed and matched; oracle CreationTime precedes the first judged run; my WPROBE re-run reproduced
`evidence/wprobe.json` byte-identically (sha256 `e01c8c90…`); my frozen-argv case re-run (S-CN-2 run1)
reproduced each comparison field including the stderr byte-hash; F1/F2/F3 each verified against live product code
AND raw run evidence; zero three-market-pass sentences; every simulated event labelled `simulated:true`（域：本 attempt 42 条 spy 事件）;
production catalog identity, 20/20 anchors, and 3/3+3/3 sample hashes unchanged across the attempt and
still unchanged at review time.

## 1. Deliverables — live re-hash (task item 1)

Values recomputed by this reviewer at review time; pins from `handoff.json.current_source_hashes`
(the task's expected prefixes are the first 8 hex chars shown).

| deliverable | live sha256 (prefix) | expected | match | CreationTime vs first judged run |
|---|---|---|---|---|
| oracle.md | `b92b6650d215cf89…` | `b92b6650…` | ✓ | 07:19:36 < wprobe 07:31:37 < first judged run 07:33:17 (frozen-first ✓) |
| binding.json | `2f4b7f40f4aa29e3…` | `2f4b7f40…` | ✓ | 07:29:22, pre-run (argv contract + counter_wiring + anchor_drift_vs_I00B present) |
| commands.json | `6e0f2e5780e3c975…` | `6e0f2e57…` | ✓ | 07:29:22, pre-run; see §1a |
| decision.md | `a538c4113cea7776…` | `a538c411…` | ✓ | case×clause matrix, J1..J9, F1..F4, §8 unverified present (read in full) |
| changes.diff | `3fa4e5d87e2bdd7c…` | `3fa4e5d8…` | ✓ | header claims anchors_identical=20/20 — re-derived in §6 |
| handoff.json | `37bb946a03c4bc34…` | (self-excluded) | n/a | `status=review_pending`, `implementer_signed=false`, `reviewer_status=PENDING` ✓ |
| recovery/README.md | `0e1b5e1fe9612963…` | handoff pin `0e1b5e1f…` | ✓ | retention rules present; isolation state still exists (see §3) |
| after/case_results.json | `72cf2bfb965a5833…` | `72cf2bfb…` | ✓ | 11 cases; per-run rcs/counters/deltas read and spot-checked in §4/§9 |

Additional pinned evidence re-hashed live, all MATCH: `evidence/wprobe.json e01c8c90…`,
`evidence/live/reachability.json 38008149…`, `evidence/snapshot_before.json 138795f2…`,
`evidence/snapshot_after.json b50563a2…`, `evidence/plan_anchor_hashes.json 9c182fac…`.

### 1a. commands.json scan (I-00-B argv forms only, exit legend, no git verbs)

- Registry contains exactly the I-00-B-bound entry form (`scripts/source_preparation.py --request-file …
  --timeout-seconds … --company-wiki-config … --filing-fetch-root … [--allow-download]`) plus harness
  bookkeeping commands (SNAP/ISO/DRIFT/WPROBE/ENTRY/SCAN/LOCK/LIVE/SUMMARIZE). `exit_code_legend` present
  and self-describing (harness 0/1/2/3 + product rcs recorded raw, explicitly "NOT the harness legend").
- Grep for `git` in commands.json returns N=2 hits: line 49 `(difflib; no git)` and line 104
  `"git": "NOT USED as a bound command in this card"` — **zero git verbs in the registry**; the one
  disclosed pre-binding `git diff --no-index` deviation (J7) is recorded in binding.forbidden,
  decision §6 J7, and handoff `git_command_deviation` (3/3 locations, verbatim-consistent). Backing
  artifacts verified in §8.

## 2. C1 — counter wiring is count-on-entry on real entry points (the card's hard red line)

- **Wiring table**: `binding.json.counter_wiring` freezes provider (2 adapter classes' discover/fetch +
  `requests.sessions.Session.request`), scan (`service.SourceCatalog.scan`, `scanner.scan_catalog`),
  read (`resolver._sha256_of_file`, `resolver._read_verified_bytes`, `SourceManifest.from_file`,
  `company_wiki_source.verify_artifact_reads`), producer (service normalize/extract_sections/summarize/
  backfill-if-present + 4 module-level producer functions). The same 18 targets appear as
  `status:"wrapped"` in `evidence/wprobe.json.wiring` and in per-case `counters/wiring.json`.
- **Wrapper code read** (`harness/spy/sitecustomize.py`): `_wrap()` installs `wrapper` which calls
  `_event(counter, …)` **before** `return original(*args, **kwargs)` — count-on-entry, before
  delegation (lines 71–79). Activation is gated on `I07B_SPY_DIR` (no effect on other processes).
  The frozen-sim replacement functions also emit their event before serving fixture bytes and hard-code
  `"simulated": True` in the event detail (lines 133–135, 167–169).
- **WPROBE record**: `zero_insert_proof=true`; `counter_totals_after_probe` = scan 2, read 2, provider 2
  (exactly the task's expectation); throwaway product-schema catalog row counts byte-identical before/after
  (18 tables: zeros except catalog_meta=1); 18/18 targets `wrapped`; `producer_wired` proven by wrap
  status with the disclosed note that no inert producer invocation exists.
- **No INSERT-derived counting (grep of the harness)**: reported counter values come solely from
  `counter_snapshot()` counting lines of `events.jsonl` (`run_case.py:92-103`). `SELECT COUNT(*)` appears
  solely in `catalog_counts()`/`catalog_counts_dir()` for *state* deltas (run evidence), never feeding the
  four counters. `INSERT` statements exist solely in `build_iso.py` (isolation state construction copying
  the production observation; its `inserted[t] += cur.rowcount` bookkeeping lands in
  `initial_state.json.rows`, not in any counter) — no artifact/producer_events INSERT feeds any reported
  provider/scan/read/producer value anywhere in this attempt's harness.
- Verdict: **C1 PASS confirmed** (the decision's C1 PASS claim holds under independent code reading).

## 3. Reviewer's own re-runs (two, into %TEMP%) (task item 3)

Isolation state: `%TEMP%\i07b\cases` **still exists** with all 11 case trees (retention honored —
recovery/README keeps them until review signs off), so no re-derivation was needed. MAX_PATH layout as
disclosed (J4).

Method adaptation (disclosed): the documented argv forms write their evidence under `<attempt>`, which is
outside this reviewer's write boundary. I mirrored the harness byte-identically to
`%TEMP%\i07b_review\harness\` — `run_case.py` sha256 `9756b59a064773e9…` and
`spy\sitecustomize.py` sha256 `58da8b36e45a734a…` both hash-equal to the attempt copies — reached the
attempt's interpreter through a directory junction (`%TEMP%\i07b_review\iso\venv` →
`<attempt>\iso\venv`, Python 3.13.9), and ran the commands.json argv forms with `<attempt>` replaced by
the mirror; PYTHONPATH composition, `I07B_SPY_DIR` semantics, and cwd-analog were unchanged. Outputs
landed in `%TEMP%\i07b_review\evidence\`.

### 3a. WPROBE re-run — CMD-I07B-WPROBE

- Command: `<mirror-python> -X utf8 -B %TEMP%\i07b_review\harness\run_case.py wprobe
  %TEMP%\i07b_review\evidence\wprobe_tmp` → harness rc 0.
- Result: `zero_insert=true`, totals **scan 2 / read 2 / provider 2**, 18/18 targets `wrapped`,
  row-count diffs `[]`.
- Strongest form of agreement: my produced `wprobe.json` sha256 =
  `e01c8c905d65609dad150df36a95cd2d4207b415450387a24bc3dc6537aef96c` — **byte-identical to the
  attempt's own `evidence/wprobe.json` and to the handoff pin**.

### 3b. Frozen-argv case re-run — S-CN-2 run1 (the F1 cell)

- Command: `<mirror-python> -X utf8 -B %TEMP%\i07b_review\harness\run_case.py entry S-CN-2 1`
  (harness rc 0, elapsed 94.7 s). Inner argv = the frozen entry form recorded in their `run1/argv.json`
  (same entry script, same flags; solely harness-rooted request/config paths point at the mirror).
- Field-by-field comparison my run vs `evidence/cases/S-CN-2/run1/evidence.json`:

| field | mine | theirs | match |
|---|---|---|---|
| product_returncode | 3 | 3 | ✓ |
| stderr sha256 | `57a7b0b47590ee56ad7b5efd38f6ea84739e0d4c8bf5b2c3cf22ef08a2b9ffba` | same | ✓ (byte-identical stderr) |
| stdout sha256 | `e3b0c442…` (0 bytes) | same | ✓ |
| counter_delta / totals before / after | `{}` / `{}` / `{}` | same | ✓ |
| catalog_count_delta | `{}` | `{}` | ✓ |
| raw_unchanged / expected sha | true / `01819e1c…f343d` | same | ✓ (raw re-hashed by my run) |
| stages (raw/注册/资格/review/适用工件/实际消费) | identical JSON | identical JSON | ✓ |
| refusal.parsed_fields | `{error: "…no_existing_source_satisfies_request…", error_code: "upstream"}` | same | ✓ |
| deep_verification | skip: refusal path — C4.2 arm applies | same | ✓ |

- My counters dir recorded `event_lines: 0` before and after, equal to their run1/run2 baselines
  (resolve-missing touches no wrapped byte-read entry — consistent with F1's strict-lookup shape).
- Idempotency bonus: after my (3rd) invocation the isolated S-CN-2 catalog is still **byte-identical to
  `initial_state.json.iso_snapshot`** (sha256 `631eb434af1b412c1af7140ddd52e7398e380c969f4d0f90b13d21201daa0ffb`,
  I re-hashed it myself) and its 18-table counts equal their `run1.catalog_counts_before`
  (independently SELECTed read-only by me; `EQUAL: True`).
- Verdict: **their documented stages/refusal/counters are exactly reproduced**; S-CN-2 re-run agrees
  with my reading of `after/case_results.json` (rc 3, counters `{}`, catalog delta `{}`,
  `structured_actionable_present=false`, C3 repeat fields provider/producer deltas 0).

## 4. The three findings — independent verification (task item 4)

### F1 — entry resolve/ensure never scan (S-*-2 fails by product shape) — CONFIRMED

Code map re-read against live product bytes (CW = `C:\Users\郑曾波\Projects\company-wiki\src`):
- `resolver.py`: grep for `scan(`/`scan_catalog` → **zero occurrences** in the whole file;
  `SourceResolver.resolve` (line 1355) starts from `self.catalog.query_filing_candidates(...)` (line 1387)
  — a SQL-pushdown SELECT over registered rows. Strict read-only lookup, no filesystem walk, no scan.
- `ensure`: the read-only ensure path (`cli.py:753`) calls `SourceResolver(...).resolve(request)` solely;
  `acquisition_service.py:77 ensure` → `coordinator.resolve_or_stage` + `writer.import_staged`
  (import happens solely after an authorized download) — no scanner call anywhere in `ensure`.
- Sole registration entry: `service.py:142 def scan → scan_catalog` dispatched from the `scan`
  subcommand (`cli.py:185`, dispatch `cli.py:952-953`).
Measured corroboration: S-CN-2/HK-2/US-2 both runs `catalog_count_delta={}`, no `scan` key in
`counter_delta` (scan 0), refusal `missing / no_existing_source_satisfies_request` — in case_results and
independently reproduced by my run (§3b). **F1 stands: matrix operation "第一次从入口恢复注册" is not
achievable through the current entry; `cli scan` alone registers.**

### F2 — every refusal lacks structured actionable recovery（域：25 次最终入口运行的拒绝）— CONFIRMED (C2.2 FAIL)

Two refusal raws spot-checked verbatim from `evidence/cases/*/…/stderr.txt`:
1. S-CN-1 run1 (review-gate refusal):
   `{"error_code": "upstream", "error": "prompt injection not reviewed — source preparation blocked per policy (prompt_injection_status=not_reviewed)"}`
   → parser output: `parsed_fields={error, error_code}` solely; `actionable_recovery_fields={}`;
   `structured_actionable_present=false`; `explicit_missing_info.names_missing=true`.
2. REGFAIL-HK scan1 (locked registration):
   `{"error": "database is locked", "error_type": "catalog_busy", "retryable": true, "status": "failed"}`
   → `actionable_recovery_fields={}`; `structured_actionable_present=false`.
The structured field inventory across this attempt's refusals is exactly
`{error_code,error,retryable}` or `{error_type,retryable,status}` — no `candidates`/`next_action`/
`required`/`gap_plan` on any failure path (matches code-map Q7 as cited). The NL "explicit missing info"
arm of clause 4 does pass (S-CN-1, S-3 run2/3 name `not_reviewed`; S-*-2/REGFAIL entry name
`no_existing_source_satisfies_request`), which is what the decision claims — structured-recovery arm fails.
**This is the C2.2 FAIL and ties to I-06-A's unsigned OPEN-5 structured-recovery contract (carried).**

### F3 — no review-receipt CLI → zero RevenueSourceRecord → C4 value arm unexercised — CONFIRMED

- `cli.py` subcommand inventory read: scan, normalize, summarize, fingerprint_backfill, extract_sections,
  derived_audit, status, focus_cleanup, documents (retire/restore), identity_enrich (preview/verify/reject),
  identify, query, evidence, sections-list, reconcile-retire, prune-retired, extraction-quality, duplicates,
  duplicate-preview, duplicate-recycle, resolve, ensure, close-gap, import-portfolio, run, worker, plugin
  commands, install/uninstall/startup, activation (sole `--reviewer` flags = activation apply/rollback),
  runtime-policy. **Zero review/prompt-injection subcommand exists.**
- `record_prompt_injection_review` exists solely as a Python function (`prompt_injection.py:263`) with
  in-package references (`read_chain.py:223`, `source_lifecycle.py:168`); grep of RF `scripts/` for it →
  zero occurrences. No CLI wiring (D-W06 OPEN-4 unsigned — carried).
- Zero-record evidence: across all 25 final entry runs (+ 4 scan runs) — N=29 outputs — **0 stdout files are non-empty**
  and **0 contain `reuse_receipt`** → this attempt emitted zero RevenueSourceRecord rows, so C4's
  deep-value assertions have nothing to check (decision C4/§8 state exactly this; C4.2 arm passes on the
  NL refusal text). Review stage unreachable for each of the 3 markets under the current product ⇒ no
  source-preparation qualification yet — as the decision says (measured reality stricter than
  declaration 1, honestly so).

## 5. Honesty face (task item 5)

- **Three exit declarations, verbatim** — card `execution_v2/card_I-07-B.md` exit line reads
  `…三公司仅来源准备通过，仍未授予正式预测资格。缺一市场/真实路径不得总体写三市场通过。恢复：保留已取得raw，只回退当前隔离变更。`
  The three sentences appear byte-identically in decision §0 (lines 11–13), decision §4, handoff
  `exit_honesty_declarations_verbatim`, and oracle §0 — 4/4 copies match the card.
- **OVERALL = NEGATIVE**: decision §0 "**Overall three-market statement: NEGATIVE (no overall pass is
  claimed)**" + handoff `overall_three_market_pass: false` with the NEGATIVE rationale (declaration 2 +
  the stricter measured fact that no RevenueSourceRecord exists). Grep for pass-claims across
  decision+handoff returns only the declaration/prohibition sentences (decision:12,17,110; handoff:13) —
  **zero sentences assert a three-market pass** in this attempt's decision or handoff.
- **S-*-3 caveats**: all three S-*-3 rows say "matrix criteria PASS at C level" (C-only, chain still
  refuses at review); the HK canonical-name open item is disclosed in decision §8 AND handoff
  `case_matrix_results`/`open_questions`. I verified the observable myself: the isolated S-HK-3 file is
  `2026-04-28_hkexnews_12127452_小米集團－Ｗ 2025年度報告.pdf` (4 405 561 B) while
  `sample_manifest.json` names `2026-04-28_hkexnews_12127452_2025年度報告.pdf` — the name differs exactly
  as disclosed (bytes match manifest size; the registered-identity re-derivation remains open, §12).
- **L rows BLOCKED ×3**: decision table L-CN/L-HK/L-US = blocked (unbound `*-NEW-MISSING` identity + no
  download authority) and handoff repeats 3/3 as blocked; reachability recorded CN 200 / HK 200 /
  US 403 (`reachable:true`, `unreachable_markets=[]`, header NAMES only, no bodies) in
  `evidence/live/reachability.json` (re-hash matches pin). The manifest's `unbound_live_samples` rule
  text confirms no frozen identity exists for the L cells.
- **Simulation labels**: I scanned each `events.jsonl` under `evidence/cases` —
  `lines=42 total, events lacking a simulated field = 0`; S-CN-3/S-HK-3/S-US-3: 10/10 lines each carry
  `simulated:true`, provider events 4/4 per case with 0 provider events unsimulated; the other cases'
  scan/read events carry `simulated:false`. The single live network call in the attempt is the separate
  reachability probe (recorded in `evidence/live/`, never in spy events). **No simulated event masquerades
  as live, and no spy event exists without a label.**

## 6. Isolation / production integrity (task item 6)

- **Production catalog identity** (`…\company-wiki\.source_catalog\catalog.sqlite3`):
  before and after snapshots both `bytes=49677344768`, `mtime_ns=1789799495406919100`; my live
  re-stat: bytes 49 677 344 768 ✓; FILETIME 134342730954069191 → (−116444736000000000)×100 =
  **1 789 799 495 406 919 100 ns — exactly the claimed mtime_ns**, so the production database file is
  bit-identical to the pre-attempt state at review time (reviewer performed stat only, N=0 opens).
- `-wal`: 0 bytes in both snapshots and 0 bytes live (mtime unchanged between snapshots).
  `-shm`: 32768 bytes in both snapshots; mtime_ns advanced before→after
  (`1790143125773848600 → 1790145208348637600`) and has advanced further since — the disclosed
  read-only-open effect (SQLite touches the shm index on `mode=ro` opens), size constant, no write
  statement ever issued (their probes ran `PRAGMA query_only=ON`).
- **Anchors 20/20**: programmatic comparison of `snapshot_before.anchors` vs `snapshot_after.anchors`:
  valid anchors 20, identical after 20, changed 0 (the 6 plan-input anchors carry `missing:true` — the
  J8 path bug, see §7). Includes `RF/scripts/source_preparation.py 91a6dc32…` before and after ✓,
  `fetch_filing.py 046cc7dc…`, `store.py 1a783240…`, `CW/config/source_catalog.yaml f9eb72a6…` as
  decision §5 states. Live re-hash at review time still equals the AFTER values for
  source_preparation `91a6dc32…`, revenue_forecast `2a2dfede…`, CW cli `fad88c60…`, fetch_filing
  `046cc7dc…`.
- **Samples**: both snapshots show raw 3/3 `raw_match=true` and sidecar 3/3 `sidecar_match=true`
  against the frozen manifest (CN `01819e1c…`/`7f7570fe…`, HK `ffd73376…`/`8228741d…`,
  US `e3de0053…`/`1cbfb1a2…`) — C3's asset-bytes claim holds at both ends.
- **RF porcelain** (`git --no-optional-locks status --porcelain=v1`): exactly five entries —
  ` M REMEDIATION_REGISTER.md` (mtime 2026-09-23 03:42:04 = pre-attempt, parent's register round),
  ` M progress.md` (same mtime), `?? execution_runs/I-07-B/` (this attempt's own new, uncommitted work),
  `?? .tmp-r41-mutation/` (mtime 2026-09-20), `?? assurance/…/plan_inputs.json.bak` (mtime 2026-09-21) —
  the two modified files and both strays predate the attempt start (06:54), and **zero product
  paths (scripts/config/tests) appear as modified** — consistent with `product_files_written: ZERO`.
- Per-case freeze evidence (C1.1 substance): `initial_state.json` per case carries asset sha256
  (src==dst==manifest), the iso file-list hashes, populated-table row counts, worker_control absent;
  the full 18-table pre-run counts live in each `run1.catalog_counts_before` (captured by the harness
  before the entry subprocess starts) and `iso_base.json.schema.table_count=18` (product's own
  `CatalogStore._initialize`) — I re-counted the isolated S-CN-2 catalog myself: 18 tables, counts equal.

## 7. Anchor drift handling (task item 7)

Drift table (`binding.json.anchor_drift_vs_I00B` + `evidence/anchor_drift/anchor_drift.json`) vs live:

| file | I-00-B / old | claimed current | my live re-hash | match |
|---|---|---|---|---|
| RF/scripts/source_preparation.py | `5ec16eaf…` (= I-06-A-era copy) | `91a6dc32…` | `91a6dc32466e9d67…` | ✓ (difflib diff 28 lines = W05-B receipt line, verified by reading the diff) |
| RF/scripts/revenue_forecast.py | `6b3d960e…` | `2a2dfede…` | `2a2dfede7941b0fa…` | ✓ (`revenue_forecast.py.diff` 0 lines after newline normalization ⇒ EOL-only, as claimed) |
| CW/src/…/cli.py | `2f5c5740…` | `fad88c60…` | `fad88c60294a7fb7…` | ✓; content diff honestly declared non-reconstructable without git (no I-00-B-era copy) |
| also drifted vs I-06-A pristine copies | filing_fetch_client `9329f331→b281e6d1`, company_wiki_source `aeeb7b2a→7d1bd8f9 (257-line diff)` | — | live = `b281e6d1…`/`7d1bd8f9…` (anchor snapshots) | ✓ |

- **Captured observations NOT rewritten (J8)**: both `snapshot_{before,after}.json` still carry
  `missing:true` on the 6 plan-input anchors (their pinned hashes match live, proving the files were not
  re-emitted after the bug was found); the corrected capture `evidence/plan_anchor_hashes.json` (pin
  matches) carries the right values, which I re-derived live: card `bd09eb6c…`, scenario_matrix
  `0dec23cd…`, manifest `d5d0bb92…`, I-00-B binding `fdb2a598…`/commands `f8a397ec…`/oracle
  `e9c82fe4…`, START_HERE `5c6e111f…` — 7/7 MATCH live bytes.
- **Superseded dirs spot-verified**: `S-CN-3`, `S-HK-3`, `S-US-3` each retain
  `run2.pre_scaffold`, `run2.pre_scaffold2`, `run2.pre_fix2`, `run3.pre_scaffold`, `run3.pre_scaffold2`,
  `run3.pre_fix2` alongside the final `run2`/`run3` — three fix generations preserved, and case_results
  even carries their rc/counters (rc 3 for each) rather than hiding them.
- **No product file was written by this attempt**: 20/20 anchors + production identity + 6/6 samples
  unchanged (§6) — the drift is upstream time, not this card's doing. The dispatcher's I-00-B
  anchor-table refresh remains open (parent action, §11).

## 8. Disclosures scan — J7 / J8 / J9 (task item 8)

| disclosure | in decision | in binding/handoff | artifact backing (verified) |
|---|---|---|---|
| **J7** `git diff --no-index` before binding, outputs replaced | §6 J7 (timing, replacement, "no git repo state touched") | binding.forbidden (parenthetical), handoff `git_command_deviation` | The two `evidence/anchor_drift/*_old_vs_current.diff` files (mtime **07:15:51 < binding 07:29:22**) contain genuine `diff --git a/… b/…` headers = the git-no-index outputs, retained; the binding-referenced `*.py.diff` files (mtime 07:16:51) are difflib format (`--- I-00-B-era:` / `+++ current:`) = CMD-I07B-DRIFT replacement. commands.json holds no git verb (§1a). Disclosure is accurate: timing, replacement, and no-repo-state all check out. |
| **J8** 6 plan anchors wrongly `missing:true` | §6 J8 ("captured observations were NOT rewritten") | handoff completed_steps 5 + open_questions (post-run captures note) | snapshots (pins match) still show `missing:true` for exactly those 6 paths (path resolved one level too deep — visible in the stored path strings); corrected `plan_anchor_hashes.json` present (07:03:47) and re-verified live (§7). Originals untouched. |
| **J9** three mid-run fixes, each preserving prior evidence | §6 J9(a) YAML `\U` path bug → rebuild before any successful run; (b) WinError 3 scaffolding + fixture `candidate_id` fixes with `*.pre_scaffold*/*.pre_fix2*` preserved | handoff changed_paths + raw_exit_codes.superseded_attempts_preserved | Timeline coherent: `build_iso.py` mtime 07:33:12 (config-template fix) → all 11 `initial_state.json` 07:33:17–26 → `adapter_scaffolding.json` 07:45:47 → superseded run dirs 07:38–07:48 → `make_fixtures.py` 07:49:30 → final S-3 run2/run3 07:49–07:52. Superseded dirs exist (§7); no oracle change after runs (oracle hash unchanged from pre-run pin). |

## 9. Oracle §7 attack list — reviewer results

1. **Re-derive a raw sha256 + initial_state counts**: my S-CN-2 re-run re-hashed the isolated CN raw =
   `01819e1c…f343d` (79 925 886 B) before and after; snapshots independently re-hash the 3 production raws
   + 3 sidecars against the manifest (3/3+3/3 at both ends). I re-counted the isolated S-CN-2 catalog
   read-only: 18 tables, counts equal to `run1.catalog_counts_before`; catalog file hash equals
   `initial_state.iso_snapshot` (`631eb434…`).
2. **Counters are call-wiring**: read `sitecustomize.py` (§2) + reproduced the WPROBE byte-identically
   (§3a) + grep shows no counter path touches an INSERT (§2).
3. **C3.2 duplicate registration**: REGFAIL-HK scan1 under lock → rc 1, `scan:1`, catalog delta `{}`
   (0 rows); scan2 after release → rc 0, `scan:1`, `read:2`, delta `documents+1, entities+1,
   locations+2, sources+2, roots+1, document_entities+1, scan_runs+1`, provider absent (=0, no
   re-download); both entry runs catalog delta `{}`. S-3 run3 (post-registration re-resolve) grows only
   `document_fingerprint_state+1` — never documents/sources/locations. No second registration of the
   same version exists in this attempt's measured rows.
4. **C4.1 re-hash a produced record**: N/A — this attempt produced zero RevenueSourceRecord (§4 F3), so
   there is no canonical_path to re-hash; the honest skip is recorded in each run's
   `deep_verification.skip_reason`. The value arm stays unearned (gated by the review receipt, not by
   this card).
5. **Attack the refusals**: parsed raws from two refusal families — structured actionable recovery is
   absent in both (F2); the NL arm is genuinely specific (`not_reviewed`, `no_existing_source_satisfies_
   request`), i.e., actionable in prose but not machine-parseable ⇒ C2.2 FAIL exactly as declared.
6. **Attack §0**: grep over decision+handoff found 4/4 prohibition-sentence hits (§5); the handoff field
   `overall_three_market_pass` is literally `false`.
7. **Attack simulation labels**: 42/42 spy events carry a `simulated` label; 12/12 provider events in
   the three sim runs are `simulated:true`; no provider event outside those runs exists; the live probe
   is recorded separately with statuses (§5).

## 10. Reviewer-added finding

- **F5 (reviewer, minor, non-blocking — REM-79/REM-86 domain discipline)**: `handoff.json.input_hashes`
  pins `I-07-A/after/state_matrix.json` as `dc72776f…`, but the live file (mtime 2026-09-20 15:47:06,
  untouched during this attempt) hashes to `de784cb2f94cb2ed7a3b13a315063fb4fc7b746519db939ea58e6707abbe8684`
  — which is also what this attempt's own `evidence/plan_anchor_hashes.json` records. Root cause proven,
  not guessed: `sha256(LF→CRLF of disk bytes) == dc72776f…` **byte-exactly**, i.e., the pin is the
  CRLF-variant of the same content (disk is pure LF), inherited verbatim from I-07-A's handoff/review
  pins (both contain `dc72776f…`). Content identity is therefore established; the defect is that the pin
  ships without its EOL domain annotation while the attempt's corrected capture uses the LF value — two
  conventions for one file inside one handoff. **Settlement item**: annotate the pin
  (`disk(LF)=de784cb2…; pin=LF→CRLF variant; content identical — verified by reviewer`) or re-pin the
  raw-disk value with provenance. No measurement, verdict, or frozen input depends on it (state_matrix was
  consumed read-only; decision §5 does not cite this pin). This is the known REM-86/EOL-pin class, not a
  content drift.

## 11. Verdict conditions and carry-scope (scope if accepting)

1. **F1 / F2 / F3 are downstream/parent findings — carried, NOT this card's fix surface**: F2 ties to
   I-06-A's unsigned OPEN-5 structured-recovery contract; F3 is the review-CLI gap under D-W06's
   unsigned state (OPEN-4); F1 is the entry-vs-`cli scan` registration gap the owner must route.
   F4 (L cells blocked ×3) stands as measured. The matrix cells recorded NOT-passed stay NOT-passed.
2. **Anchor-table refresh of I-00-B = parent/dispatcher action** (J6 drift: source_preparation,
   revenue_forecast, CW cli; CW cli content diff reconstructable solely where copies exist).
3. **Exit-honesty declarations carry into any downstream use** of this attempt: the three verbatim
   sentences, `overall_three_market_pass=false`, and the stricter measured fact (zero
   RevenueSourceRecord) must accompany any citing artifact.
4. **F5 settlement annotation** (§10) — one line at settlement, per project precedent for minor pin
   defects (accepted, fixed at 落定).
5. Retention: `%TEMP%\i07b\cases` and `evidence/wprobe_tmp` may be cleaned solely after this sign-off,
   per recovery/README (this review is now the sign-off; the superseded `*.pre_*` evidence dirs plus the
   attempt evidence must be kept).

## 12. Unverified / remaining open (honest list)

- HK-3 registered identity: I confirmed the **name** differs from the manifest (§5) but did not
  independently re-derive its registered hash identity — stays open as decision §8 says.
- `document_fingerprint_state+1` on S-3 run3: observed in case_results, not root-caused (their §8 item,
  accepted as disclosed).
- Producer counter: wiring status alone; this attempt contains zero producer invocations, so no
  invocation-proof exists (their §8 item; correct for these cases).
- I did not re-run the S-*-3 frozen-sim arms, the REGFAIL lock arms, the live probe, or the snapshots —
  just WPROBE and S-CN-2 as tasked; those results rest on the artifacts verified above.
- I-07-A-side provenance of the CRLF pin (whether upstream pinned pre-normalization bytes) not
  investigated — out of this card's scope; F5 records just the reproducible fact.
- CW cli `2f5c5740→fad88c60` content diff remains non-reconstructable without git (disclosed J6).
- I-07-B attempt evidence remains uncommitted (`?? execution_runs/I-07-B/`); committing is the
  parent's/owner's action (no state-changing git by this review).

## 13. Boundary compliance and self-check

- Writes: exactly two files in the attempt (`reviewer_report.md`, `reviewer_report.sha256`); run
  outputs into `%TEMP%\i07b_review\**`; isolation state at `%TEMP%\i07b\cases` reused per recovery
  README (review re-run authorized); RF/CW/FF product trees read-only; production catalog never opened
  by this reviewer (stat solely); git: one read-only `git --no-optional-locks status --porcelain=v1`
  (required by the brief; no index/repo state changed); never self-signed.
- REM-79 self-check: this file was scanned with the REM79 attempt tool
  `execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py` under
  `PYTHONIOENCODING=utf-8`; result recorded in the reviewer's final message and
  `reviewer_report.sha256` covers the checked bytes.
