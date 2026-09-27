# FC-906 Preflight — BLOCKED (needs user decision)

> Recorded 2026-08-11 during `/planning-with-files` “有哪些未完成的项目，从头开始一个一个实施”.
> This is a preflight finding, NOT an accepted receipt. FC-906 remains `pending`.

## Verified current triplet (2026-08-11)
- revenue `c79d7cccbbc4f84f2b8c4e9d9ad780e52e0305ff`
- filing  `6b617714f253400e6cba93c9aa7fc0fbe3ed46bc`
- wiki    `0c9adac9ce0780a0d72bc1e2b1145686aa4e9189` (dirty: `llm_cost_log.csv` — known user file)
- Dependencies FC-901..905 all `accepted` (registry confirms). Execution lock free.

## What FC-906 requires (task_plan §Phase 9 / registry)
1. normalized / markdown / sections / summary / consumer_analysis — each ≥1 real **bound** sample, or a contract reason for absence.
2. T2: artifact_read>0 **and** corresponding producer=0 (real consumption, no regeneration).
3. Includes FC-901 `artifact_bindings` **production apply** window (authorized): replica drill + before/after fingerprint + idempotent rerun + rollback, zero deletion.
4. Real samples must carry a `prompt_injection_review` receipt (FC-905-b gate: `not_reviewed` → RuntimeError, blocks consumption).

## Production catalog reality (read-only, `.source_catalog/catalog.sqlite3`, 46 GB)
| Check | Result | Verdict |
|---|---|---|
| `artifact_bindings` table | **does not exist** | FC-901 never applied. Moot now — see dry-run below (nothing to bind). |
| artifacts by role | normalized 4797 / summary 2910 / sections 11 / **markdown 0** / **consumer_analysis 0** | 2/5 roles have no artifacts at all. |
| **FC-901 production dry-run (first ever run, read-only)** | **input 7718 → bindable 0 → legacy_unbound 7718** | **DOMINANT BLOCKER.** reasons: `artifact_schema_unsupported` 7579 + `artifact_status_not_completed` 139. Zero artifacts pass the binding gate. |
| artifact v2 metadata | `schema_version`/`source_sha256` NULL on 100% of rows (column and metadata_json) | Root cause: producers (normalizer/summarizer/section_extractor) never stamped v2 binding fields. Source lineage itself IS available (23520/23521 docs have primary_source_id; 43082/43082 sources have content_sha256). |
| documents with `prompt_injection_review` receipt | **0 / 23521** | FC-905-b gate blocks ALL consumption — but moot until bindings exist. |
| `producer_events` rows | 0 | Trigger added in FC-905-a but no artifact INSERT since. |

## Reframe (supersedes the prior Q1/Q2 framing)
The corpus-wide missing v2 binding metadata is upstream of everything:
- FC-901 apply → 0 bindings (nothing to bind) until artifacts carry v2 `schema_version`+`source_sha256`.
- FC-906 "real bound sample" impossible for ALL 5 roles (not just markdown/consumer_analysis).
- Review-receipt generation (Q1) and markdown/consumer_analysis production (Q2) are both moot until the corpus is bindable.

True first work unit = make production artifacts bindable (v2 binding metadata), THEN FC-901 apply, THEN receipts, THEN FC-906 T2.

## Why this is a hard blocker (cannot self-resolve)
- `prompt_injection.py` only **records/reads** the receipt (`record_prompt_injection_review` / `read_prompt_injection_review`). There is **no automated reviewer/scanner**. Producing a receipt needs an actual review (LLM scan / policy-deterministic / human) **plus** a production `UPDATE documents.metadata_json` — both outside the “artifact_bindings apply” change-window authorization.
- markdown & consumer_analysis are downstream DAG roles (`markdown←normalized`, `consumer_analysis←summary`) that no registered generator currently produces; producing them is separate producer work.
- Per runbook rules 5 & 10 + session posture “遇 blocked/异常停下, 绝不伪造”: STOP, record, ask. Fabricating receipts or hand-waving absent roles would violate the project’s core invariant.

## Downstream dependency note
FC-1001 (Phase 10) depends on FC-906; nearly all Phase 10–15 FCs chain through it transitively. So FC-906 is the critical path — it must be unblocked; skipping is not viable.

## Decisions requested from user (reframed 2026-08-11 after dry-run)
The binding-metadata gap is the true blocker. Strategic options for unblocking:

- **A — Producer v2 update + full re-process**: update normalizer/summarizer/section_extractor to stamp `schema_version`+`source_sha256`, re-run on all docs. Most honest; huge (LLM cost for 2910 summaries, re-normalize 4797; production write to all). Multiple FCs.
- **B — Binding-metadata backfill**: new FC that stamps v2 fields onto existing completed artifacts in-place (UPDATE), deriving `source_sha256` provably from the sources table + `schema_version` from the producer contract. Smaller; retroactive certification needs FC-402 "no-guessing" rigor. Doesn't produce markdown/consumer_analysis.
- **C — Fresh v2 canary corpus (recommended for FC-906)**: produce a small set of real documents end-to-end through v2-aware producers for all 5 roles (incl. new markdown/consumer_analysis producers); legacy 7718 stay honestly legacy_unbound. Bundles producer-v2-update + markdown/consumer_analysis producers + a real canary run. Bounded; satisfies FC-906's "≥1 bound sample/role" without mass re-processing.

Plus the prior two decisions (review-receipt basis; markdown/consumer_analysis handling) fold into whichever option is chosen.
