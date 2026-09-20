# I-15-A review.md

> ## PENDING independent review
> Written by the **implementer**. Nothing here is an acceptance. The independent recovery
> reviewer must re-derive at least one oracle value and attack the cases listed at the end.
> The implementer did not sign this card, did not modify product code, and did not run any
> production command.
>
> **r2 status (after the independent review returned `accepted_scoped` for the evidence /
> diagnostic scope): the PRODUCT IMPLEMENTATION REMAINS BLOCKED on the unsigned D-W15.
> `accepted_scoped` covers the evidence and the frozen oracle only; it is NOT a release to
> implement, and nothing in this attempt may be used to start a production prune.**

## r2 corrections (F-I15A-01)

`commands.json` and this file's "How the fixed sample was made real" section both cited the
delivered archive gzip as sha256 `85d2f08e05…`. **That citation was wrong**: no artifact in
the attempt carries that value any more. Provenance, now verified:

- `85d2f08e…` was the `p2-restore` case's archive hash at the **earlier** iteration
  (`before_pass/cmd-C6`). The suite re-ran at `after_pass/cmd-C7`; the gzip bytes changed
  because gzip embeds an mtime, so the earlier value can no longer be matched to any file.
- The **delivered** file and its `p1-verify` scratch source both hash to
  `4798b9719528223b8614d2ff6e22939cd60bd1427ce9c22da5d576317e1b9556`, and the delivered
  `archive-verified-manifest.json` records that same value
  (`commands.json`, `review.md:34`, `evidence/archive-verified-manifest.json` corrected).
- Rule adopted: **an archive hash quoted from this attempt must name both its case and its
  run.** `evidence/restore-proof.json` already follows that rule by carrying its own case's
  archive hash (`bccfe6a2…`).

## What this attempt is (and is not)

I-15-A asks for the prune rule to be bound to a specific verified archive set. `D-W15` is a
specialist decision that has not been signed, and `common_wiki_cards.md` forbids the
implementer from choosing the schema/transaction/recovery mechanism. So this attempt
delivers:

- a **frozen oracle** (`oracle.md`, written before any run) with W15-R1..R8 and the card's
  fixed sample;
- an **independent verifier** for archives (`harness/archive_verifier.py`) that shares no
  code with the product writer;
- **measured counterexamples** on the current code for every case the card names;
- **evidence artifacts** with the names the card requires;
- a **proposed** D-W15 decision (`decision.md`) for signature.

It does **not** deliver a fix, and it does not claim the gap is closed.

## How the fixed sample was made real

The product archiver only exports spans of documents whose current `source_status` is
`retired` (`archive_retired_evidence.py:26`). The card's sample says `c1` **is** archived
while `doc-C` **is** `active` at prune time, so the sample implies a timeline:

1. PRE: `doc-A` retired {a1,a2}, `doc-C` retired {c1} → **real** `archive_retired_evidence()`
   runs → gzip contains a1, a2, c1 (verified: `real-archive-retired-evidence.jsonl.gz`,
   archive sha `4798b97195…`, rows=3, no duplicate ids);
2. POST: add `doc-B`/b1 (retired, never archived), add `a3` to the dated `doc-A`, flip
   `doc-C` back to `active` → 5 spans total, exactly as the card fixes.

The attempt does **not** fabricate an archive: every archive used in the P-cases is the
product writer's own output over a real scratch catalog.

## Frozen expectations vs measured behaviour

| case | frozen expectation | measured on current code | evidence |
|---|---|---|---|
| W15-P1 delete exactly the verified set | delete {a1,a2}, retain {a3,b1,c1} | **deleted {a1,a2,a3,b1}, retained {c1}** — a3 and b1 destroyed with no archive proof | `deleted-and-retained-ids.json`, `exact-prune-plan.json` |
| W15-P2 second apply idempotent | 0 deleted, retain {a3,b1,c1} | second apply deletes 0 (empty set) but a3/b1 are already gone: **not idempotent w.r.t. the authorised set** | `idempotence.json` |
| W15-P2 restore | row-identical restore of a1,a2; refuse c1 | **restore identical** (digests match) and **c1 refused** — this one PASSES | `restore-proof.json` |
| W15-N1 empty old dir | 0 deleted | **deleted {a1,a2,a3,b1}** from an empty directory with no gzip at all | `n1-empty-old-dir.json` |
| W15-N1 corrupt gzip | verification fails closed | corrupt body → `ok:false`, problem recorded (attempt-side verifier) | `n1-corrupt-archive.json` |
| W15-N1 count/digest conflict | conflict must fail verification | count 3→4 and digest a1→`000…` are detectable by the verifier; **the product has no manifest at all**, so nothing in the product detects them | `n1-manifest-conflict.json` |
| W15-N1 same-day overwrite | manifest pins sha256+size so it is detectable | second same-day run **overwrote** the snapshot (`bccfe6a2…` → `7efa681c…`, ids {a1,a2,c1} → {a1,a2,a3,b1}); **both runs reported `ok: true`** | `n1-same-day-overwrite.json` |
| W15-N2 clock | 0 deleted, use verified completion time | directory `2021-01-01` with `verified_completed_at` 1 day old → **due:true, deleted 4** | `n2-clock.json` |
| W15-N3 TOCTOU | apply refuses the whole plan | a2 mutated after the plan hash was frozen → **deleted {a1,a2,a3,b1}** with no refusal, no re-check | `fault-recovery.json` |
| W15-N4 crash mid-batch | exact deleted ids recoverable | crash after the first batch commit → **4 rows deleted, `receipt_files: []`** | `n4-crash-receipt-absence.json` |

Suite result on the current code: **6 failed / 5 passed**
(`evidence/pytest_full_stdout.txt`, raw rc=1). The 5 passes are: real-archive verification,
corrupt-archive refusal, manifest conflict detection, restore proof, same-day overwrite
detection. The 6 failures are the counterexamples above — the RED is the oracle, not a
weakened check.

## Independent-oracle discipline

- `EXPECTED_DELETE = [a1, a2]` / `EXPECTED_RETAIN = [a3, b1, c1]` are pre-listed constants in
  `harness/archive_verifier.py`, taken from the card. No assertion uses a value produced by
  `prune_retired_evidence` to build its own expectation: the product's `PruneReport` is only
  ever *written beside* the measured id sets, never used as the expectation.
- The prunable set is derived by `select_prunable_ids()` = archived ∩ still-present ∩
  still-retired, which is the oracle's W15-R2 restated, and it is computed from the verified
  manifest plus a read-only SQL query — not from the product's selection SQL.
- The verifier (`archive_verifier.py`) never imports the product at verification time; only
  `write_real_archive()` imports `archive_retired_evidence`, and that is the artifact under
  test, not the oracle.

## Scope / safety statement

- Product code changed: **none**. `git status --porcelain` for company-wiki still shows only
  the two pre-existing user edits (`CLAUDE.md`, `README.md`) plus the three files changed by
  the I-14-C card in this same session. `prune_retired_evidence.py` and
  `archive_retired_evidence.py` are byte-identical to the hashes recorded in `binding.json`.
- Production catalog opened: **never**. `guard_scratch()` refuses any path containing
  `.source_catalog`, and all catalogs used are `<attempt>/harness/scratch/<case>/catalog/`.
- Production bytes deleted: **zero**. Every DELETE in this attempt targeted a scratch SQLite
  file created minutes earlier by the attempt itself. No file under
  `C:\Users\郑曾波\Projects\company-wiki` was removed or moved.
- `worker_control.json` sha256 before and after: `9fcbe233efe7…` (desired_state `paused`,
  unchanged). No worker was started.
- Network: none. `D:` drive: not touched.

## Open gaps / not verified

1. **No fix implemented.** The counterexamples stand. Implementation waits for a signed
   D-W15 (schema, transaction boundary, receipt durability, restore protocol).
2. **Scale is not proven.** All fixtures are 5 spans in a few-hundred-byte DB. Nothing here
   says anything about a 25.7M-row / 49.7 GB production prune, query plans, vacuum cost or
   disk headroom. The card says small-fixture correctness is not production-scale
   correctness; that remains open on purpose.
3. **The retention clock is not injectable today.** `prune_retired_evidence` uses
   `datetime.now(timezone.utc).date()`; the N2 case therefore had to encode "recent verified
   completion" in a fabricated manifest the product ignores. A fixed-clock parameter is part
   of the D-W15 proposal, not implemented.
4. **Manifest for old archives.** W15-R8 (no guessing) is stated but no upgrade procedure is
   designed; production's 2026-08-07 archive has no manifest and is therefore unusable for
   prune under the frozen rule.
5. **The product's own prune test is still wrong and unmodified.**
   `CW/tests/contract/test_source_catalog_prune_retired.py::test_prune_apply_deletes_spans_when_due`
   builds an empty `archive/2026-05-01` directory and asserts a full delete; the card says
   this must become a refusal counterexample. This attempt left it untouched (the replacement
   lives in `harness/tests/`) so the reviewer can judge it before it enters the product repo.
   Its date comment ("`> 90 days old`") is also stale but still true for 2026-05-01 vs the
   current clock.
6. **`archive_retired_evidence.py:65` opens the snapshot with mode `"wt"`** — the same-day
   overwrite is measured, not fixed. Any manifest scheme must survive this, or the writer
   must stop truncating.
7. **Restore has no product-side entry point.** `restore.py` exists but is about
   `restore_document` (document status), not evidence-span restoration; the restore proof
   here uses an attempt-owned insertion procedure. A product restore path is required before
   any prune can be called safe, and it is out of this card's allowlist.

## reviewer: attack first

1. Re-derive `EXPECTED_DELETE`/`EXPECTED_RETAIN` from the card text alone and confirm the
   pre-listed constants were not retro-fitted to the observed output (check
   `harness/archive_verifier.py` was written before the run evidence exists — the attempt's
   file mtimes and the `cmd-C*` sequence are the trace).
2. Reconstruct the PRE/POST timeline yourself: confirm the archive genuinely contains
   {a1,a2,c1} by gunzipping `evidence/real-archive-retired-evidence.jsonl.gz` and hashing the
   rows with your own canonicalisation; if your digest scheme differs from
   `row_digest()`, say so — the manifest's `row_digests` are only meaningful with the scheme
   pinned in `decision.md` D-W15-1.
3. Try to make the N4 crash case pass without a receipt (e.g. by arguing the WAL still holds
   the deleted rows). If it does, the finding changes: record which recovery artifact really
   exists.
4. Check the guard: run `prune_retired_evidence` with a `CatalogConfig` pointing at the
   production `.source_catalog` in a scratch copy of the harness and confirm `guard_scratch`
   refuses before any connection is opened. If it does not, that is a binding defect in this
   attempt, not in the product.
5. Decide the D-W15 items in `decision.md` (schema, clock, TOCTOU rule, receipt durability,
   restore protocol) and, if you choose differently, update this oracle before any
   implementation card is released — the implementer must not move the expectation while
   implementing.
