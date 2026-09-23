# I-07-B review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; never self-signed)

Status: **`ACCEPTED_SCOPED`** (attempt `a20260923-01`). The independent reviewer (独立复核) wrote
the verdict in `reviewer_report.md` — the byte-pinned carrier — **not** in this file. This file is
the carrier-landing bookkeeping landing of that verdict: it transcribes the verdict, its settlement
conditions and its carry-scope so the attempt's `review.md` slot exists. **It is a pure bookkeeping
transcription: it adds no acceptance of its own.** Read `reviewer_report.md` itself (§0–§13) for the
reviewer's own words. No verdict, review, or acceptance was authored in this pass.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this file
was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **I-07-B / attempt `a20260923-01`** (`<PLAN>\execution_runs\I-07-B\a20260923-01`).
- Verdict: **`ACCEPTED_SCOPED`** — the reviewer's literal label is at carrier **line 14** (§0
  "Verdict", lines 12–26): "**ACCEPTED_SCOPED** — the nine-step delivery is reproducible, its
  measurements hold under independent re-derivation, its disclosures are backed by artifacts, and
  its exit-honesty face is intact. Acceptance carries the conditions and carry-scope in §11 (one
  non-blocking pin-annotation defect, reviewer finding F5, settled with the report; F1/F2/F3/F4
  carried downstream as parent/parent-upstream scope — not this card's fix surface; I-00-B
  anchor-table refresh is a dispatcher/parent action)."
- Basis (carrier lines 20–26; N=12 independently measured): 12/12 handoff-pinned
  deliverable+evidence hashes re-computed and matched; oracle CreationTime precedes the first
  judged run; the reviewer's WPROBE re-run reproduced `evidence/wprobe.json` byte-identically
  (`e01c8c90…`); the frozen-argv S-CN-2 run1 re-run reproduced each comparison field including the
  stderr byte-hash; F1/F2/F3 each verified against live product code AND raw run evidence; zero
  three-market-pass sentences; every simulated event labelled `simulated:true` (42 spy events in
  this attempt); production catalog identity, 20/20 anchors, and 3/3+3/3 sample hashes unchanged
  across the attempt and still unchanged at review time.
- Verdict author: **独立复核** — the delegated independent review subagent (parent session
  `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`), N=1 signer (carrier lines 1–10). The
  implementer did not and cannot self-sign: during review the carrier re-verified
  `handoff.json` `status=review_pending`, `implementer_signed=false`, `reviewer_status=PENDING`
  live (carrier lines 3–5) — this pass measured the same pre-image before touching the record:
  **17173 B / sha256 `37bb946a03c4bc3419cf7691c320d6271950c9596dcb36edf4c6d894d5dea440`**,
  status `review_pending`, `implementer_signed: false`.
- Settlement conditions + carried scope: carrier §11 (lines 333–348), transcribed as (j) below.
  F5 is settled by the one-line annotation described in (i).
- This pass **does not self-sign**: `implementer_signed: false`,
  `implementer_never_signs_acceptance: true`; the verdict is **transcribed, not authored**; this
  file is a **bookkeeping transcription, adds no acceptance of its own**.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` (single round; verdict `ACCEPTED_SCOPED`) |
| path inside attempt | `execution_runs/I-07-B/a20260923-01/reviewer_report.md` |
| sha256 | `fc96bb0bec1051412a528b4a372732fb5da27f574987e34c9c9913fd471099be` |
| bytes | 31450 (matches the dispatch figure exactly) |
| lines | 376 (UTF-8 without BOM; LF-only, 0 CR; single trailing LF) |
| pin sidecar | `reviewer_report.sha256` (present, 85 B, sha256 `23a6f9ae85f329e303c951ebf1603acca29dacef69603dad7e47fb9fb65827dd`, content `fc96bb0bec1051412a528b4a372732fb5da27f574987e34c9c9913fd471099be  reviewer_report.md` + LF) — **content-match**: equals this pass's independent read-only re-hash ⇒ 0 bytes written |
| verdict line | 14 (`**ACCEPTED_SCOPED** — the nine-step delivery is reproducible, …`), byte region start 821 .. end_incl 923 (103 B), sha256 `7f0c13b1a9103bbaac5ddf87b27d7bdf9c14a52cef9244fe7c002e577930aa8a` |
| header + method lines (independent reviewer, no self-sign) | 1–10 (bytes 0..803, 804 B, sha256 `71ca8bf417752de2d6704193b5dab6b7a13993c42f1da6b89275055ce62c1952`) |
| verdict section (§0) lines | 12–26 (bytes 806..2023, 1218 B, sha256 `6f9a5eb94cec54589596969b22670783ed22de4d18fa4b1467383058bacfa5a7`) |
| findings (§4: F1/F2/F3) lines | 140–191 (F1 = 142–156, F2 = 158–173, F3 = 175–191) |
| reviewer-added finding F5 (§10) lines | 317–331 (bytes 26882..28179, 1298 B, sha256 `b8642dacb552c4201b807829883e012c67f88a765f1fa537f2be31c73cb3d5fc`) |
| conditions + carry-scope (§11) lines | 333–348 (bytes 28182..29464, 1283 B, sha256 `29189308ee48f0b7b7901d2a23bc6f7fd01d9b47733d24da22393e4c8a118790`) |
| unverified list (§12) lines | 350–364 (bytes 29467..30634, 1168 B, sha256 `8d94437c04e2ed00fceddbb6bf4619cd3dbd97c638e87f572cb80368965754ce`) |
| boundary (§13) lines | 366–376 (bytes 30637..31448, 812 B, sha256 `e9a03e20285ccc892937545dd367fcb0eab53e15dd565c4fa9a32bca1b0f9a5f`) |
| producer | independent reviewer (独立复核) only — never the implementer, never this file's author |

Section line map (for audit): §1 28–46, §1a 48–58, §2 60–84, §3 86–99, §3a 101–109, §3b 111–138,
§4 140–191, §5 193–220, §6 222–254, §7 256–279, §8 281–287, §9 289–315, §10 317–331, §11 333–348,
§12 350–364, §13 366–376 (byte offsets are 0-based against the file at the recorded sha256;
multi-line regions include internal LFs and exclude the final LF).

Verification at landing (read-only): length **31450 B** ✓; independent re-hash **`fc96bb0b…99be`**
✓ equals both the dispatch figure and the sidecar value; **376 lines** ✓; line 14 reads
`ACCEPTED_SCOPED` ✓. **No byte of `reviewer_report.md` or `reviewer_report.sha256` was changed by
this pass (0 bytes to either).**

## (a) §1 Deliverables — 12/12 pins + frozen-first timing (carrier lines 28–58)

- **12/12 handoff-pinned deliverable+evidence hashes re-computed and matched** at review time:
  oracle.md `b92b6650…`, binding.json `2f4b7f40…`, commands.json `6e0f2e57…`, decision.md
  `a538c411…`, changes.diff `3fa4e5d8…`, recovery/README `0e1b5e1f…`, after/case_results.json
  `72cf2bfb…` (handoff self-excluded, n/a) **plus** the pinned evidence: wprobe.json `e01c8c90…`,
  live/reachability.json `38008149…`, snapshot_before `138795f2…`, snapshot_after `b50563a2…`,
  plan_anchor_hashes `9c182fac…`.
- **Frozen-first timing**: oracle.md CreationTime 07:19:36 < wprobe 07:31:37 < first judged run
  07:33:17 — the oracle was frozen before any judged run; binding/commands written pre-run
  (07:29:22) with the argv contract + `counter_wiring` + `anchor_drift_vs_I00B` present.
- **§1a commands scan**: registry holds exactly the I-00-B-bound entry form plus harness
  bookkeeping commands; self-describing `exit_code_legend`; grep for `git` = 2 hits, both
  non-verbs ("difflib; no git", "NOT USED as a bound command") ⇒ **zero git verbs**; the one
  disclosed pre-binding `git diff --no-index` deviation (J7) appears verbatim-consistent in 3/3
  locations (binding.forbidden, decision §6 J7, handoff `git_command_deviation`).

## (b) §2 C1 — the card's hard red line, confirmed PASS (carrier lines 60–84)

- **Count-on-entry wrapper**: `harness/spy/sitecustomize.py` `_wrap()` installs a `wrapper` that
  calls `_event(counter, …)` **before** `return original(*args, **kwargs)` (lines 71–79) — the
  count fires on entry, before delegation; activation gated on `I07B_SPY_DIR` only. Frozen-sim
  replacement functions likewise emit their event before serving fixture bytes and hard-code
  `"simulated": True` (lines 133–135, 167–169).
- **Wiring**: 18 targets frozen in `binding.counter_wiring`, all `status:"wrapped"` in
  `evidence/wprobe.json.wiring` and in every per-case `counters/wiring.json`.
- **WPROBE**: `zero_insert_proof=true`; `counter_totals_after_probe` = scan 2 / read 2 /
  provider 2; throwaway product-schema catalog rows byte-identical before/after (18 tables, zeros
  except catalog_meta=1); 18/18 wrapped; producer wiring proven by wrap status (disclosed: no
  inert producer invocation exists).
- **INSERT only in `build_iso.py`** (isolation construction; its `inserted[t] += rowcount`
  bookkeeping lands in `initial_state.json.rows`, never in a counter); **`SELECT COUNT(*)` only in
  `catalog_counts()`/`catalog_counts_dir()` for *state* deltas** (run evidence) — never feeding
  the four counters; reported counter values come solely from counting `events.jsonl` lines
  (`run_case.py:92-103`). No artifact/producer_events INSERT feeds any reported value.

## (c) §3 The reviewer's own two %TEMP% re-runs (carrier lines 86–138)

Method adaptation (disclosed): the documented argv forms write evidence under `<attempt>`, outside
the reviewer's write boundary ⇒ the harness was mirrored **byte-identically** to
`%TEMP%\i07b_review\harness\` (`run_case.py` `9756b59a…`, `spy\sitecustomize.py` `58da8b36…` both
hash-equal to the attempt copies), reached through a directory junction to the attempt's own
`iso\venv` (Python 3.13.9); PYTHONPATH, `I07B_SPY_DIR` semantics and cwd-analog unchanged;
outputs landed in `%TEMP%\i07b_review\evidence\`.

- **WPROBE re-run**: harness rc 0; `zero_insert=true`, totals **scan 2 / read 2 / provider 2**,
  18/18 wrapped, row-count diffs `[]`. Strongest agreement form: the reviewer's produced
  `wprobe.json` sha256 = **`e01c8c905d65609dad150df36a95cd2d4207b415450387a24bc3dc6537aef96c`
  — byte-identical** to the attempt's own `evidence/wprobe.json` and to the handoff pin.
- **Frozen-argv case re-run — S-CN-2 run1 (the F1 cell)**: harness rc 0 (94.7 s); **field-by-field
  all match**: product_returncode 3=3; **stderr sha256 `57a7b0b47590ee56ad7b5efd38f6ea84739e0d4c8bf5b2c3cf22ef08a2b9ffba`
  byte-equal**; stdout `e3b0c442…` (0 B) = 0 B; counter_delta/totals `{}`/`{}`/`{}` = `{}`;
  catalog_count_delta `{}` = `{}`; raw re-hashed unchanged `01819e1c…f343d`; stages identical
  JSON; refusal.parsed_fields `{error: "…no_existing_source_satisfies_request…", error_code:
  "upstream"}` = same; deep_verification skip = same. Counters dir: `event_lines: 0` before and
  after, equal to their run1/run2 baselines.
- **Iso snapshot unchanged after the 3rd invocation**: after the reviewer's (3rd) invocation of
  the S-CN-2 catalog it is still **byte-identical to `initial_state.json.iso_snapshot`**
  (`631eb434…`, re-hashed by the reviewer) and its 18-table counts equal
  `run1.catalog_counts_before` (independently SELECTed read-only: `EQUAL: True`) — C3 idempotency
  bonus for free.

## (d) §4 The three findings — independently confirmed (carrier lines 140–191)

- **F1 — entry resolve/ensure never scan — CONFIRMED** (code map re-read against live bytes):
  `resolver.py` has **zero** `scan(`/`scan_catalog` occurrences; `SourceResolver.resolve` starts
  from `query_filing_candidates` (SQL-pushdown SELECT, strict read-only, no filesystem walk);
  read-only `ensure` (`cli.py:753`) calls `resolve` solely, `acquisition_service.ensure` never
  calls a scanner; sole registration entry = `service.scan → scan_catalog` dispatched from the
  `scan` subcommand only. Corroboration: S-*-2 both runs `catalog_count_delta={}`, scan counter 0,
  refusal `missing / no_existing_source_satisfies_request` — measured and re-reproduced. Matrix
  operation "第一次从入口恢复注册" is not achievable through the current entry.
- **F2 — every refusal lacks structured actionable recovery — CONFIRMED (C2.2 FAIL)**: two
  refusal raws parsed verbatim (S-CN-1 run1 review-gate
  `{"error_code":"upstream","error":"prompt injection not reviewed … not_reviewed"}` and
  REGFAIL-HK scan1 `{"error":"database is locked","error_type":"catalog_busy","retryable":true,"status":"failed"}`);
  in both, `actionable_recovery_fields={}`, `structured_actionable_present=false`. The structured
  inventory across this attempt's refusals is exactly `{error_code,error,retryable}` or
  `{error_type,retryable,status}` — no `candidates`/`next_action`/`required`/`gap_plan` on any
  failure path. The NL explicit-missing-info arm genuinely passes (`not_reviewed`,
  `no_existing_source_satisfies_request`) — actionable in prose, not machine-parseable.
- **F3 — no review-receipt CLI → zero RevenueSourceRecord → C4 value arm unexercised — CONFIRMED**:
  full `cli.py` subcommand inventory read (scan, normalize, summarize, fingerprint_backfill,
  extract_sections, derived_audit, status, focus_cleanup, documents, identity_enrich, identify,
  query, evidence, sections-list, reconcile-retire, prune-retired, extraction-quality, duplicates,
  resolve, ensure, close-gap, import-portfolio, run, worker, plugin, install/uninstall/startup,
  activation — sole `--reviewer` flags —, runtime-policy): **zero review/prompt-injection
  subcommand**; `record_prompt_injection_review` exists solely as a Python function
  (`prompt_injection.py:263`, in-package references only; zero occurrences in RF `scripts/`).
  Zero-record evidence: across 25 final entry runs + 4 scan runs = **29 outputs, 0 non-empty
  stdout, 0 containing `reuse_receipt`** ⇒ zero RevenueSourceRecord ⇒ C4's deep-value assertions
  have nothing to check; review stage unreachable for all 3 markets ⇒ no source-preparation
  qualification yet (measured reality stricter than declaration 1, honestly so).

## (e) §5 Honesty face (carrier lines 193–220)

- **Three exit declarations, verbatim — 4/4 copies match the card**: the card's exit line reads
  `…三公司仅来源准备通过，仍未授予正式预测资格。缺一市场/真实路径不得总体写三市场通过。恢复：保留已取得raw，只回退当前隔离变更。`
  The three sentences appear byte-identically in decision §0 (lines 11–13), decision §4, handoff
  `exit_honesty_declarations_verbatim`, and oracle §0 — **4/4**.
- **OVERALL = NEGATIVE**: decision §0 "Overall three-market statement: NEGATIVE (no overall pass
  is claimed)" + handoff `overall_three_market_pass: false` with its rationale. Pass-claim grep
  over decision+handoff returns **4 hits, prohibitive-sentences only** (decision:12,17,110;
  handoff:13) — **zero sentences assert a three-market pass**.
- **S-*-3 caveats**: all three rows say "matrix criteria PASS at C level" (C-only; the chain still
  refuses at review); the HK canonical-name open item is disclosed in decision §8 AND handoff. The
  reviewer **verified the filename themselves (亲验)**: isolated file
  `2026-04-28_hkexnews_12127452_小米集團－Ｗ 2025年度報告.pdf` (4 405 561 B) vs manifest
  `2026-04-28_hkexnews_12127452_2025年度報告.pdf` — differs exactly as disclosed; registered-identity
  re-derivation stays open (§12).
- **L rows BLOCKED ×3**: decision and handoff both record L-CN/L-HK/L-US blocked (unbound
  `*-NEW-MISSING` identity + no download authority) 3/3; reachability **CN 200 / HK 200 /
  US 403** (`reachable:true`, **`unreachable_markets=[]`**, header NAMES only) in
  `evidence/live/reachability.json` (re-hash matches pin); manifest's `unbound_live_samples` rule
  confirms no frozen identity exists for the L cells.
- **Simulation labels**: each `events.jsonl` scanned — **42/42 spy events carry a `simulated`
  label** (0 lacking); S-CN-3/S-HK-3/S-US-3: 10/10 lines `simulated:true` each, provider events
  4/4 per case with 0 unsimulated; other cases' scan/read events `simulated:false`; the single
  live network call is the separate reachability probe (never in spy events). No simulated event
  masquerades as live; no spy event unlabeled.

## (f) §6 Isolation / production integrity (carrier lines 222–254)

- **Production catalog identity**: before/after snapshots both `bytes=49677344768`,
  `mtime_ns=1789799495406919100`; the reviewer's **live re-stat only (N=0 opens)**:
  FILETIME `134342730954069191` → (−116444736000000000)×100 = **1 789 799 495 406 919 100 ns —
  exactly the claimed mtime_ns** ⇒ the production database file is bit-identical to the
  pre-attempt state at review time.
- **`-wal` 0 B** in both snapshots and live (mtime unchanged); **`-shm` 32768 B in both — size
  constant**, mtime_ns advanced (read-only-open shm-index effect, disclosed; probes ran
  `PRAGMA query_only=ON`; no write statement ever issued).
- **Anchors 20/20**: programmatic before-vs-after comparison: 20 valid, 20 identical, 0 changed
  (the 6 plan-input anchors carry `missing:true` — the J8 path bug). Includes
  `source_preparation.py 91a6dc32…`, `fetch_filing.py 046cc7dc…`, `store.py 1a783240…`,
  `CW/config/source_catalog.yaml f9eb72a6…`; live re-hash at review time still equals the AFTER
  values.
- **Samples 3/3 + 3/3** raw and sidecar `match=true` against the frozen manifest at **both**
  ends (CN `01819e1c…`/`7f7570fe…`, HK `ffd73376…`/`8228741d…`, US `e3de0053…`/`1cbfb1a2…`).
- **RF porcelain = exactly 5 entries, pre-existing + untracked**: ` M REMEDIATION_REGISTER.md`
  and ` M progress.md` (both mtimes pre-attempt, parent's register round), `?? execution_runs/I-07-B/`
  (this attempt's own new work), `?? .tmp-r41-mutation/` (2026-09-20),
  `?? assurance/…/plan_inputs.json.bak` (2026-09-21) — **zero product paths modified**,
  consistent with `product_files_written: ZERO`.
- Per-case freeze (C1.1): per-case `initial_state.json` (asset sha256, iso file-list hashes,
  populated-table counts, worker_control absent), full 18-table pre-run counts in each
  `run1.catalog_counts_before`, `iso_base.json.schema.table_count=18` from the product's own
  `CatalogStore._initialize` — the reviewer re-counted the isolated S-CN-2 catalog: 18 tables,
  counts equal.

## (g) §7 Drift + §8 Disclosures (carrier lines 256–287)

- **4 drift anchors re-hashed live, all match**: `source_preparation.py 5ec16eaf→91a6dc32`
  (difflib diff 28 lines = the W05-B receipt line, read and verified);
  `revenue_forecast.py 6b3d960e→2a2dfede` (**`revenue_forecast.py.diff` = 0 lines after newline
  normalization ⇒ EOL-only**, as claimed); `CW cli.py 2f5c5740→fad88c60` (content diff honestly
  declared non-reconstructable without git); plus the I-06-A-era drifts
  `filing_fetch_client 9329f331→b281e6d1`, `company_wiki_source aeeb7b2a→7d1bd8f9` (257-line
  diff) — live = anchor snapshots. **The drift is upstream time, not this card's doing**; 20/20
  anchors + production identity + 6/6 samples unchanged.
- **J7**: the two `evidence/anchor_drift/*_old_vs_current.diff` files (mtime **07:15:51 <
  binding 07:29:22**) contain genuine `diff --git a/… b/…` headers = the **pre-binding git-no-index
  outputs, retained**; the binding-referenced `*.py.diff` files (mtime 07:16:51) are **difflib
  format** (`--- I-00-B-era:` / `+++ current:`) = the CMD-I07B-DRIFT **replacement**; commands.json
  holds no git verb; disclosure accurate in **3/3 locations** (timing, replacement, no-repo-state
  all check out).
- **J8**: both snapshots **still carry `missing:true`** on the 6 plan-input anchors — captured
  observations **not rewritten** (their pinned hashes match live ⇒ not re-emitted after the bug
  was found); the corrected `evidence/plan_anchor_hashes.json` was **re-derived live 7/7 equal**:
  card `bd09eb6c…`, scenario_matrix `0dec23cd…`, manifest `d5d0bb92…`, I-00-B binding
  `fdb2a598…`/commands `f8a397ec…`/oracle `e9c82fe4…`, START_HERE `5c6e111f…`.
- **J9**: **three superseded fix generations present** — `S-CN-3`/`S-HK-3`/`S-US-3` each retain
  `run2.pre_scaffold`, `run2.pre_scaffold2`, `run2.pre_fix2`, `run3.pre_scaffold`,
  `run3.pre_scaffold2`, `run3.pre_fix2` beside the final `run2`/`run3`, with their rc/counters
  kept in case_results (rc 3 each, not hidden). **Coherent timeline**:
  `build_iso.py` 07:33:12 → 11 × `initial_state.json` 07:33:17–26 → superseded run dirs
  07:38–07:48 → `adapter_scaffolding.json` 07:45:47 → `make_fixtures.py` 07:49:30 → final S-3
  run2/run3 07:49–07:52; **no oracle change after any run** (oracle hash unchanged from pre-run
  pin).

## (h) §9 Oracle §7 attack list — items 1–7 executed (carrier lines 289–315)

1. **Re-derive a raw sha256 + initial_state counts** — S-CN-2 re-run re-hashed the isolated CN raw
   `01819e1c…f343d` (79 925 886 B) before and after; snapshots re-hash 3 production raws + 3
   sidecars (3/3+3/3 both ends); isolated S-CN-2 catalog re-counted read-only: 18 tables, counts
   equal to `run1.catalog_counts_before`; catalog file hash = `initial_state.iso_snapshot`
   `631eb434…`.
2. **Counters are call-wiring** — `sitecustomize.py` read (b), WPROBE reproduced byte-identically
   (c), grep shows no counter path touches an INSERT (b).
3. **C3.2 duplicate registration** — REGFAIL-HK scan1 under lock: rc 1, `scan:1`, catalog delta
   `{}` (0 rows); scan2 after release: rc 0, `scan:1`, `read:2`, delta
   `documents+1, entities+1, locations+2, sources+2, roots+1, document_entities+1, scan_runs+1`,
   provider absent (=0, no re-download); both entry runs delta `{}`; S-3 run3 grows only
   `document_fingerprint_state+1` — never documents/sources/locations. No second registration of
   the same version exists.
4. **C4.1 re-hash a produced record** — **N/A**: zero RevenueSourceRecord exists (F3); no
   canonical_path to re-hash; honest skip recorded in every run's `deep_verification.skip_reason`;
   the value arm stays unearned (gated by the review receipt, not by this card).
5. **Attack the refusals** — two refusal families parsed; structured actionable recovery absent in
   both (F2); NL arm genuinely specific ⇒ **C2.2 FAIL exactly as declared**.
6. **Attack §0** — grep over decision+handoff: **4/4 prohibition-sentence hits**, and
   `overall_three_market_pass` is literally `false`.
7. **Attack simulation labels** — **42/42** spy events labelled; **12/12** provider events in the
   three sim runs `simulated:true`; no provider event outside those runs; the live probe recorded
   separately with statuses.

## (i) §10 F5 = CRLF variant proven — SETTLED by annotation (carrier lines 317–331)

- **The defect**: `handoff.json.input_hashes` pins `I-07-A/after/state_matrix.json` as
  `dc72776f…` while the live file (mtime 2026-09-20 15:47:06, untouched during this attempt)
  hashes to `de784cb2f94cb2ed7a3b13a315063fb4fc7b746519db939ea58e6707abbe8684` — also what this
  attempt's own `plan_anchor_hashes.json` records.
- **Proven, not guessed**: `sha256(LF→CRLF of disk bytes) == dc72776f…` **byte-exactly** — the
  pin is the **CRLF variant of the same content** (disk is pure LF), inherited verbatim from
  I-07-A's handoff/review pins (both contain `dc72776f…`). **Content-identical**; the defect is
  only that the pin shipped without its EOL-domain annotation (two conventions for one file in one
  handoff). Known **REM-86 / REM-79 EOL-pin class, not content drift**. No measurement, verdict,
  or frozen input depends on it (state_matrix consumed read-only; decision §5 does not cite the
  pin).
- **Settlement executed by this landing (the only record edit beyond status flips)**: the row now
  carries `eol_domain_note: "pin = sha256(LF->CRLF(disk bytes)) variant; content-identical to
  disk LF value de784cb2f94cb2ed7a3b13a315063fb4fc7b746519db939ea58e6707abbe8684; inherited from
  I-07-A handoff; REM-86 class; no measurement or freeze input depends on this pin"` —
  **the original pin value is retained (annotate, not silently re-pinned)**. Handoff hash
  before annotation `37bb946a…ea440` (17173 B) → after annotation `610172ee…7897` (17466 B);
  JSON re-parsed.

## (j) §11 Verdict conditions and carry-scope — the verdict is accepted WITH these (carrier lines 333–348)

1. **F1/F2/F3 are downstream/parent findings — carried, NOT this card's fix surface**: **F2 →
   I-06-A's unsigned OPEN-5 structured-recovery contract**; **F3 → the D-W06 review-CLI gap**
   (OPEN-4 unsigned); **F1 → the entry-vs-`cli scan` registration gap the owner must route**.
   F4 (L cells blocked ×3) stands as measured; matrix cells recorded NOT-passed stay NOT-passed.
2. **I-00-B anchor-table refresh = parent/dispatcher action** (J6 drift: source_preparation,
   revenue_forecast, CW cli; CW cli content diff reconstructable solely where copies exist).
3. **Exit-honesty declarations carry into any downstream use**: the three verbatim sentences,
   `overall_three_market_pass=false`, and the stricter measured fact (zero RevenueSourceRecord)
   must accompany any citing artifact.
4. **F5 settlement annotation** — one line at settlement (done, item (i)).
5. **Retention**: `%TEMP%\i07b\cases` and `evidence/wprobe_tmp` may be cleaned **solely after this
   sign-off** (this review IS the sign-off — cleanup authorized); the superseded `*.pre_*`
   evidence dirs plus the attempt evidence must be kept.

## (k) §12 Unverified / remaining open — 10 items carried (carrier lines 350–364)

1. HK-3 **registered hash identity** not independently re-derived (the name difference itself was
   亲验, §5) — stays open as decision §8 says.
2. `document_fingerprint_state+1` on S-3 run3 — observed, not root-caused.
3. Producer counter: **wiring status only** — zero producer invocations in this attempt, so no
   invocation-proof exists.
4. S-*-3 **frozen-sim arms not re-run** by the reviewer (artifacts verified instead).
5. REGFAIL **lock arms not re-run** by the reviewer.
6. The **live probe not re-run** by the reviewer.
7. The **snapshots not re-run** by the reviewer.
8. **I-07-A-side provenance of the CRLF pin** (whether upstream pinned pre-normalization bytes)
   not investigated — out of this card's scope; F5 records just the reproducible fact.
9. **CW cli `2f5c5740→fad88c60` content diff** remains non-reconstructable without git (J6).
10. **Attempt evidence uncommitted** (`?? execution_runs/I-07-B/`) — committing is the
    parent's/owner's action (no state-changing git by this review).

Also carried from the attempt's own decision §8 (already in handoff `open_questions`): the six
corrected plan-anchor hashes are post-run captures of read-only inputs; `read=2` per resolve was
not individually attributed to `_sha256_of_file` vs `_read_verified_bytes`.

## (l) §13 Boundary compliance (carrier lines 366–376)

- The reviewer wrote **exactly two files** in the attempt (`reviewer_report.md`,
  `reviewer_report.sha256`); run outputs into `%TEMP%\i07b_review\**`; isolation state reused per
  recovery README (review re-run authorized); RF/CW/FF product trees read-only; **production
  catalog never opened (stat solely)**; git: one read-only
  `git --no-optional-locks status --porcelain=v1` required by the brief (no index/repo state
  changed); **never self-signed**. REM-79 self-check run over the report bytes; the sidecar pins
  the checked bytes.

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; no three-market pass
(overall = **NEGATIVE**); no formal prediction qualification (declaration 1 ceiling); no live (L)
market qualification (blocked ×3); no source-preparation qualification (zero RevenueSourceRecord);
`REVIEW`/`C4 value arm` remain unearned pending D-W06/I-06 work; and **this file grants nothing**
— it is bookkeeping transcription only.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-23, on the
  parent's dispatch; parent session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`.
- Verify-first (read-only, done before any write): report **31450 B** / re-hash
  **`fc96bb0bec1051412a528b4a372732fb5da27f574987e34c9c9913fd471099be`** == dispatch figure;
  sidecar **content-match**; verdict `ACCEPTED_SCOPED` at line 14; handoff pre-image =
  **`review_pending` / `implementer_signed: false`**, 17173 B /
  `37bb946a03c4bc3419cf7691c320d6271950c9596dcb36edf4c6d894d5dea440`.
- **F5 settlement fix applied FIRST** (the only record edit beyond status flips), then this pass
  wrote **exactly three files**: `review.md` (created, this file), `handoff.json`
  (`status` → `accepted_scoped` + `status_before_bookkeeping_fix` + `status_authority` +
  `bookkeeping` + carried findings F1/F3/F5 + carry scope + four stale pre-verdict fields
  superseded under `*_historical_pre_verdict`; pre-existing content otherwise untouched), and
  `evidence/I-07-B/qualification.json` (created).
- Zero bytes written to `reviewer_report.md` / `reviewer_report.sha256`, to product or production
  trees, to any frozen or historical evidence, or to any git state. **No self-signing anywhere**;
  the verdict was written by 独立复核 and is transcribed here, never re-authored.
