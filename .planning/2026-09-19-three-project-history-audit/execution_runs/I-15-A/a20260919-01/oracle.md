# I-15-A oracle — FROZEN BEFORE ANY RUN of this attempt

Status: FROZEN 2026-09-19, written before `before_pass*` / `after/` evidence exists.
Author: implementer. Not the reviewer. The implementer never writes "accepted".

## 0. The rule being frozen

`PLAN/reviews/wiki/review.md:80`: *"维护上区分每个待删除记录是否属于已验证归档集合"*.
`PLAN/audit_report.md` row "section 查询、prune、日志脱敏等" and
`reviews/wiki_legacy/item_ledger.jsonl` entries `WIKI-LEGACY-SPECIAL-0112 / 0130-0132 /
0155-0162` show the current code does **not** implement that rule:

- `prune_retired_evidence._DELETE_BATCH` selects **every** retired document's spans;
  it never consults the archive at all;
- the only archive input is the **oldest directory NAME** under `archive/`, and `due` is
  `(today - oldest_dir_name).days >= retention_days` — directory age is treated as the
  deletion authorisation;
- `archive_retired_evidence` writes `archive/<today>/retired-evidence.jsonl.gz` with `"wt"`
  (truncating) and reconciles **counts only** (`rows_written == rows_in_catalog`);
- nothing binds a span id, a row digest, an archive completion time, or a per-document
  identity; there is no plan hash, no TOCTOU re-check, no receipt of the exact set.

**Frozen rule (W15-R1..R8), which any fix must satisfy:**

- **W15-R1 (authorisation)** — deletion is authorised **only** by a specific, verified
  archive set: a manifest that names the catalog identity, the archive file(s) with their
  sha256 and byte size, the exact span ids and their row digests, and the verified
  completion time. A directory existing, or being old, authorises nothing.
- **W15-R2 (per-row recoverability)** — every span selected for deletion must (a) appear in
  the verified archive with an identical row digest, (b) still exist in the current catalog
  with an identical row digest at plan time, and (c) belong to a document whose current
  `source_status` is `retired`.
- **W15-R3 (retention clock)** — the retention window is computed from the manifest's
  verified completion time, never from a directory name and never from the archive file's
  mtime.
- **W15-R4 (exact set + plan hash)** — the dry run emits the exact span-id set plus a plan
  hash; apply re-verifies archive, current rows and plan hash under the operation lock
  before the first delete. Any mismatch aborts the whole apply with a business refusal —
  silently narrowing the set and reporting success is forbidden.
- **W15-R5 (crash / batch receipts)** — batch commits write a receipt of the exact ids
  already deleted, so an interrupted run is recoverable from transactions rather than from
  the directory listing. Unproven rows always stay.
- **W15-R6 (idempotence)** — a second apply of the same plan deletes 0 rows.
- **W15-R7 (restore)** — a deleted span can be restored into an independent empty catalog
  with identical document_id/source_id/locator/digest; a restore must never overwrite a
  newer active row.
- **W15-R8 (old archives)** — an archive without a manifest is *not* upgraded by guessing;
  it is either verified by a separately specified procedure or left unusable for prune.

## 1. Fixed sample (from the card, restated so it cannot drift)

```
now                        = 2026-09-19T00:00:00Z  (fixed clock; never datetime.now)
retention_days             = 90
manifest verified_completed_at = 2026-05-01T00:00:00Z   -> age 141 days -> due
catalog (scratch)          = 5 spans total
  A  retired, archived     -> spans a1, a2   (both inside the verified archive)
  A  retired, added after  -> span  a3       (NOT in the archive)
  B  retired, never archived -> span b1      (NOT in the archive)
  C  active again, archived  -> span c1      (in the archive, but the document is active)
expected deleted           = {a1, a2}        (exactly 2)
expected retained          = {a3, b1, c1}    (exactly 3)
```

Expected sets are **pre-listed by hand here and in `expected_sets.json`**; they are never
produced by calling `prune_retired_evidence` or by deriving from its report.

## 2. Cases and frozen expectations

**W15-P1 / positive (delete only the verified set).**
Build a real scratch archive (real `archive_retired_evidence` output over a real scratch
catalog) plus a manifest for exactly {a1, a2}, verify it with the attempt's own independent
verifier (NOT the product's), then run the current product prune with `apply=True`,
`retention_days=90`.
- Expected on the **current** code: `deleted_rows == 5` (all retired spans) — i.e. a1, a2,
  **a3 and b1 are destroyed although the archive proves nothing about them**.
- Expected of a compliant implementation: `deleted_rows == 2`, remaining = {a3, b1, c1}.
- The frozen verdict for the current code is therefore **counterexample reproduced**, not a
  pass. No product code is modified in this attempt, so no "after" P1 pass is claimed.

**W15-P2 / positive (idempotence + restore).**
- Second apply must delete 0 rows. Frozen expectation on current code: it deletes whatever
  is still retired, so it is not idempotent against the authorised set; measured and
  reported.
- Restore: a deleted span restored into an independent empty catalog must equal the archived
  row exactly (document_id, source_id, locator, row digest). There is no supported restore
  CLI (`CMD-W10` note), so this is exercised through the attempt's own restore procedure
  reading the archive, and the result is compared to the pre-delete row digests. Expected:
  byte-identical row digests for a1 and a2. Restoring c1 (active) must be refused.

**W15-N1 / negative.**
Only an old empty directory; missing / corrupt / count-conflicting gzip and manifest.
- Expectation: a compliant dry-run reports **not eligible** and apply deletes 0.
- Frozen expectation on current code: an **empty old directory is accepted as authorisation**
  and apply deletes everything retired. Variants to measure: empty old dir, truncated gzip,
  manifest with a wrong row count, manifest with a wrong row digest, missing manifest.
- Explicitly: the current `test_prune_apply_deletes_spans_when_due` (which builds an empty
  directory and asserts a full delete) is **not** a valid oracle.

**W15-N2 / negative (clock).**
90 days not elapsed; or the directory name is old but the verified completion time is recent.
- Expectation: 0 deleted, computed from verified completion time.
- Frozen expectation on current code: `due` follows the **directory name**, so a fabricated
  old directory with a recent verified completion deletes everything. Measured.

**W15-N3 / negative (TOCTOU).**
After a dry run, mutate a2's content (or flip its document back to active), then apply.
- Expectation: apply must refuse the whole plan; narrowing the set silently is not allowed.
- Frozen expectation on current code: apply deletes based on the live query, so the mutated
  or reactivated row is either still deleted (a2 content changed) or silently dropped from
  the set with no refusal (c1 reactivated). Measured.

**W15-N4 / negative (interrupted batch).**
Simulate a crash between batches / a receipt write failure.
- Expectation: recover from transaction facts: rows already committed are recorded, the rest
  can be re-planned, and rows without an archive proof are always kept.
- Frozen expectation on current code: the receipt is written **only after** the whole loop
  completes (`prune_retired_evidence.py:125-142`), so an interrupt mid-loop leaves deleted
  rows with **no receipt at all**. Measured by interrupting via a monkeypatched transaction
  that raises after the first batch.

## 3. Side-effect expectations

- Only this attempt dir is written. The scratch catalog is created by the attempt at
  `<attempt>/scratch/<case>/catalog.sqlite3`.
- The production catalog is **opened read-only at most, and never by these runs**: the
  harness refuses any path containing `company-wiki\.source_catalog`.
- `worker_control.json` is not opened for writing; `desired_state` stays `paused`.
- No network, no D: drive access, no scheduler.

## 4. Exit criteria for this card

"以行集合/实际可恢复性关闭缺口" — the gap is judged by the **span id set** and by **actual
restorability**, not by row counts. Scope limited to isolated maintenance: nothing here may
be used to start a production prune.
