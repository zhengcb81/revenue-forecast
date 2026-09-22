# DW15-REPAIR — independent reviewer report (claim verification)

Card: `DW15-REPAIR` · attempt `a20260922-01` · reviewer pass date: 2026-09-22
Scope of THIS document: independent verification of the 7 listed claims about the
repair card **and the reviewer's explicit three-state ruling on the card**. The
ruling is `accepted_scoped` — see "RULING" below. The implementer never signs;
transcription of this ruling into `handoff.json.status` is the carrier's step,
not part of this file. Three other states are independent of this ruling and are
NOT changed by it: **production prune/archive execution remains unauthorized**
(owner `OWNER_DECISIONS.md` §15/§16 `A-1`, §16 `E-4 = 维持暂不签`, confirmed by
me at lines 353–378), **promotion of `iso/fixed` into `company-wiki` remains not
taken**, and **the data-recovery reviewer re-sign remains OUTSTANDING/unsigned**.

Reviewer boundaries honored: wrote ONLY `reviewer_report.md` and
`reviewer_report.sha256`; production trees read-only; no git write operation; no
self-sign; every prune exercised in this review pruned only my own synthetic
`%TEMP%` pytest fixtures.

## VERDICT

**All 7 claims VERIFIED. No blocking defect found. Six non-blocking findings
(F1–F6) and eight explicitly unverified items (U1–U8) are recorded below.**

## RULING (reviewer, three-state): `accepted_scoped`

I rule the card **`accepted_scoped`**. Scope statement:

1. **Accepted (in scope):** the repair as it exists in `iso/fixed/`
   (prune `0c99bbe0…`/23115 B, archive `bbe855e4…`/9894 B) as a verified fix of
   defects D1–D5, together with its evidence chain (oracle pin `003f48da31f1…`,
   RED 15 failed/rc1 → GREEN 15 passed/rc0, mutation matrix declared==observed
   for M1–M5, M5 independently re-run by me) — i.e. acceptance covers *code
   correctness of the isolated copy against this attempt's frozen oracle, and
   only that*.
2. **Explicitly OUT of scope — four independent states, none granted here:**
   (a) any production prune/archive **execution**, dry-run included, stays
   unauthorized (owner §15/§16 A-1, §16 E-4); (b) **promotion** of `iso/fixed`
   into `company-wiki` stays a separate, untaken owner decision; (c) the
   **data-recovery reviewer re-sign** stays unsigned — it is a precondition of a
   future *execution* card, not of this card's acceptance: this card's
   authorized scope was "repair code only" (owner A-1) and that scope is now
   delivered and verified, so making the re-sign a condition of *this* card's
   acceptance would make the card permanently unacceptable, contradicting the
   owner's explicit grant of the repair card; (d) transcription of
   `handoff.json.status` is the carrier's step, not this ruling.
3. **Carried findings (registered, non-blocking):** F1 (multi-batch D4 "0
   deleted" narrow window), F2 (conflicting-digest order dependence), F3+F5
   (RED evidence captured `--tb=no`, UTF-16LE), F4 (no directory fsync →
   power-loss durability unproven), F6 (freeze ordering evidenced by mtimes +
   hash pin only).
4. **Carried unverified items (registered):** U1–U8 as listed. Recommended —
   **not** required for this card — as entry criteria for any future execution
   card: decide the receipt durability medium (U5), address or explicitly waive
   F1/F2, demonstrate scale behaviour (U4), replace the product contract tests
   (U7).

Conditions on this acceptance: **none blocking.** F1/F2 are LOW-severity edge
cases whose realistic exposure is further limited by the read-only archive actor
and the paused worker; they are carried, not gating. This ruling does not sign,
and does not release, any of the three out-of-scope states named in (2).

## Findings (numbered, one per claim)

### F-CLAIM-1 — production locations + before-hashes: VERIFIED
Measured by me (SHA-256 / bytes):

| file | measured | declared | = |
|---|---|---|---|
| `company-wiki\src\company_wiki\source_catalog\prune_retired_evidence.py` | `2358c73b82da65e5292998e3dba71c6132eebab1ab6c88a224a736c1e5a8ae46` / 4658 B | `2358c73b…` / 4658 B | ✅ |
| `company-wiki\src\company_wiki\source_catalog\archive_retired_evidence.py` | `143fef01fade43a5e6ae5c733d86e5ea6081482547c2560fc872990a9d8f53e0` / 3291 B | `143fef01…` / 3291 B | ✅ |

- Both hashes equal the originals I-15-A declared (`execution_runs/I-15-A/
  a20260919-01/binding.json` L41/L52, `handoff.json` L25–26, `changes.diff`
  L15–16 — all four occurrences identical to my measurement).
- Re-hashed at the END of my review (after all my test runs): **unchanged** ✅.
- Review-snapshot copies (`.review-zr407-20260818\company-wiki\src\…`) hash
  identically ✅.

### F-CLAIM-2 — fix confined to `iso/fixed/`: VERIFIED
- `iso/fixed` prune = `0c99bbe0c5f4ef16e7f84ba8aae0548ef6f59a0080274d5bd1ce83a7d37990b0` / 23115 B ✅;
  archive = `bbe855e4495e82d2a40b0185c9db8efa2639449fdd5f768120538abb992b28ac` / 9894 B ✅.
- My own byte-compare (independent script, SHA-256 per file): baseline 146 files,
  fixed 146 files, **exactly 2 differ** = the two target scripts; 0 added, 0 deleted ✅.
- `iso/baseline` copies are byte-identical to production (both scripts) ✅ — so the
  RED run is a run against the production original.
- `company-wiki\.source_catalog\worker_control.json` = `9fcbe233efe76222a32316c07b9273b9c5128da3af6db27d706b1759680ac7bd` / 178 B ✅
  (`desired_state: "paused"` still present).

### F-CLAIM-3 — RED→GREEN re-run by me: VERIFIED
Interpreter per `commands.json`: `iso\venv` → Python 3.13.9, pytest 9.1.1,
`PYTHONDONTWRITEBYTECODE=1`, workdir = attempt dir.

| run (mine, not the implementer's) | result | rc |
|---|---|---|
| `DW15_VARIANT=iso/baseline pytest tests -q --tb=no` | **15 failed / 0 passed** | 1 |
| `DW15_VARIANT=iso/baseline pytest tests -q --tb=line` (extra, to prove failure KIND) | 15 failed, **all 15 are `AssertionError` on their behavioural assertion** (0 errors/TypeErrors) | 1 |
| `DW15_VARIANT=iso/fixed pytest tests -q --tb=no` | **15 passed / 0 failed** | 0 |

- RED failure ids = exactly the frozen D1–D5 list `t_d1_1..4, t_d2_1..2,
  t_d3_1..4, t_d4_1..2, t_d5_1..3` ✅, and each failure text matches its frozen
  expectation (examples from my run: "an empty old directory authorised the
  deletion of ['a1','a2','a3','b1']"; "snapshot published under '2026-09-22';
  the system clock decided the path instead of the injected now"; "a published
  snapshot is not crash-safe: ['retired-evidence.jsonl.gz: 2 rows, expected 4']").
- Implementer evidence files hash-verified against their declared pins in
  `commands.json`: red `b035696a…`, green `bb2b0602…`, m1 `fd56c3e6…`,
  m2 `830c0a8b…`, m3 `26e004ac…`, m4 `2df701ae…`, m5 `df08ac5e…`,
  matrix `50716b9b…`, `changes.diff` `62bb1236…` — **all 9 match** ✅.

### F-CLAIM-4 — mutation matrix: VERIFIED (incl. my own M5 re-run)
- Declared sets exist in `oracle.md` §3 (oracle SHA-256 = `003f48da31f131a4b35604807cb1c37aef968c413edfb4d0181854f2462e0574`, matching the
  frozen pin) and match the task's declared matrix exactly
  (M1→d1{1,2,3}, M2→d2{1,2}, M3→d3{1,2,3}, M4→d4{1,2}, M5→d5{1,2,3}).
- Observed sets in the pinned `mutation_matrix.json` and in the pinned raw
  `mutant_m*_stdout.txt` files equal declared for all five ✅ (counts 3/2/3/2/3,
  rc=1 each; t_d1_4 and t_d3_4 pass under all mutants — as oracle §3 pre-declares).
- **My own re-run of M5** (`DW15_VARIANT=mutants/m5`): `3 failed, 12 passed`,
  rc=1, failing exactly `t_d5_1, t_d5_2, t_d5_3` ✅ — observed == declared
  without trusting `mutation_matrix.json`.
- Freeze-order evidence (filesystem mtimes, supporting only — see U1): oracle.md
  08:36:20 → tests 08:47–08:51 → harness 08:59–09:04 → RED/GREEN evidence
  09:05 → mutant evidence 09:07–09:08 → matrix 09:24 (all on 2026-09-22).

### F-CLAIM-5 — five defects actually addressed (read from `changes.diff` + independent scan): VERIFIED
- **D1 manifest-authorized deletion**: `_load_verified_archives()` requires
  schema `archive-verified-manifest-1.0` + `ok: true` + archive exists + size +
  sha256 + full gzip re-read with per-row digest recomputation + row count +
  `verified_completed_at` parse; anything else lands in `manifest_problems` and
  authorises nothing; `_build_plan` authorises only from *verified + due*
  archives and only rows that are still `retired` with an identical digest.
  Empty dir / bare snapshot / broken snapshot → empty plan → `due=false`,
  apply deletes 0 ✅ (also proven by t_d1_1..3 RED→GREEN and M1).
- **D2 same-second runs**: archive writes `retired-evidence-<uuid16>.jsonl.gz`
  with create-if-absent publish (`FileExistsError` if taken); prune receipt is
  `prune-retired-<uuid16>.json`, rewritten only by its own run via
  temp+`os.replace` ✅ (t_d2_1/2 RED→GREEN, M2).
- **D3 no wall-clock API**: my own static scan of BOTH fixed modules for
  `datetime.now|utcnow|date.today|time.gmtime|time.strftime|time.time(|fromtimestamp|import time`
  → **0 matches** ✅. Paths come from the required timezone-aware `now`
  (`TypeError` otherwise) and `uuid4`; retention = `now − manifest
  .verified_completed_at` via `_is_due()`, never a directory name (t_d3_1..4,
  M3). Baseline genuinely contained `datetime.now` + `time.gmtime` (removed lines
  in the diff).
- **D4 TOCTOU**: inside `CatalogOperationLock`, before the first delete:
  `_verify_archives_on_disk()` (sha256 of every archive byte) + `_span_states()`
  re-read of every planned row's digest/status → `PruneRefused` (whole apply,
  0 deleted). Then each batch re-reads its rows **inside the same
  `store.transaction()`** that issues the DELETE and refuses on any digest/status
  drift. No silent narrowing path exists in the code ✅ (t_d4_1/2 RED→GREEN, M4).
  See F-1 below for one narrow multi-batch caveat.
- **D5 crash safety**: archive writes a TEMP file only (`gzip.open(tmp_path,"wt")`
  — the baseline's `archive_retired_evidence.py:65` `gzip.open(out_path,"wt")`
  truncation of the published path is confirmed present in baseline L65 and
  **gone in fixed**), then fsync, full re-read verification (count+digests),
  atomic create-if-absent publish, then an atomically written manifest; unpublish
  residue is unlinked in `finally`. Prune publishes a **pending receipt naming
  the full plan (span_ids + row_digests + archives + plan_hash) before the first
  delete**, atomically updates it after every committed batch, and finalizes to
  `complete`. Kill-safety invariant deleted ⊆ receipt plan ∩ verified snapshot is
  asserted directly by t_d5_3 ✅ (t_d5_1..3 RED→GREEN, M5 re-run by me).

### F-CLAIM-6 — ZERO real data: VERIFIED (within the limits of U2/U3)
- `guard_scratch()` (read in `harness/dw15_fixtures.py` L70–83): hard
  `SystemExit("BINDING-REFUSED")` for any path whose parts contain
  `.source_catalog`, or that is not under `%TEMP%` or this attempt dir, or that
  points into a foreign `execution_runs` dir. `make_config()` runs every DB path
  through it, and `CatalogConfig.catalog_dir/project_root` are built under
  `tmp_path` — so all prune/archive/lock/receipt activity in the tests targets
  synthetic `%TEMP%` trees only.
- Tests contain **no production path** (grep: only `tmp_path/…/catalog.sqlite3`
  and the variant source tree for the static scan) and **no git/subprocess/os.system
  call** in `tests/` or `harness/` ✅.
- `evidence/` (all 8 files) grep for `company-wiki|.source_catalog|catalog.sqlite3|D:\|Projects\`
  → **0 matches**: no production path appears in any recorded run output ✅.
- Production script hashes unchanged **before and after** my review runs ✅;
  `worker_control.json` unchanged ✅.
- Git (read-only checks by me): `git diff --name-only` on the two target scripts →
  empty (clean vs HEAD `f39bd5a6`); `git status --porcelain -uno` shows 3
  modified tracked files (`CLAUDE.md`, `README.md`,
  `src/company_wiki/source_catalog/artifact_dag.py`) with mtimes 2026-09-19 /
  2026-09-20 — **all predate this attempt (2026-09-22)** and none is a target
  script; `.git/HEAD` mtime 2026-09-08, `.git/INDEX` mtime 2026-09-20 → no git
  write activity inside the attempt window observable by me ✅.
- Dry-run vs production catalog: every code path the tests exercise builds its
  own `CatalogConfig` from `tmp_path` (guard-enforced); no production catalog path
  is constructed anywhere in `tests/`, `harness/`, or recorded `evidence/` (U3
  records the method limit of this conclusion).

### F-CLAIM-7 — honest scope: VERIFIED
- `handoff.json.status = "review_pending"` (measured at review time, before any
  transcription of this ruling — transcription is the carrier's step),
  `implementer_signed = false`,
  `implementer_never_signs_acceptance = true`, `disclosure_adaptation = unmapped`,
  `accuracy = unproven` ✅.
- `open_questions[0]`: data-recovery reviewer re-sign **"OUTSTANDING and expected
  to remain so"**; `open_questions[1]`: promotion **not taken**, separate owner
  decision ✅. `decision.md` §1 and §6 repeat both. No "accepted"/"signed" token
  anywhere in the implementer's artifacts ✅.
- Owner ruling text verified directly in `OWNER_DECISIONS.md` (§15 L353/357
  「A-1，授权"修代码"卡」/ **不授权执行任何生产 prune**; §16 L365/369 A-1=b
  允许修 prune 代码，不授权执行 prune; L378 E-4 维持暂不签) ✅ — the card's
  declared scope matches the ruling in both directions (nothing done beyond it,
  nothing required left undone except items explicitly reserved).

## Non-blocking findings on the repair code itself

- **F1 (LOW, D4 edge):** "any mismatch ⇒ 0 deleted" holds for drift detected
  before the first delete (which is where all planned-row drift lands, inside the
  lock). If drift were detected by the *in-transaction* re-read of a LATER batch
  (only reachable with >1 batch; `BATCH_SIZE = 100_000`), batches already
  committed stay deleted — the apply is refused and the receipt's `committed_ids`
  keep the exact deleted set recoverable, but the literal "0 deleted" would not
  hold for that race. Fixtures are ≤5 spans (single batch), so this path is
  untested (U4). Exposure is further limited because the only other actor
  (archive) is read-only and the worker is `paused`.
- **F2 (LOW, D1 edge):** in `_build_plan`, a span with conflicting verified
  digests is popped as "ambiguous", but a *later* due archive in the same loop
  re-adds it via `setdefault` — the "refuse to guess" outcome is therefore
  order-dependent and only guaranteed when the conflict is with the last
  conflicting manifest. Requires ≥2 verified manifests disagreeing about one
  span; untested.
- **F3 (documentation):** `evidence/red_baseline_stdout.txt` was captured with
  `--tb=no`, so the assertion messages quoted in `decision.md` §3 are not inside
  the referenced evidence file (they match my independent `--tb=line` re-run
  verbatim, so the quotes are accurate — just not sourced from that file). The
  evidence file is UTF-16LE (**F5**), which plain-text readers report as binary.
- **F4 (LOW, D5 durability):** publish/replace is atomic and file-level
  `fsync` is used, but there is no directory-level fsync and Windows offers no
  portable equivalent — process-kill safety is test-proven; power-loss durability
  is not.
- **F6 (provenance):** the "oracle frozen before runs" ordering is evidenced
  only by filesystem mtimes (self-reported, U1) — consistent and internally
  coherent, but not externally attested.

## Unverified list (explicitly NOT verified in this pass)

1. **U1** True temporal freeze of `oracle.md` before any run — supported by
   mtime ordering + the `003f48da31f1…` pin only; no external timestamp/notary.
2. **U2** "No other card's attempt or frozen artifact was modified" — spot-checked
   (I-15-A attempt files all mtime 2026-09-20; plan root `OWNER_DECISIONS.md`
   mtime 2026-09-22 08:13 predates the attempt's runs), not exhaustively audited
   across the whole plan tree.
3. **U3** "Dry-run never opened the production catalog" at syscall level —
   concluded from code-path + guard inspection and absence of any production path
   in evidence; no strace/File-System-Audit tracing was performed.
4. **U4** Behaviour at production scale (25.7M rows / 49.7 GB, whole-snapshot
   re-read at plan time) — untested, as the implementer themselves declared.
5. **U5** Receipt-durability medium (JSON under `artifacts/gates` implemented vs
   DB-table option) and `catalog_identity` binding depth — deliberately open for
   the data-recovery reviewer; I record, not decide.
6. **U6** Mutants M1–M4 observed sets — accepted from hash-pinned evidence
   files; I re-ran only M5 myself (task requirement: ≥1).
7. **U7** The product's own contract tests
   (`test_source_catalog_prune_retired.py` / `…_archive_…`) — not run; per
   I-15-A they encode the wrong oracle and per `decision.md` §6.4 were
   deliberately untouched.
8. **U8** I did not independently re-derive I-15-A's W15-R1..R8 rules text
   against this diff line-by-line; D1–D5 as frozen in this attempt's oracle were
   my comparison basis.

## REM-79 self-audit (bidirectional difference on my own text)

Criterion per `REMEDIATION_REGISTER.md` L332: a change of class must be checked
in BOTH difference directions.

- **`new \ old` (nothing unsupported added):** every verdict above traces to a
  command output, a hash I computed, or a file line I read in this session. The
  only acceptance language is the explicit `accepted_scoped` ruling, which is
  the reviewer's to issue (the implementer never signs) and is scope-limited to
  the isolated code; **no sentence claims execution authorization, promotion
  authorization, or the data-recovery re-sign** — those three states appear only
  as "not granted / unsigned / outstanding". Every quantitative claim (hashes,
  byte counts, rc codes, test counts, file counts) is a measurement, not a
  restatement of the card's claims.
- **`old \ new` (nothing material dropped):** all 7 task claims are individually
  answered (F-CLAIM-1..7); every caveat I found is either a numbered finding
  (F1–F6) or a numbered unverified item (U1–U8); the two things the task
  explicitly required me to guard (no self-sign, no production prune) are stated
  both in the header and in this audit.

## Commands I executed (all read-only except pytest fixtures under %TEMP%)

1. SHA-256/size measurement of production, snapshot, baseline, fixed, oracle,
   evidence, worker_control files.
2. Independent baseline-vs-fixed full-tree byte-compare (146/146, 2 differ).
3. `DW15_VARIANT=iso/baseline pytest tests -q --tb=no` → 15F/0P rc1.
4. `DW15_VARIANT=iso/baseline pytest tests -q --tb=line` → 15 AssertionError rc1.
5. `DW15_VARIANT=iso/fixed pytest tests -q --tb=no` → 15P rc0.
6. `DW15_VARIANT=mutants/m5 pytest tests -q --tb=no` → 3F (t_d5_1..3) rc1.
7. Static clock-API scan of both fixed modules → 0 matches.
8. Greps: tests/harness for production paths & git/subprocess; evidence/ for
   production paths; `OWNER_DECISIONS.md` for the A-1 ruling; `REM-79` definition.
9. Read-only git queries in `Projects\company-wiki` (`diff`, `status -uno`,
   `log -1`) and mtime inspection of the 3 modified files + `.git` metadata.

No production prune/archive/dry-run was executed by me; the only "prunes"
performed were against my own synthetic `%TEMP%` fixtures created by the suite.
