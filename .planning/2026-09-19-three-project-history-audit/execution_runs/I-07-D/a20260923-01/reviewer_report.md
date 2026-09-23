# I-07-D a20260923-01 — independent reviewer report

- Card: **I-07-D 故障矩阵与断点恢复** · Attempt: `a20260923-01` · Reviewer: independent session dispatched by parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`
- Method: sampled independent verification across the dispatch's 8 verify sections. Tools: `read` / `grep` / `pwsh` only; no network tools; no git; two rulings issued below. My helper scripts ran in `%TEMP%\i07d_review\` and my only writes anywhere are this report + its `.sha256` sidecar (域：本报告 §12 boundaries).
- The implementer handoff stays unsigned (`status=review_pending`, `implementer_signed=false`); this report is the acceptance instrument (域：review_and_handoff rule).

## VERDICT: `accepted_scoped`

The frozen-oracle chain, the 8-cell trigger ledger, clause-3/4/5 proofs, both supersession disclosures, and the write boundaries all survive independent re-computation from raw files (域：8 cells = F01–F05 + F06A/B/C). Four findings are recorded (FR-1..FR-4), none blocking; FR-1 carries a required landing gap-marker condition. The two deferred product findings are ruled in §6/§7: **F-F06-audit = NON-BLOCKING (rows PASS, measured red retained, ledger-routed)** and **F-F05-cause = REMEDIATION-ledger route with F05 row-PASS + clause3-cause-FAIL recorded**. Acceptance scope is fixed by the per-cell table in §10.

---

## 1. Deliverables re-hashed + freeze order — VERIFIED

| deliverable | dispatch pin | my re-hash | result |
|---|---|---|---|
| oracle.md (frozen first) | `576ddfc5…18846` | `576ddfc57c2c949d6a9e5f875114d8c7e49c833d69b5bd8cd81bcf2417718846` (27211 B) | MATCH |
| binding.json | `30ea8a7b…4e8e` | `30ea8a7be0469c77dff8f084a93c142e9b9a7595454f76e8c410b3f245c4e4e8` | MATCH |
| commands.json | `458c62c3…e6e` | `458c62c36824014c3f9552e46f4b0851d30242db8508da16e1c4a7e09ccce66e` | MATCH |
| decision.md | `79252379…49d5` | `792523799fcbf74002d3ff3e1db876c80f19a47baabc10099fbe457ac9f649d5` | MATCH |
| changes.diff | `f3dfe7c7…8e5a` | `f3dfe7c7ea6260efe15d8268d45f4a3d469473662a4e5799e9228817c5908e5a` | MATCH |
| recovery/README.md | `65d6bebb…ffbf` | `65d6bebbb8f24abbaeedbea760d11315a09baeb2af1eb4bc65e64c1e4330ffbf` | MATCH |

- **Freeze order (stat-based)**: binding `17:47:35` → oracle `17:50:26` → first case-state evidence `18:06:34` → first judged product run evidence `18:09:51+` (F01 run1). The oracle precedes every judged run (域：6 timestamp points).
- **Per-card input pins re-hashed file-by-file, 9/9 match**: matrix `0dec23cd…` (L47–58 read — the 6 F rows below), card_I-07-D `b54f4bc8…`, card_I-04-E `9f98b194…`, card_I-09-C `59e9d71d…`, sample_manifest `d5d0bb92…`, I-09-C oracle `ccd1ea51…`, I-09-A decision `94a27b8a…` + addendum `de7fa1f3…`, I-07-B oracle `b92b6650…` (+handoff `e43cf258…`), I-00-B binding `fdb2a598…` (+commands `f8a397ec…`).
- **Exit declaration**: card `退出：…` vs handoff `exit_declaration_verbatim` byte-compared — the first quoted sentence 「每个触发点有前后状态、错误与恢复证据；不能以单一“抛了异常”通过。」 is exact; the final clause differs by **1 ASCII space** (`先blocked` vs `先 blocked`) → FR-3. `matrix_l58_rule_verbatim` == matrix L58 **exactly** (my byte compare: True). Handoff is `review_pending` / unsigned as required (域：2 status fields).
- **Matrix six rows tested = the rows pinned**: F01 原error/retryable/cause保留+无伪raw → F01 verdict hop/no_fake_raw/recovery-not-pseudo checks; F02 原件保留/注册失败/无handle/下载0 → F02 raw_preserved + nohandle_refusal + recovery_no_download; F03 锁错误+幂等恢复不重下 → F03 elapsed/catalog_busy/recovery_no_download; F04 无半合格handle+恢复资产+原件不损坏 → F04 no_consumable_stdout + raw_committed/provenance + raw_intact; F05 真实状态+仅补缺项 → F05 failed:1 + summary_plus1_only + normalized_not_reproduced; F06 不见可消费半发布/幂等/不删历史 → F06 consumable flags + rec2 rows + history_not_deleted (域：6 matrix rows ↔ 6 cell verdicts).

## 2. Trigger-count ledger (matrix L58 hard criterion) — VERIFIED

`evidence/verdicts.json`: trigger counts **F01=1 F02=1 F03=1 F04=1 F05=1 F06A=1 F06B=1 F06C=1**, `blocked=[]`, per-cell failed_checks solely `fault_audit_clean`+`rec2_audit_clean` on the 3 F06 cells (§6). Three spot-verifications from raws:

- **F03 lock-hold**: `lock/hold.json` — `BEGIN EXCLUSIVE` on `%TEMP%\i07d\cases\F03\…\catalog.sqlite3` (scratch path, 域：1 catalog path), locked `17:29:31.742`, released `17:30:46.743` (75 s hold); scan window in F03 verdict `[1790184573.695332, 1790184608.2103322]` → **34.515 s exact** (arithmetic: end−start = 34.515000…; start = lock+1.95 s, end = release−38.5 s — the wait is inside the hold on both sides); stderr raw = `{"error": "database is locked", "error_type": "catalog_busy", "retryable": true, "status": "failed"}`; rc1; stdout empty sha `e3b0c442…`; catalog delta `{}`. Trigger count 1 at `store.py BEGIN IMMEDIATE` wait path — real lock-wait, not an instant error.
- **F04 kill**: `state/pid_42124.json` self-written by the barrier wrapper — `argv` contains `…\i07d\cases\F04\cwroot\config\source_catalog.yaml` AND `cwd=…\i07d\cases\F04\cwroot` (both scratch, no production config path in the manifest); `barrier_42124.json` present; gate checks in `run1_entry_fault/evidence.json` = manifest_present/path_in_argv/path_in_cwd/alive_before **4 of 4 true**, `alive_after=false`, `kill.exit_code_set=4242`, `released_marker_present=false`; product itself quotes the kill: entry stderr `…company-wiki ensure exited 4242: no stderr…` rc3, stdout empty (`stdout_has_consumable_record=false`). Count 1.
- **F06C kill gate**: same pattern — `pid_36224.json` (argv + `cwd=…\a20260923-01\iso\rf`, both inside ATT), `barrier_36224.json`, checks all true, `alive_after=false`, rc **4242**, `released_marker_present=false`, fault-writer exit record ABSENT (`writer_exits=[writer_exited_29860.json]` only — seed), `fault_writer/stdout.txt` = 0 B (no ack), hook trace `return:before` count 1. Count 1 (域：3 of 3 spot-checks passed).

## 3. Clause-3 pseudo-qualified negations — VERIFIED from raws

1. **F01 (best of 3, five-hop chain re-read)**: fault entry stdout EMPTY (sha `e3b0c442…`), zero record markers, raw ABSENT (`raw_sha_before/after=null`, catalog delta `{}`), downloads 0 (FF envelope `"downloads": 0`). Chain hop-by-hop from raw files: hop1 fixture doc inside wiki stderr `{"code":"http_403","retryable":true,"message":"HTTP 403 Forbidden from provider (frozen I-07-D fault fixture)"}`; hop2 wiki CLI wrapper `error_type:"fatal", retryable:false` (re-derived, recorded); hop3 FF stdout envelope `{status:fatal, stage:ensure, attempts:1, calls:3, downloads:0, error:…http_403…}` rc2; hop4 client stderr `{error_code:fatal, error:…403…, retryable:false}` rc2; hop5 entry stderr `{error_code:"upstream", error:…}` rc3. `http_403` + a `retryable` field survive hops 1→2→3→4→5 verbatim-as-text — verdict hop1/3/4/5 checks all true match the raws (域：4 hops carrying the marker). Trigger: `fixture_log.jsonl` = 3 discover + 3 fetch lines, run1 window fetch=1 (bound 1..3), outcome `http_403`, fixture cwd under the cell scratch tree.
2. **F02**: scan1 rc0 BUT `scan_runs.status=completed_with_errors` with `errors:1` and `error_details[0].error="PermissionError: [Errno 13] Permission denied: '…年度報告.pdf'"` — cause text present in both the stdout report and `scan_runs.report_json` (quoted in both raw files); hold `17:19:07.865→17:19:20.821` (12.956 s) ⊃ scan1 (`17:19:15→17:19:19`). Later entry `entry_nohandle`: rc3, stdout EMPTY, stderr `error_code not_found / source is not reusable: missing / no_existing_source_satisfies_request` — no consumable handle. Precision note (FR-4 context): that entry ran ~0.2 s AFTER the holder released, so it proves the fault-PRODUCED state is non-reusable while the request is unchanged; after the recovery scan the same entry passes 資格 to the review gate.
3. **F06B**: at fault the registry has the P1 row (line 2) + `p1.json` present + `p1.md` ABSENT; fresh reader computes `p1 consumable=false` (member completeness fails), `p0 consumable=true`, `chain.ok=true`, `is_registered(p1)=true` (ordering disclosed), `no_mixed_package=true`, `tmp_files=[]`; fault stderr plain text `error: [Errno 13] I-07-D injected replace failure: '…p1.md'` rc2 — no success claim anywhere (域：3 clause-3 examples verified against raws).

No fault run printed a success-looking stdout/report: F01 empty, F02 discloses errors=1, F03 rc1+empty, F04 empty (no half-handle), F05 `failed:1` counts-only, F06 rc2/4242 + plain `error:` line (attack-list item 7 answered for 8 of 8 sub-cells).

## 4. Clause-4 deltas recomputed from raws — VERIFIED

| cell | fault phase (measured) | recovery phase (measured) | vs frozen |
|---|---|---|---|
| F01 | provider +2 (discover+fetch), downloads **0**, rows 0, raw absent | provider +2 (sim discover+fetch), **+1 download** (raw lands `01819e1c…f343d` = manifest), documents+1 locations+2 sources+2 roots+1 scan_runs+1, then review-gate refusal rc3 `prompt_injection_status=not_reviewed`, stdout empty | +1 download exact; gap stays visible (域：1 recovery entry re-issued) |
| F02 | provider key absent from both counter sets = **0/0**; rows as D-1 | rc0, errors0, provider **0**, raw sha unchanged, registrations complete | 新增下载0 ✓ |
| F03 | provider 0, catalog delta `{}` | rc0, delta `{scan_runs+1, sources+1}` + registrations, provider key absent = **0**, raw sha unchanged | 幂等恢复不重下raw ✓ |
| F04 | provider +2, raw committed (canonical name ≠ manifest, sha `ffd73376…` ✓ + `.source.json`), rows `{}` (scan never started: scan_runs 0→1 solely at recovery) | `cli scan` rc0, **provider delta 0** (key present = 0), documents+1 locations+2 sources+2; entry-after rc3 at review gate, provider 0 | 原件不损坏 ✓ |
| F05 | producer events = summarize×1 (spy), summary **+0** (artifacts=1 normalized only), normalized row/file byte-identical (`980ea4f8…`, created_at `2026-07-31 21:36:54`), report `failed:1` | producer summarize +1 (`events.jsonl` = 2 lines, both `service.summarize`, normalize **0 calls**), artifacts 1→2 (**summary+1 only**, `0b11ca34…`), producer_events 1→2, normalized row+file unchanged, provider 0 | 仅补必需缺项 ✓ |
| F06A/B/C | A: 0 rows/no members; B: +1 row/json only; C: +1 row/both members | rc0×2; rows append-only **1→3 / 1→4**; p0 json+md shas constant (`960699f4…`/`de9eee94…`) in every reader; members hash-identical across recoveries; no conflict | 不删除历史 ✓ |

- **Independent chain recompute (my own implementation of `contracts.evidence.canonical_sha256`, definition read at `evidence.py:139-143`)**: F06A 3/3 lines, F06B 4/4, F06C 4/4 — every `line_sha256` re-derives and every `prev_line_sha256` links; rows 1–2 at rec2 are the same content-addressed lines read at fault time (history never rewritten). Input shas recomputed from bytes: p0 `02a9502e…f35e`, p1 `f5a8413e…f0b9d` — identical to the reader's `sha_computed` in all 3 sub-cells (域：3 registries re-derived).
- Masking exposure: no recovery re-downloaded (F02/F03/F04 provider=0), no re-produce (normalize=0), no bulk rebuild anywhere — the deltas would have exposed each of these (域：3 masking classes checked).

## 5. Clause-5 kill scope — VERIFIED, one disclosure defect (FR-1)

- `census_diff.json`: before **359** → after **349**, gone=25, **real_source_catalog_gone=0**; every gone entry is OS/harness churn (SearchFilterHost/svchost/chrome/node/pwsh…). The killed PIDs (`42124`, `36224`) and F06C's launcher `49348` appear **nowhere in census_before** (my grep: 0 hits) ⇒ no pre-existing process died (域：0 of 3 killed PIDs in the before-census).
- Both kill manifests are self-registered scratch children: F04 `pid_42124.json` (argv∧cwd inside `%TEMP%\i07d\cases\F04`; argv[0] is the product CLI *source path* with the cell config — no production config/worker path in the manifest); F06C `pid_36224.json` (argv+cwd inside ATT). Gate code re-read (`run_d_matrix.py:120-173`): kill permitted solely on manifest ∧ path-in-argv ∧ path-in-cwd ∧ alive; else `gate_failed_not_killed` is recorded and the PID is skipped.
- **Gate-failed-not-killed record**: the sole raw record in the attempt is `F06C/fault_writer.pre_gate_fix/result.json` → `gate_failed_not_killed=[{pid:44784, checks: argv:false, cwd:false}]` + `launcher_kill={pid:49348, 4242}` — verified. **No such record exists for F04's first attempt**: its evidence dirs were deleted (disclosed), and decision §7.1's transcription shows `{killed:{}, timed_out:true, barrier_files_at_timeout:[]}` — a TIMEOUT shape (the barrier never fired), not a gate-fail shape. Worse, decision **§6's F04 paragraph conflicts with §7.1** (§6 says gate-failed + launcher killed as fallback + "recorded in gate_failed_not_killed" + cites `writer.py` manifest fields — `writer.py` does not appear anywhere in F04's execution path; that text matches F06C attempt-1). → **FR-1 (P2): honest gap marker / erratum required at landing**; the rebuilt F04 cell itself is internally consistent and unaffected.
- F06C attempt-1's child `44784` died without a recorded mechanism (no `writer_exited_44784`, absent from census_after, absent in my live process scan now) — no stray process is alive (my live `Get-CimInstance` scan for `i07d|writer.py` returned only my own tool subprocesses); carried as unverified mechanism, scope-safe.
- Recovery README §2 cleanup authorization present (`SAFE TO CLEAN after the independent review signs off`); its process re-scan claim holds now (域：live scan this review).

## 6. RULING 1 — **F-F06-audit: NON-BLOCKING for the three F06 cells** (option (b))

**Defect verified at source (line-level).** `scripts/publication_registry.py`:
- **L207** `by_generation: dict[tuple[str, str, str, str], set[str]] = {}` — keys typed as tuples;
- **L208–215** `generation = (entry["input_sha256"], engine, schema, artifact_type)`; `by_generation.setdefault(generation, set())` — keys ARE tuples;
- **L216** `for (anchor, engine, schema, artifact_type), result_hashes in by_generation.items():` — unpacking proves tuple keys (the conflict branch itself is sound);
- **L228** `claimed = artifact.get("input_sha256")` → a `str`;
- **L229** `if not isinstance(claimed, str) or claimed not in by_generation:` — for any well-formed `str` claim the first operand is False and `str in {tuple keys}` is **always False** (str never equals/hash-matches tuple) ⇒ the `unregistered claim` branch at **L230–233 fires for each readable result file**, registered or not. The intended check is anchor-level (`any(gen[0] == claimed …)`).

**Contradiction measured in the same fresh process** (their reader raw, re-read by me): F06A `reader_after_seed_p0/authority` + F06B/C `reader_after_fault/authority` each show `is_registered_p0=true` / `is_registered_p1=true`, `registry_path_match=true`, `chain.ok=true` while `audit_problems=[unregistered claim … never registered]` for p0/p1 (域：3 of 3 readers contradicting audit).

**Is the row evidence tainted? No — it is independent of the buggy path.** I read `harness/d_reader.py` in full (247 lines): `consumable` = json-exists ∧ md-exists ∧ parse ∧ recomputed-input-match ∧ registry-result-match ∧ chain-ok (L187-190); chain recompute (L95-121) and input recompute (L73-86) never call `audit()`; `is_registered` (product L188-190) is a correct string comparison on `input_sha256`. The buggy L229 branch is a **one-way false-positive generator**: it can only *add* a spurious problem line; it cannot suppress the correct conflict branch (L216-221, which emitted zero `conflict:` lines), alter reader consumability, alter chain linkage, or delete history. Append-only/history/p0-identity are proven from the registry file bytes + my independent chain recompute (§4). Therefore the F06 **matrix-row expectations (visibility + idempotent recovery + no history deletion + trigger location/count) all PASS on evidence that does not flow through L229**.

**Posture ruling (both halves):**
1. **The implementer's KEEP-RED decision is CORRECT and stays**: do NOT re-gate `fault_audit_clean`/`rec2_audit_clean` to true — `audit_problems==0` was frozen in oracle §2 before results, and measured ≠ frozen is recorded as measured (`all_ok=false` on the 3 cells stands; no retry-to-green). This is exactly the I-09-C F12 handling (case kept red), whose disposition in the register is "F12 保留不阻断验收" (kept red, does not block acceptance).
2. **The red is NON-BLOCKING for this card**: it is a product defect outside this card's surface (fix = publication-registry track), so it routes to the **REMEDIATION ledger** as product finding F-F06-audit (`publication_registry.py:229`, suggested class: audit false-positive / operator-CLI trust), fixes NOT part of this card. The three F06 cells land as **row-evidence PASS + frozen-audit-check FAIL (product defect), measured red retained, non-blocking** — this is the per-cell table in §10.

## 7. RULING 2 — **F-F05-cause: REMEDIATION-ledger route; F05 cell = row-PASS + clause3-cause-FAIL recorded; NOT blocked**

- **Defect verified at source**: `company-wiki/src/company_wiki/source_catalog/summarizer.py:164-170` — `markdown = normalized_path.read_text(...)` inside `try`, `except (OSError, UnicodeError): failed += 1; continue` — no log, no re-raise, no persistence of type/text/code/retryability at the swallow point.
- **Verified from their raws + my own read-only catalog query**: fault stdout = `{"completed":0, "failed":1, operation:"summarize", …}` counts only (0 B stderr); recovery stdout = `{"completed":1, "failed":0}`; hold window `1.744 s` ⊃ the fault run (single variable = the lock); my `mode=ro`+`query_only` scan of the F05 cell catalog: `producer_events` has NO error-ish column (7 columns, none carrying cause) and its 2 rows are the seed normalized event + the recovery summary event — **the failed attempt persisted nothing**; a column sweep across all 18 tables for error/cause/reason/message/retry fields with values returned **empty** (域：0 persisted cause fields in 18 tables). So "no durable cause field exists elsewhere in this card's surface" is confirmed; clause-3's `错误cause/code/retryability不丢失` genuinely FAILS at the F05 origin, honestly pre-registered and recorded (`verdicts.json.F05.cause_survival=FAIL`).
- **Routing**: REMEDIATION ledger as product finding (same class/track as C1 / F-REV-7 — remediation-track, fix NOT this card's surface), owner = CW producer track (`summarizer.py:168`). **Posture**: F05 cell = **row-evidence PASS** (真实状态保持 failed:1 honest + 需求可追踪 by report counter & summary-absence + recovery 仅补缺项 verified) **with clause3-cause-FAIL carried as the ledger finding** — not `blocked`, not a cell-red: trigger and recovery evidence are complete, and the failure is a product cause-persistence defect, not an evidence gap.

## 8. Disclosures audit

- **F04 attempt-1 overwrite**: the §7.1 transcription EXISTS with specific values (`kill_record={killed:{}, timed_out:true, barrier_files_at_timeout:[]}`, no `scan_catalog_barrier` wiring entry, run1 counters `{provider:2, read:4}` with no scan event, registration completed) and the stale-binding root cause + fix are stated. The rebuilt cell is **internally consistent** (I verified kill-gate checks all true, counters `{provider:2, scan:1}`, catalog delta `{}` at fault, raw+provenance committed, recovery registers with provider 0, entry-after rc3). Judgment: **overwrite acceptably bounded, but FR-1's §6↔§7.1 conflict needs an honest gap marker at landing** (record in landing notes + remediation-style erratum; do not edit the frozen decision.md bytes). The expected `gate_failed_not_killed` record for F04 is confirmed ABSENT (§5) — the gap marker must say so.
- **F06C `*.pre_gate_fix` present**: `fault_writer/pre_gate_fix`, `recovery1/2_writer.pre_gate_fix`, `seed_writer.pre_gate_fix`, `state.pre_gate_fix/**` — 4 of 4 preserved on disk (I read the fault one: gate-fail + launcher-kill raw record) — disclosure accurate.
- **Verdict-only recalcs**: product-facing raws predate every recalc verdict — F01 raws ≤`18:11:51` < verdict `18:46:00`; F02 ≤`18:20:45` < `18:29:09`; F03 ≤`18:30:48` < `18:46:00`; F05 raws/verdict same run-second `18:39:17` (no later rewrite); F06 raws ≤`18:43:20` < verdicts `18:43:35-37`. No product raw was rewritten by any recalc (域：5 of 5 cells mtime-ordered).
- **D-1..D-4 recorded**: D-1 in F02 verdict (`model_prediction_checks.oracle_literal_zero_registration_rows_at_fault=false` + note) and decision §5; D-2 (retryable re-derivation) §5; D-3 filename divergence §5 (+F04 evidence's filename_note); D-4 attempts=1 §5. All 4 present (域：4 of 4 divergences).
- **Evidence JSON**: full parse of the json_check scope (attempt `*.json` + `evidence/**.json`) = **242 files, 242 ok, 0 bad** — matches the 242 claim exactly; I additionally read 20+ JSON evidence files line-by-line (verdicts, evidences, readers, manifests, holds, snapshots).

## 9. Findings (4 of 4 non-blocking; no finding rewrites a measured verdict)

- **FR-1 (P2, disclosure accuracy — landing condition)**: decision.md §6's F04-attempt-1 mechanics conflict with the §7.1 transcription; no `gate_failed_not_killed` raw record exists for F04 (solely F06C's). Required: honest gap marker/erratum at landing stating (i) F04 attempt-1 raw bytes unrecoverable, (ii) §7.1 timeout transcription is the authoritative account, (iii) §6's gate-fail/launcher/`writer.py` text is mis-attributed (it describes F06C attempt-1), (iv) zero F04 gate-fail record survives. Rebuilt F04 evidence unaffected.
- **FR-2 (P3, claim precision)**: snapshot.py computed the 6 plan anchors under `ATT.parents[1]` (=`execution_runs`) instead of `parents[2]`, so those 6 anchors are `missing:true` in BOTH snapshots and the `26/26 anchors identical` claim = 20 hashed anchors + **6 missing==missing (vacuous)** (changes.diff's `anchors_identical=20` is the honest count). I re-hashed the 26 intended files at corrected paths — **0 mismatches** (6/6 match their binding/input_pins). Non-blocking; land the corrected wording "20 hashed + 6 pin-verified by reviewer".
- **FR-3 (P3, transcription)**: `exit_declaration_verbatim` deviates from the card by one ASCII space in its final clause (`先 blocked` vs `先blocked`); the first sentence and matrix L58 are byte-exact.
- **FR-4 (info, wording)**: oracle §4's F01 recovery cell reads "+1 sim fetch" while the measured provider delta is +2 (1 sim discover + 1 sim fetch, decision §4 reports it honestly); downloads are exactly +1 as frozen — wording ambiguity only, no masking (域：1 oracle cell wording).

## 10. Scope of acceptance (per-cell table per my rulings)

| cell | matrix-row evidence (clauses 2-5) | frozen extra checks | reviewer disposition |
|---|---|---|---|
| F01 | PASS (trigger/chain/no-pseudo-raw/+1-download/gap-visible) | 20/20 true | **accepted** |
| F02 | PASS (raw preserved, no handle, 0 downloads; D-1 recorded non-gating) | 15/15 true | **accepted** |
| F03 | PASS (real 34.515 s lock-wait, catalog_busy, idempotent recovery) | 11/11 true | **accepted** |
| F04 | PASS (gate-clean kill, 4242 visible, recovery registers, raw intact) | 17/17 true | **accepted** + FR-1 gap marker attached |
| F05 | PASS row; clause3-cause-**FAIL** = F-F05-cause | 18/18 row checks true | **accepted** as row-PASS + clause3-cause-FAIL recorded (ledger) |
| F06A | row PASS (visibility, append-only 1→3, p0 intact, chain ok) | audit checks FAIL = product defect | **accepted_scoped**: measured red retained (no re-gate), NON-BLOCKING per §6 |
| F06B | row PASS (row+json/md-absent ⇒ not consumable, 1→4, chain ok) | same | as F06A |
| F06C | row PASS (complete-never-half, scoped kill, 1→4, members identical) | same | as F06A |

**Ledger routing at landing**: F-F06-audit + F-F05-cause → REMEDIATION ledger (fixes NOT this card's surface). **Inherited carries stay open upstream** (not this card's surface): I-07-B F1/F2/F3/J6, I-09-C F12/F5, production I-16/I-17 pending; `disclosure_adaptation=unmapped`, `accuracy=unproven` unchanged. **Cleanup authorized after landing** per recovery/README §2 (`%TEMP%\i07d\**`, `evidence/wprobe_tmp/**`, iso/venv if archived) — my own `%TEMP%\i07d_review\` helpers may be deleted with it (域：3 cleanup scopes).

## 11. Unverified / limits (carried)

- F01 fixture candidate fields remain C-level (lifted from production metadata observation; no live-provider validation in this card).
- Share-none hold semantics rely on observed Win32 `CreateFileW(ShareMode=0)` behavior in this environment (outputs verified; OS semantics not re-derived).
- F05 `production_observation_copy` row schema equality vs production is asserted via `content_sha256`+row dict (I confirmed the cell file hash equals production `normalized.md` `980ea4f8…`; full row-dict schema diff not re-run).
- F06C attempt-1 child pid 44784's death mechanism after the launcher kill is not recorded (no exit record; dead by census-after and by my live scan — no stray alive).
- Side/inherited observations remain open: HK canonical filename divergence (D-3), `document_fingerprint_state+1` during F05 fault, `producer_events.event_type='llm'` label for the extractive summary (cosmetic, out of card scope).

## 12. Boundaries at MY close — VERIFIED

- **Anchors**: 20/20 hashed product+config anchors — sha(before)==sha(after)==sha(now) AND mtime_ns(before)==(after)==(now), **0 mismatches**; 6/6 plan inputs re-hashed at corrected paths match pins ⇒ **26 intended anchors, 0 mismatches** (with FR-2's count caveat).
- **Samples**: 3/3 raw + 3/3 sidecar + 2/2 CN derived files — before==after==now, `01819e1c…` / `ffd73376…` / `e3de0053…` (域：3 samples re-hashed by me).
- **Production catalog (stat-only, I never opened it)**: main `bytes=49677344768` + `mtime_ns=1789799495406919100` identical before/after/now; `-wal` bytes+mtime identical (`0`/`1790121578113891700`); `-shm` bytes unchanged `32768`, mtime drift `1790180754917664300`→`1790185152460690800` (= 17:39:12Z, the disclosed F05 read-only observation SELECT moment), and shm_now == shm_after (my stat introduced no further drift). Disclosed WAL-reader side-effect confirmed; matches changes.diff header.
- **No network**: no web/network tool used by me; their commands.json declares network disabled per command + CMD-D-NOT-RUN; harness grep shows only fixture `source_url` literals, no client code (域：0 network calls by reviewer or declared runs).
- **No git**: I ran no git; their snapshot records `production_porcelain_note: git is NOT run`; CMD-D-NOT-RUN lists any git command (域：0 git mutations).
- **My runs**: helper scripts only under `%TEMP%\i07d_review\`; all product/catalog access by me was read-only (`mode=ro`+`query_only` on the **scratch** F05 cell only; production catalog stat-only); I killed/locked nothing; my live process query was read-only and returned only my own tool subprocesses (域：0 real workers touched by reviewer).

## 13. REM-79 self-check + report integrity

- REM-79 self-check: `REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py` v1.2.0-correction2 run on this file with `PYTHONIOENCODING=utf-8` → **0 violations across 1 file, exit 0**（域：本报告）.
- Deliverable pair: `reviewer_report.md` + `reviewer_report.sha256` (hash written after this text; sidecar format `<sha256>  reviewer_report.md`).

— end of report —
