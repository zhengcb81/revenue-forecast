# I-07-D review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; never self-signed)

Status: **`accepted_scoped`** (card `I-07-D 故障矩阵与断点恢复` / attempt `a20260923-01`). The
independent reviewer (独立复核) wrote the verdict in `reviewer_report.md` — the byte-pinned
carrier — **not** in this file. This file is the carrier-landing bookkeeping of that verdict: it
transcribes the verdict, the two rulings (§6/§7), and in substance the carrier's verification
sections, findings register, unverified list and per-cell scope, so the attempt's `review.md` slot
exists. **It is a bookkeeping transcription, adds no acceptance of its own.** Read
`reviewer_report.md` itself (142 lines) for the reviewer's own words. No verdict, review, or
acceptance was authored in this pass; the implementer never signs and this pass does not sign
either.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this file
was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **I-07-D / attempt `a20260923-01`** (`<PLAN>\execution_runs\I-07-D\a20260923-01`).
- Verdict: **`accepted_scoped`** — the reviewer's literal label is at carrier **line 7**:
  `` ## VERDICT: `accepted_scoped` ``, with the acceptance scope at carrier **line 9**: the
  frozen-oracle chain, the 8-cell trigger ledger, clause-3/4/5 proofs, both supersession
  disclosures and the write boundaries all survive independent re-computation from raw files; four
  findings FR-1..FR-4, none blocking, FR-1 carrying a required landing gap-marker condition; the
  two deferred product findings ruled **F-F06-audit = NON-BLOCKING (rows PASS, measured red
  retained, ledger-routed)** and **F-F05-cause = REMEDIATION-ledger route with F05 row-PASS +
  clause3-cause-FAIL recorded**; acceptance scope fixed by the per-cell table in §10.
- Verdict author: **独立复核** — the independent reviewer session dispatched by parent session
  `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`, N=1 signer (carrier lines 3–5: method =
  `read`/`grep`/`pwsh` only, no network tools, no git, helper scripts only under
  `%TEMP%\i07d_review\`, the reviewer's only writes anywhere = this report + its `.sha256`
  sidecar). The implementer did not and cannot self-sign: this pass measured the handoff
  pre-image **before any write**: **16078 B / sha256
  `2ea58a5a30c7d883e50632ab7c96b9d112edc18d7adb23a7c3cbd80e0b1d61a5`**, `status:
  review_pending`, `implementer_signed: false` — confirmed by the carrier's own line 5
  ("The implementer handoff stays unsigned (`status=review_pending`,
  `implementer_signed=false`); this report is the acceptance instrument").
- This pass **does not self-sign**: `implementer_signed: false`,
  `implementer_never_signs_acceptance: true`; the verdict is **transcribed, not authored**
  (`verdict_is_transcribed_not_authored: true`); this file is a **bookkeeping transcription, adds
  no acceptance of its own**.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` (single round; verdict `accepted_scoped`) |
| path inside attempt | `execution_runs/I-07-D/a20260923-01/reviewer_report.md` |
| sha256 | `1a1d1c0500e959012888a6c9f2d367d51412d6532a2822c813869eb08ac9a933` |
| bytes | 27858 (== dispatch figure exactly) |
| lines | 142 content lines / 143 offsets (UTF-8 without BOM; LF-only, 0 CR; single trailing LF) |
| pin sidecar | `reviewer_report.sha256` (present, 86 B, file sha256 `320c689c36f6e691520af2b3a94460f3ed04fe6589ada3dfbc0857eacfdc6d9e`, content `1a1d1c0500e959012888a6c9f2d367d51412d6532a2822c813869eb08ac9a933  reviewer_report.md`) — **content-match**: equals this pass's independent read-only re-hash ⇒ 0 bytes written by this pass |
| header + method lines | 1–5 (bytes 0..722, 723 B, sha256 `e73ab61c232c07bc31c594c98bd9609bced06b5840a3de4630baef4da93286c0`); reviewer identity 3–5 (55..722, 668 B, `cce93bab0be3dd567cd3acbf3955872572fc748961a56137debad3e871b91d1d`) |
| verdict heading line | 7 — byte region start 725 .. end_incl 753 (29 B), sha256 `e73c0ee633559827314c0517d1f2bd64fafe5bdf2fd2906d8f614e4cbd46b55e` |
| scope paragraph line | 9 (bytes 756..1377, 622 B, sha256 `db467e9317a075af4db210c19d7c250382d99fdfeefe4ef41f77170d8ffab04d`); verdict block 7–9 (725..1377, 653 B, `9fd49f28753765ae61b59a5ac67fe9060ecf613ded00a7e9623650f81c3871a6`) |
| §1 deliverables + pins | lines 13–27 (incl. FR-3 exit-declaration byte-compare at line 26: 2898..3381, 484 B, `96d82d6882bc806c5b51157a435fbad45ca2f6c5c46849088b63ab6638560005`) |
| §5 clause-5 + FR-1 line | line 63 (bytes 12426..13359, 934 B, sha256 `86a75d50be66165df1e4bd5f85784297f7c2a3c7135f548f38b7a90d459f8af1`) |
| **RULING 1 (§6)** | lines 67–82 (bytes 13864..17291, 3428 B, sha256 `634d488e2d092a02fcd8f1430079c09c8492370494bd9d1890f910074f2218c1`); heading line 67 (13864..13948, 85 B, `fb935ca2aee291a75c501dc92540a33f79203583c7f428bff4acee6153db3826`) |
| **RULING 2 (§7)** | lines 84–88 (bytes 17294..19244, 1951 B, sha256 `dea7305557c7835a34d036fa7a526c7698815300a50dcc99fb6076590f53ec30`) |
| §8 disclosures audit | lines 90–96 (bytes 19247..21385, 2139 B, sha256 `2fc35395ee9207eb52ea1b07aa7b18eb65c9aed2dbf3891c2cc548f69173ef8c`); 242/242 parse line 96 (21107..21385, 279 B, `27d41c635d3107b889e7ba5b30448418e2182f4dc4d00480c0254a7227149ae8`) |
| §9 findings FR-1..4 | lines 98–103 (bytes 21388..23053, 1666 B, sha256 `90bcc7000b83ea7bacef08533edf1cc51eb00eb32048b6d5a34b42c8ea16b45c`) |
| §10 scope of acceptance | lines 105–118 (bytes 23056..24724, 1669 B, sha256 `748d2595fa79fcb55e95503835cec8a3b07da9e5f8fe2622511099c7c240293a`) |
| §11 unverified / limits | lines 120–126 (bytes 24727..25687, 961 B, sha256 `c2ab28089703a48684c54dfdbb74b8aed73c8b23382381c24e50f23b74e80357`) |
| §12 boundaries | lines 128–135 (bytes 25690..27420, 1731 B, sha256 `bfce73d91a87241ab601484c9e57afd221b0d06e911676875ff56bacf584195b`) |
| §13 REM-79 + integrity | lines 137–141 (bytes 27423..27834, 412 B, sha256 `701e09f8be6d3252a581de89228d3ce9a8e3de40d18aa3295fb44c42090687a6`) |
| reviewer write surface | `reviewer_report.md` + `reviewer_report.sha256` only (carrier line 4, 域 §12); helper scripts under `%TEMP%\i07d_review\` (deletable with cleanup) — 0 bytes written to either by this pass |

region definition: byte offsets 0-based against the file as it stands at the recorded sha256;
multi-line regions include internal LFs and exclude the final LF.

## Key verifications (transcribed in substance from the carrier's §1–§5, §8, §12)

- **Pins (the dispatch's "7+9")**: §1 deliverable re-hash all **MATCH** — oracle
  `576ddfc5…18846` (frozen first, 27211 B), binding `30ea8a7b…4e8e`, commands
  `458c62c3…ce66e`, decision `79252379…c649d5` (pre-annotation pin), changes.diff
  `f3dfe7c7…c5908e5a`, recovery/README `65d6bebb…430ffbf`, **plus** the handoff
  `review_pending`/unsigned two-status-field check = 7 pin checks; and **9/9 per-card input
  pins** re-hashed file-by-file (matrix `0dec23cd…` incl. the 6 F rows, card_I-07-D
  `b54f4bc8…`, card_I-04-E `9f98b194…`, card_I-09-C `59e9d71d…`, sample_manifest
  `d5d0bb92…`, I-09-C oracle `ccd1ea51…`, I-09-A decision `94a27b8a…` + addendum
  `de7fa1f3…`, I-07-B oracle `b92b6650…` + handoff `e43cf258…`, I-00-B binding
  `fdb2a598…` + commands `f8a397ec…`).
- **Oracle frozen-first**: stat-based order binding `17:47:35` → oracle `17:50:26` → first
  case-state evidence `18:06:34` → first judged product run `18:09:51+` (F01 run1) ⇒ the oracle
  precedes every judged run. `oracle.md` re-hashed by this pass at landing = `576ddfc5…18846`,
  27211 B — **untouched** (FR-4 annotation went into decision.md only).
- **Trigger ledger 8/8 = 1**: `evidence/verdicts.json` F01=1 F02=1 F03=1 F04=1 F05=1 F06A=1
  F06B=1 F06C=1, `blocked=[]`; per-cell failed_checks solely `fault_audit_clean` +
  `rec2_audit_clean` on the 3 F06 cells. **Three spot raws**: F03 `lock/hold.json`
  `BEGIN EXCLUSIVE` on the cell scratch catalog held 75 s with the verdict scan window
  **34.515 s exact** (end−start arithmetic; start = lock+1.95 s, end = release−38.5 s) and
  stderr `{"error": "database is locked", "error_type": "catalog_busy", "retryable": true}`;
  F04 `state/pid_42124.json` argv+cwd both inside the F04 scratch cell with
  `barrier_42124.json`, gate checks **4/4 true**, `alive_after=false`, `kill.exit_code_set=4242`,
  product quotes `exited 4242`; F06C `pid_36224.json` (argv+cwd inside ATT) +
  `barrier_36224.json`, all checks true, rc **4242**, fault-writer exit record ABSENT (seed
  `writer_exited_29860.json` only), `fault_writer/stdout.txt` 0 B, hook `return:before` count 1.
- **Clause-3 negations from raws (3 of 3)**: F01 five-hop chain re-read hop1→hop5 with
  `http_403` + a `retryable` field surviving as text at 4 hops, empty fault stdout
  (`e3b0c442…`), raw ABSENT, downloads 0, fixture log 3 discover + 3 fetch with run1 window
  fetch=1; F02 rc0 but `completed_with_errors`/`errors:1` with the `PermissionError` cause
  quoted in both stdout report and `scan_runs.report_json`, hold 12.956 s ⊃ scan1, and
  `entry_nohandle` rc3 `not_found / source is not reusable` (empty stdout) — no consumable
  handle; F06B at fault: registry P1 row + `p1.json` present + `p1.md` ABSENT, fresh reader
  `p1 consumable=false` / `p0 consumable=true` / `chain.ok=true` / `no_mixed_package=true` /
  `tmp_files=[]`, fault stderr plain `error: [Errno 13] …` rc2. No fault run printed a
  success-looking stdout/report across 8 of 8 sub-cells (attack-list item 7 answered).
- **Clause-4 deltas recomputed from raws**: F01 fault provider +2 / downloads 0 / rows 0 →
  recovery provider +2 with **exactly +1 download** (raw `01819e1c…` == manifest) +
  documents+1 locations+2 sources+2 roots+1 scan_runs+1 then review-gate refusal rc3;
  F02 provider 0/0 both phases, raw sha unchanged; F03 provider 0, catalog delta `{}` →
  `{scan_runs+1, sources+1}`; F04 fault provider +2 with raw committed (`ffd73376…` +
  `.source.json`) and rows `{}` → recovery **provider 0**, registrations land;
  F05 fault summarize 1 / summary +0 / normalized byte-identical (`980ea4f8…`) → recovery
  summarize +1, normalize **0 calls**, artifacts 1→2 (**summary+1 only**), normalized row+file
  unchanged; F06A/B/C rows append-only **1→3 / 1→4 / 1→4** with p0 shas constant
  (`960699f4…`/`de9eee94…`), members hash-identical, no conflict. **Independent chain
  recompute** with the reviewer's own implementation of `canonical_sha256` (definition read at
  `evidence.py:139-143`): F06A 3/3, F06B 4/4, F06C 4/4 lines `line_sha256` re-derived and
  `prev_line_sha256` linked; input shas p0 `02a9502e…f35e`, p1 `f5a8413e…f0b9d` identical to
  each reader's `sha_computed`. Masking exposure: no re-download (F02/F03/F04 provider=0), no
  re-produce (normalize=0), no bulk rebuild anywhere.
- **Clause-5 kill scope**: census before **359** → after **349**, gone=25,
  **real_source_catalog_gone=0**; the killed PIDs `42124`, `36224` and F06C's launcher `49348`
  appear **nowhere in census_before** (0 hits) ⇒ **0 pre-existing processes died**; gate code
  re-read at `run_d_matrix.py:120-173`; **the sole `gate_failed_not_killed` record in the
  attempt is F06C's** `fault_writer.pre_gate_fix/result.json` (pid 44784, argv/cwd false +
  launcher_kill 49348→4242) and **none exists for F04** (→ FR-1); F06C attempt-1 child 44784
  dead with no recorded mechanism, no stray alive in the reviewer's live scan; recovery README
  §2 cleanup authorization present and its re-scan claim holds.
- **Disclosures**: F04 attempt-1 overwrite acceptably bounded — §7.1 transcription exists with
  specific values and the rebuilt cell is internally consistent (but §6↔§7.1 conflict ⇒ FR-1);
  F06C `*.pre_gate_fix` **4 of 4 preserved on disk** (`fault_writer`, `recovery1/2_writer`,
  `seed_writer`, `state.pre_gate_fix/**`); verdict-only recalcs **5 of 5 mtime-ordered** (F01
  raws ≤18:11:51 < verdict 18:46:00; F02 ≤18:20:45 < 18:29:09; F03 ≤18:30:48 < 18:46:00; F05
  same run-second 18:39:17; F06 ≤18:43:20 < 18:43:35-37) ⇒ no product raw rewritten;
  **D-1..D-4 all 4 present** (D-1 in the F02 verdict + decision §5; D-2 §5; D-3 §5 + F04
  filename_note; D-4 §5); **242 JSON files, 242 ok, 0 bad** (exact match to the 242 claim) plus
  20+ evidence files read line-by-line.
- **Boundaries at the reviewer's close**: anchors **20/20** hashed product+config anchors
  sha(before)==sha(after)==sha(now) AND mtime_ns equal, 0 mismatches; 6/6 plan inputs re-hashed
  at corrected paths match pins ⇒ 26 intended anchors, 0 mismatches (**with FR-2's count
  caveat**); samples 3/3 raw + 3/3 sidecar + 2/2 CN derived before==after==now
  (`01819e1c…`/`ffd73376…`/`e3de0053…`); production catalog **stat-only, never opened**:
  main `bytes=49677344768` + `mtime_ns=1789799495406919100` identical, `-wal` identical,
  `-shm` bytes 32768 unchanged with one disclosed mtime drift = the F05 read-only SELECT;
  **no network** (0 calls by reviewer or declared runs), **no git** (0 git mutations),
  **0 real workers touched** (helper scripts only under `%TEMP%\i07d_review\`; all product
  access read-only; reviewer killed/locked nothing).

## RULING 1 (carrier §6) — **F-F06-audit: NON-BLOCKING for the three F06 cells (option (b))** — transcribed in substance

- **Defect verified at source, line-level** in `scripts/publication_registry.py`: **L207**
  `by_generation: dict[tuple[str, str, str, str], set[str]] = {}` (keys typed as tuples);
  **L208–215** `generation = (entry["input_sha256"], engine, schema, artifact_type)` with
  `setdefault` (keys ARE tuples); **L216** `for (anchor, engine, schema, artifact_type),
  result_hashes in by_generation.items():` (unpacking proves tuple keys — the conflict branch
  itself is sound); **L228** `claimed = artifact.get("input_sha256")` → a `str`; **L229**
  `if not isinstance(claimed, str) or claimed not in by_generation:` — for any well-formed
  `str` claim the first operand is False and `str in {tuple keys}` is **always False** (a str
  never equals/hash-matches a tuple) ⇒ the `unregistered claim` branch at **L230–233** fires
  for every readable result file, registered or not. Intended check is anchor-level
  (`any(gen[0] == claimed …)`). ⇒ a **one-way false-positive generator**.
- **Same-fresh-reader contradiction measured**: `reader_after_seed_p0/authority` (F06A) and
  `reader_after_fault/authority` (F06B/C) each show `is_registered_p0=true` /
  `is_registered_p1=true`, `registry_path_match=true`, `chain.ok=true` while
  `audit_problems=[unregistered claim … never registered]` for p0/p1 — 3 of 3 readers
  contradicting their own audit.
- **Row evidence is NOT tainted** — `harness/d_reader.py` read in full (247 lines):
  `consumable` = json-exists ∧ md-exists ∧ parse ∧ recomputed-input-match ∧
  registry-result-match ∧ chain-ok (L187-190); chain recompute (L95-121) and input recompute
  (L73-86) never call `audit()`; `is_registered` (product L188-190) is a correct string
  comparison. The buggy branch can only *add* a spurious problem line; it cannot suppress the
  correct conflict branch (L216-221, which emitted zero `conflict:` lines), alter reader
  consumability, alter chain linkage, or delete history. **Reviewer recomputed all 3 chains
  independently: 3/3 + 4/4 + 4/4 lines hash_ok + link_ok, input shas p0=`02a9502e…`,
  p1=`f5a8413e…`.**
- **Posture, both halves**: (1) the implementer's **KEEP-RED is CORRECT and stays** — do NOT
  re-gate `fault_audit_clean`/`rec2_audit_clean` to true; `audit_problems==0` was frozen in
  oracle §2 before results, measured ≠ frozen is recorded as measured (`all_ok=false` on the 3
  cells stands; no retry-to-green); this is exactly the I-09-C F12 handling, whose register
  disposition is "F12 保留不阻断验收". (2) The red is **NON-BLOCKING for this card** — a
  product defect outside this card's surface (fix = publication-registry track), routed to the
  **REMEDIATION ledger** as product finding **F-F06-audit** (`publication_registry.py:229`,
  suggested class: audit false-positive / operator-CLI trust), fixes NOT part of this card.
- **Disposition**: F06A/F06B/F06C = **row-PASS + frozen-audit-check FAIL (product defect),
  measured red retained, non-blocking** — matrix rows (visibility, idempotent recovery, no
  history deletion, trigger location/count) all PASS on evidence that does not flow through
  L229.

## RULING 2 (carrier §7) — **F-F05-cause: REMEDIATION-ledger route; F05 = row-PASS + clause3-cause-FAIL recorded; NOT blocked** — transcribed in substance

- **Defect verified at source**: `company-wiki/src/company_wiki/source_catalog/summarizer.py:
  164-170` — `markdown = normalized_path.read_text(...)` inside `try`, `except (OSError,
  UnicodeError): failed += 1; continue` — the swallow happens **at the source**: no log, no
  re-raise, no persistence of type/text/code/retryability.
- **Measured**: fault stdout `{"completed":0, "failed":1, operation:"summarize", …}` counts
  only (0 B stderr); recovery stdout `{"completed":1, "failed":0}`; hold window 1.744 s ⊃ the
  fault run (single variable = the lock); the reviewer's own `mode=ro` + `query_only` scan of
  the F05 cell catalog: `producer_events` has no error-ish column and its 2 rows are the seed
  normalized event + the recovery summary event — **the failed attempt persisted nothing**;
  a column sweep across **all 18 tables** for error/cause/reason/message/retry fields with
  values returned **empty** ⇒ **clause-3's `错误cause/code/retryability不丢失` genuinely FAILS
  at the F05 origin**, honestly pre-registered and recorded
  (`verdicts.json.F05.cause_survival=FAIL`) — a genuine honest FAIL, not an evidence gap.
- **Routing**: REMEDIATION ledger as product finding (same class/track as C1 / F-REV-7),
  owner = CW producer track (`summarizer.py:168`), fix NOT this card's surface.
  **Posture**: F05 cell = **row-evidence PASS** (真实状态保持 failed:1 honest + 需求可追踪 by
  report counter & summary-absence + recovery 仅补缺项 verified) **with clause3-cause-FAIL
  carried as the ledger finding** — **not `blocked`, not a cell-red**.

## Findings register FR-1..FR-4 (carrier §9 — dispositions transcribed; none rewrites a measured verdict)

| id | severity | finding (substance) | disposition at this landing |
|---|---|---|---|
| **FR-1** | P2, disclosure accuracy — **landing condition** | decision.md §6's F04-attempt-1 mechanics conflict with the §7.1 transcription; no `gate_failed_not_killed` raw record exists for F04 (solely F06C's) | **LANDING CONDITION SATISFIED HERE**: `## FR-1 erratum (landing)` section written into `decision.md`, stating (i) §6's F04 paragraph mis-attributes F06C-attempt-1 mechanics (gate-failed + launcher-kill + `writer.py`), (ii) §7.1 is authoritative for F04 attempt-1 — `{killed:{}, timed_out:true, barrier_files_at_timeout:[]}`, barrier never fired, nothing killed, and **zero F04 gate-fail records exist**, (iii) F04 attempt-1 bytes unrecoverable (disclosed overwrite; original values transcribed into §7.1 at execution time), (iv) rebuilt F04 cell internally consistent (gate 4/4, counters, chain 4242, recovery deltas). §6's original text **retained untouched** (erratum-style, not a silent rewrite) |
| **FR-2** | P3, claim precision | `snapshot.py` used `ATT.parents[1]` as the PLAN root ⇒ the 6 plan anchors are `missing:true` in BOTH snapshots; "26/26 anchors identical" = 20 hashed + 6 vacuous; honest count = `changes.diff`'s `anchors_identical=20` | **ANNOTATED** in `decision.md` (§8 original claim retained as superseded-with-note) and in `handoff.json`; **reviewer's correction figure recorded: re-hashed all 26 intended files at corrected paths = 0 mismatches (6/6 match pins)** ⇒ landed wording "20 hashed + 6 pin-verified by reviewer" |
| **FR-3** | P3, transcription | `exit_declaration_verbatim` deviates from the card by one ASCII space in its final clause (`先 blocked` in the handoff vs `先blocked` in `card_I-07-D.md` L14); first sentence byte-exact; `matrix_l58_rule_verbatim` == matrix L58 byte-exact | **ANNOTATED** in `decision.md` + `handoff.json`. The verbatim declaration in the handoff is **NOT altered** — it is what the card recorded at execution; the note records that the intended card form differs by that one ASCII space |
| **FR-4** | info, wording | oracle §4's F01 recovery cell reads "+1 sim fetch" (oracle.md L298) while the measured provider delta is +2 (1 sim discover + 1 sim fetch; decision §4 reports it honestly); downloads exactly +1 as frozen | **ANNOTATED IN `decision.md` ONLY** — `oracle.md` untouched (frozen-first preserved); wording ambiguity only, no masking |

## Scope of acceptance (carrier §10 per-cell table, transcribed under the two rulings)

| cell | matrix-row evidence (clauses 2-5) | frozen extra checks | reviewer disposition |
|---|---|---|---|
| F01 | PASS (trigger / chain / no-pseudo-raw / +1-download / gap visible) | 20/20 true | **accepted** |
| F02 | PASS (raw preserved, no handle, 0 downloads; D-1 recorded non-gating) | 15/15 true | **accepted** |
| F03 | PASS (real 34.515 s lock-wait, catalog_busy, idempotent recovery) | 11/11 true | **accepted** |
| F04 | PASS (gate-clean kill, 4242 visible, recovery registers, raw intact) | 17/17 true | **accepted** + FR-1 gap marker attached |
| F05 | PASS row; clause3-cause-**FAIL** = F-F05-cause | 18/18 row checks true | **accepted** as **row-PASS + clause3-cause-FAIL recorded (ledger)** |
| F06A | row PASS (visibility, append-only 1→3, p0 intact, chain ok) | audit checks FAIL = product defect | **accepted_scoped**: measured red retained (no re-gate), **NON-BLOCKING** per §6 |
| F06B | row PASS (row+json present / md-absent ⇒ not consumable, 1→4, chain ok) | same | as F06A |
| F06C | row PASS (complete-never-half, scoped kill, 1→4, members identical) | same | as F06A |

- **Ledger routing at landing**: F-F06-audit + F-F05-cause → **REMEDIATION ledger** (fixes NOT
  this card's surface).
- **Inherited carries stay open upstream** (not this card's surface): I-07-B F1/F2/F3/J6,
  I-09-C F12/F5, production I-16/I-17 pending; `disclosure_adaptation=unmapped`,
  `accuracy=unproven` unchanged.
- **Cleanup authorized after landing** per `recovery/README.md` §2 (`%TEMP%\i07d\**`,
  `evidence/wprobe_tmp/**`, iso/venv if archived) — the reviewer's own `%TEMP%\i07d_review\`
  helpers may be deleted with it (3 cleanup scopes).
- **Parent actions**: batch commit of `execution_runs/I-07-D/`; open REMEDIATION-ledger
  entries for F-F06-audit and F-F05-cause; authorize cleanup including `%TEMP%\i07d_review`.

## Unverified / limits (carrier §11 — 7 items carried, transcribed)

1. F01 fixture candidate fields remain **C-level** (lifted from production metadata
   observation; no live-provider validation in this card).
2. Share-none hold semantics rely on observed Win32 `CreateFileW(ShareMode=0)` behavior in this
   environment (outputs verified; OS semantics not re-derived).
3. F05 `production_observation_copy` row schema equality vs production is asserted via
   `content_sha256` + row dict (cell file hash == production `normalized.md` `980ea4f8…`;
   full row-dict schema diff not re-run).
4. F06C attempt-1 child **pid 44784's death mechanism** after the launcher kill is not recorded
   (no exit record; dead by census-after and by the reviewer's live scan — no stray alive).
5. HK canonical filename divergence (**D-3**) remains open (side/inherited observation).
6. `document_fingerprint_state+1` during the F05 fault run remains an open side observation.
7. `producer_events.event_type='llm'` label for the extractive summary — cosmetic, out of card
   scope.

## Record fixes applied at this landing (FR-1..FR-4 — corrected/annotated with originals retained)

| file | fix | sha256 before → after |
|---|---|---|
| `decision.md` | FR-1 erratum section + FR-2/FR-3/FR-4 annotations appended; §6, §7.1, §8 and §0's verbatim declarations all **retained untouched** | `792523799fcbf74002d3ff3e1db876c80f19a47baabc10099fbe457ac9f649d5` (26,850 B) → `ba6e4a1d0d1190f79c0c0519e61d16d6542cfab6e14184879897047c4c01f730` (31,292 B) |
| `handoff.json` | status → `accepted_scoped` + `status_before_bookkeeping_fix` + `status_authority` + `bookkeeping` (FR-1..4 before/after hashes, `ruling_R1`/`ruling_R2`) + per-cell final table + carried inherits + stale pre-verdict prose superseded as `*_historical_pre_verdict`; **`exit_declaration_verbatim` NOT altered** (FR-3) | `2ea58a5a30c7d883e50632ab7c96b9d112edc18d7adb23a7c3cbd80e0b1d61a5` (16,078 B) → (final sha recorded in `evidence/I-07-D/qualification.json`; self-excluded inside handoff.json) |
| `evidence/I-07-D/qualification.json` | created — formula.state mirror, carrier mirror, declarations, FR-1..4 mirror, two-ruling mirror, per-cell scope mirror, ledger-routed findings | pre-image: none (dir + file created) |

Untouched by this landing: `reviewer_report.md` (27,858 B / `1a1d1c05…c9a933`),
`reviewer_report.sha256` (86 B / `320c689c…`), `oracle.md` (27,211 B / `576ddfc5…18846`,
frozen-first), `binding.json`, `commands.json`, `changes.diff`, `recovery/README.md`,
`evidence/**`; git writes 0; network 0; product/production writes 0.
