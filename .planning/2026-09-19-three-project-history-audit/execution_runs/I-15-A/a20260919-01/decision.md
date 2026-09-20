# I-15-A decision.md — D-W15 specialist decision

> **This is a proposed decision, submitted for signature by the storage-maintenance owner
> and the independent data-recovery reviewer.** `common_wiki_cards.md` says the D-W15
> entries are "建议方案与必须冻结的决策字段，由具名高级 reviewer 在该 attempt/decision.md
> 明确选择、反例、兼容/回滚后才释放" and that "弱模型不得自行选 schema/事务/安全审核机制".
> The implementer has therefore **not** written any product code for this card: the schema,
> transaction and recovery mechanism below is a proposal plus measured counterexamples.
> Card status stays `planned`/`blocked-on-D-W15` for implementation, while the isolated
> counterexample evidence in this attempt is complete.

## D-W15-1 Archive manifest schema (proposal, needs signature)

Frozen fields the reviewer must either accept or replace:

```json
{
  "schema_version": "archive-verified-manifest-1.0",
  "catalog_identity": "<catalog dir name + schema version + db file identity>",
  "archive_path": "<absolute path of the gzip snapshot>",
  "archive_sha256": "<sha256 of the gzip bytes>",
  "archive_bytes": 0,
  "rows_in_archive": 0,
  "verified_completed_at": "<ISO-8601 UTC>",
  "span_ids": ["..."],
  "row_digests": {"<span_id>": "<sha256 of the canonical JSON row>"},
  "verifier": "<who verified, by what procedure>",
  "problems": [],
  "ok": true
}
```

Chosen canonical row digest: `sha256(json.dumps(row, sort_keys=True, separators=(",",":"),
ensure_ascii=False).encode("utf-8"))` over the archive's own row dict.

- **Why this and not a checksum of the gzip only.** The gzip hash proves the *file* did not
  change; it does not prove that the file contains the row you are about to delete. The
  measured same-day overwrite (evidence `n1-same-day-overwrite.json`: first snapshot sha
  `bccfe6a2…` with ids {a1,a2,c1}, second `7efa681c…` with ids {a1,a2,a3,b1}, **both
  reporting `ok: true`**) shows count-based reconciliation cannot distinguish these.
- **Rejected alternative A:** reuse `source_contract/source_manifest.v1.schema.json`. It
  describes *source* manifests (documents/sources), not evidence-span archive sets, and
  binding prune to it would require inventing a span-level extension anyway.
- **Rejected alternative B:** a manifest-less rule such as "archive file exists, is newer
  than X, and row count matches". This is what the code effectively does today and is
  exactly the failure mode the card names.
- **Compatibility:** additive. Old archives have no manifest; W15-R8 says they must not be
  upgraded by guessing, so they stay unusable for prune until a separately specified
  verification is run. That is a deliberate non-goal for this card.

## D-W15-2 Retention clock (proposal)

`due = (now_utc - manifest.verified_completed_at).days >= retention_days`, with `now`
injected as an explicit parameter (the harness's fixed clock is `2026-09-19T00:00:00Z`).

- **Counterexample measured** (`n2-clock.json`): directory name `2021-01-01` with
  `verified_completed_at = 2026-09-18T00:00:00Z` (1 day old) → current code computed
  `due: true` and deleted 4 rows. The directory name is not evidence.
- Alternative rejected: file mtime. It is not part of the verified manifest and is trivially
  reset by a copy/restore, which would *extend* the window silently.

## D-W15-3 Exact set + plan hash + TOCTOU (proposal)

Dry run emits `{span_ids, plan_hash, archive_sha256, verified_completed_at,
retention_days}`; `apply` re-reads the archive (sha256 must match), re-reads every planned
row digest and `documents.source_status`, recomputes the plan hash and **aborts the whole
apply** on any mismatch.

- **Counterexample measured** (`fault-recovery.json`): after freezing the plan for {a1,a2},
  `a2`'s `raw_text` was mutated and the current code deleted `a1, a2, a3, b1` — it deleted a
  row whose frozen digest no longer matched, plus two rows that were never in the plan.
- Explicitly forbidden by the frozen oracle: "silently narrowing the set" (deleting the
  still-matching subset and reporting success). The card says apply must refuse and require
  a new plan.
- Locking: `CatalogOperationLock(config.catalog_dir, operation="prune_retired_evidence")`
  already exists and is reused; the re-verification must happen **inside** the lock.

## D-W15-4 Batch receipts and crash recovery (proposal, needs signature)

Per-batch receipt written **before** the batch commits nothing is impossible; the proposal
is: (a) compute the exact id set up front, (b) write a `pending` receipt that names the full
plan, (c) after each batch commit, append the committed ids to the receipt, (d) on restart,
read the receipt and only re-plan the ids that are still present, never widening the set.

- **Counterexample measured** (`n4-crash-receipt-absence.json`): the current receipt is
  written only after the whole loop (`prune_retired_evidence.py:125-142`). A crash after the
  first batch commit left 4 rows deleted with `receipt_files: []` — the exact deleted set is
  unrecoverable from any durable artifact.
- Reviewer must decide the receipt's durability medium (same SQLite DB in a table vs a JSON
  file under `artifacts/gates`). The implementer did not choose, because this is the
  "cross-process lock and crash recovery mechanism" that START_HERE reserves for a
  specialist decision.

## D-W15-5 Restore protocol (proposal)

Restore proves recoverability by **row digest identity**, not by row count. Evidence
`restore-proof.json`: archives rows a1/a2 restored into an independent empty scratch catalog
reproduce identical digests (`615eed4a…`, `64e883ee…`), and `c1` — which is inside the same
verified archive but whose document is active — is **refused** (`refused_ids: ["c1"]`).

- Rejected alternative: "restore by re-running the archiver". The archiver reads current
  state, so it cannot reproduce a deleted row.
- Scope limit: this proof is in scratch only. It does not authorise, and must not be read as
  authorising, a production prune or a D:-drive migration.

## Non-decisions (explicitly NA)

- **No production cleanup.** The card forbids it; nothing in this attempt ran against the
  production catalog or the production archive.
- **No CLI invented.** `prune-retired-evidence --apply` exists but is a production command;
  this attempt never invoked it. There is no supported restore CLI (`CMD-W10` note), so the
  restore proof uses an attempt-owned procedure.
- **No schema migration executed.** The manifest lives outside the DB in this proposal; if
  the reviewer chooses a DB table, that is a schema change and needs its own card.
- **`section_query.py` / `reconcile_retire_state.py`** were read only (hashes in
  binding.json); they are neighbours named by the audit row, not part of this card's change.
