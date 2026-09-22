# DW15-REPAIR oracle — FROZEN BEFORE ANY RUN of this attempt

Status: FROZEN 2026-09-22, written before any RED/GREEN/mutation run exists.
Author: implementer (repair card). Not a reviewer. The implementer never writes
"accepted"; `handoff.json` stays `review_pending`.

## 0. What this card is and is not

Owner ruling (2026-09-22, verbatim): 「A-1，授权"修代码"卡」 recorded in
`PLAN/OWNER_DECISIONS.md` §15 (and re-confirmed §16 as `A-1 = b`).

- **Authorized**: repair the two scripts per the proposal I-15-A already documented
  (`execution_runs/I-15-A/a20260919-01/decision.md`, source of truth).
- **NOT authorized**: executing ANY production prune. No real evidence data may be
  pruned or archived by this card. After repair, a data-recovery reviewer must
  re-sign before any real execution — that is a separate future step, not this one.

The source of truth for *what is broken* is I-15-A's `decision.md`; the frozen rule
set it proposes is `W15-R1..R8` (I-15-A `oracle.md`). This card fixes the **five
defects** the owner enumerated; where a fix touches a W15 rule, the property below
restates that rule for the repaired code.

## 1. The five defect properties (property, not implementation)

**D1 — 空目录也删 (an empty directory must not authorise a prune).**
Prune may authorise a deletion only from at least one *verified* archive manifest:
a manifest that exists, declares `ok`, names an archive file whose bytes match its
declared sha256, and whose per-row digests match the rows actually re-read from that
archive. An empty directory, a directory containing a snapshot but no manifest, a
manifest whose snapshot is missing or truncated, and "the directory is old" each
authorise **nothing**: prune must report not-eligible and apply must delete 0 rows.
Conversely, when a verified due manifest exists, apply must delete exactly the
manifest-authorised, still-retired, digest-matching rows — no more (W15-R1/R2).

**D2 — 同日覆写 (same-instant runs must not clobber each other).**
Two archive runs and two prune runs issued at the same instant (same second, same
injected `now`) must each leave their own complete output behind: every snapshot and
every receipt from run 1 must still exist, byte-identical, after run 2 finishes.
No run may truncate, replace, or overwrite another run's artifact (W15-R1's
same-day-overwrite instance; I-15-A evidence `n1-same-day-overwrite`).

**D3 — 时钟取目录名 (no system-clock read may decide a path or the retention clock).**
(a) Neither script may read the machine clock (`datetime.now`, `utcnow`,
`date.today`, `time.gmtime/strftime/time`, `fromtimestamp`): every path component is
decided either by the explicitly injected `now` parameter or by a non-clock unique
token. (b) Prune's retention decision comes from the manifest's
`verified_completed_at` compared against the injected `now` — never from a
directory/file name and never from the system clock (W15-R3; I-15-A evidence
`n2-clock`). A directory named with an ancient date, or a wall clock far past the
window, must not by itself make anything due; a recent `verified_completed_at`
inside the window must keep `due=false` regardless of the directory name.

**D4 — TOCTOU (the state a delete acts on must be re-verified atomically with the
delete).**
Apply must freeze an exact plan (span ids + row digests + archive sha256s +
plan hash) and, inside the operation lock, re-verify **before the first delete**
that every archive byte still matches its sha256 and every planned row still has
the planned digest and a `retired` document; then each delete batch must re-read
and re-verify its rows **inside the same transaction** that deletes them. Any
mismatch aborts the whole apply with a refusal and 0 deleted. Silently narrowing
the set (deleting the still-matching subset and reporting success) is forbidden
(W15-R4; I-15-A evidence `fault-recovery`).

**D5 — 崩溃后不可恢复 (crash safety).**
(a) The snapshot must be written to a temporary file, verified, and atomically
published; a kill at any point during the write must leave **no truncated file at
any published snapshot path** — an already-published snapshot stays complete
byte-for-byte, and the evidence rows stay in the catalog (the concrete instance is
`archive_retired_evidence.py:65` mode `"wt"`, which truncates the published
snapshot on open). (b) Prune must publish a *pending* receipt naming the full plan
**before the first delete**, update it after every committed batch, and finalize
it at the end; a kill between snapshot-write and delete must leave the snapshot
complete AND the evidence present-or-restorable — i.e. every deleted id is a subset
of the receipt's plan and of the verified snapshot, so the exact deleted set is
recoverable from durable artifacts, not from a directory listing
(W15-R5; I-15-A evidence `n4-crash-receipt-absence`).

## 2. Pre-listed tests and frozen expectations

Fixtures are SYNTHETIC only, built under `%TEMP%` (pytest `tmp_path`) or the
attempt dir's `scratch/`; a guard refuses any path that resolves into a product
repo or a `.source_catalog` directory. Expected sets are pre-listed here; they are
never derived from the scripts' own reports.

Fixed sample (reused from I-15-A): PRE state archived = doc-A retired {a1,a2},
doc-C retired {c1}; POST state at prune time adds a3 (after archive), doc-B/b1
(retired, never archived), doc-C active. `EXPECTED_DELETE = [a1, a2]`,
`EXPECTED_RETAIN = [a3, b1, c1]`. Timeline: archive `now=2026-05-01T00:00:00Z`,
prune `now=2026-09-19T00:00:00Z`, `retention_days=90` (age 141 ≥ 90 → due).

| id | property | frozen expectation | expected on ORIGINAL code |
|---|---|---|---|
| t_d1_1 | D1 | empty dir `archive/2026-05-01`, no snapshot, no manifest → apply deletes 0, `due=false` | RED (deletes all retired) |
| t_d1_2 | D1 | snapshot present but no manifest → apply deletes 0 | RED (deletes all retired) |
| t_d1_3 | D1 | manifest present but snapshot missing/corrupt → apply deletes 0 | RED (deletes all retired) |
| t_d1_4 | D1 | real archive + real prune → deletes exactly [a1,a2]; retains [a3,b1,c1] | RED (wrong set) |
| t_d2_1 | D2 | two archive runs with the same injected `now` → 2 complete snapshots; run-1 bytes unchanged | RED (1 snapshot, run-1 overwritten) |
| t_d2_2 | D2 | two prune applies in the same second → 2 receipts; first reports its own deletes, second reports 0 | RED (receipt overwritten) |
| t_d3_1 | D3 | source of both modules contains no system-clock API (regex scan) | RED (`datetime.now`, `time.gmtime` present) |
| t_d3_2 | D3 | manifest `verified_completed_at=2026-09-18`, dir `2026-05-01`, now 2026-09-19 → 0 deleted | RED (wall clock + dir name) |
| t_d3_3 | D3 | dir `2021-01-01` (ancient), verified completion recent → 0 deleted (I-15-A n2 verbatim) | RED (dir name is the clock) |
| t_d3_4 | D3 | archive with injected `now=2021-03-04` publishes under `archive/2021-03-04/` | RED (real today's date) |
| t_d4_1 | D4 | mutate a2's content after the plan is frozen → apply refuses, 0 deleted | RED (deletes anyway) |
| t_d4_2 | D4 | flip a planned row's document back to `active` after freeze → apply refuses, 0 deleted | RED (deletes anyway) |
| t_d5_1 | D5 | kill the snapshot write mid-stream → no published snapshot is truncated; the previously published snapshot is byte-identical; catalog untouched | RED (truncated file at published path) |
| t_d5_2 | D5 | kill prune after the pending receipt, before the first delete → receipt exists naming the full plan, 0 deleted, snapshot complete, evidence intact | RED (no receipt) |
| t_d5_3 | D5 | kill prune after batch 1 commits → receipt exists; every deleted id ⊆ receipt plan ∩ snapshot; evidence outside the plan intact | RED (no receipt) |

Guard: a compliant original could in principle pass a test by accident; the
mutation matrix below is what binds each test to its defect.

## 3. Declared mutation red sets (frozen BEFORE mutation runs)

Each mutation is applied to a SEPARATE copy of the repaired `iso/fixed` tree; only
the named revert is introduced. Declared = expected RED tests; observed must equal
declared exactly.

| mutation | revert | declared RED set |
|---|---|---|
| M1 | D1: restore original authorisation when no verified manifest exists (directory-age due → delete all retired spans) | t_d1_1, t_d1_2, t_d1_3 |
| M2 | D2: fixed output names (`retired-evidence.jsonl.gz` per day-dir; `prune-retired.json` for receipts) — same-instant overwrite restored, no clock reintroduced | t_d2_1, t_d2_2 |
| M3 | D3: restore original retention clock (oldest archive directory name vs `datetime.now`) in prune; manifest gate kept | t_d3_1, t_d3_2, t_d3_3 |
| M4 | D4: skip the pre-delete state re-verification (plan is trusted; batches delete without digest/status re-read) | t_d4_1, t_d4_2 |
| M5 | D5: write the snapshot directly to its published path (no temp+verify+rename) and write the receipt only after the loop completes (original positions); unique names kept | t_d5_1, t_d5_2, t_d5_3 |

Not mutation-bound (expected RED on the original, GREEN under all five mutations
by design): t_d1_4 (uses a verified manifest, outside M1's fallback), t_d3_4
(archive-side clock, outside M3's prune-side revert). Any *unexpected* red under a
mutation is recorded as observed ≠ declared and blocks `review_pending` sign-off
until explained.

## 4. Side-effect expectations

- Writes only: the attempt dir, pytest `tmp_path` under `%TEMP%`, and the attempt's
  own `scratch/`. The product repos are read-only in place; the fix lives in `iso/`.
- The production catalog (`company-wiki\.source_catalog\catalog.sqlite3`, 49.7 GB)
  is never opened, read or written; no production prune or archive is executed even
  once; no worker/scheduler/network/D:-drive access; no git operations in the
  product repos; no other card's attempt or frozen artifact is modified.
- `disclosure_adaptation = unmapped`, `accuracy = unproven`; this card never
  self-signs; `handoff.json.status = review_pending`.
