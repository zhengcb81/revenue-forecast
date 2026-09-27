# ORACLE — DEF-MSFT-CANONICAL-DUP (frozen 2026-09-27, implementer a20260926-01)

## Status
- [x] Evidence verified (see below)
- [x] Root cause pinned (code + DB + scan_runs evidence)
- [x] Fix criteria frozen
- [x] Mutations frozen (3)

## Evidence (verified against production)
- `company-wiki/.source_catalog/acquisition_attempts.jsonl`: 2 failed attempts for `sec:0001193125-26-323660` — 2026-09-19T04:53:00Z (`content_sha256=e3de0053…`) and 2026-09-27T06:16:35Z (`content_sha256=095935f9…`), both `error_type=CanonicalImportError`, `error="canonical file was written but exact provider identity did not resolve"`, `canonical_path=null`. Same failure class also on 2026-08-01 (goog `0001652044-26-000018`, cninfo 1222806982) and 2026-09-19 (hkex 12127452).
- `companies/MICROSOFT CORP/raw/financial_reports/annual/`: orphan canonical file (8,585,615B, 2026-09-19, sidecar present) + hash-suffix file `…__095935f968b5.htm` (8,585,621B, 2026-09-27, sidecar present). Bytes differ (SEC re-serve drift, +6B).
- `catalog.sqlite3`: **zero** rows for either sha; only Microsoft FY2024/FY2025 docs; `roots.last_scanned_at=2026-08-20`.
- `scan_runs`: the scans executed inside both failed imports report `status=completed_with_errors`, `files_seen=0`, `strategy={"company_raw":"adapter"}`, `error="scan_root_strategy: v2 scanner unavailable (fail closed): root 'company_raw' has no adapter_id (2.x policy required)"` (runs scan-6f9fd490 2026-09-19, scan-c4ae2c00 2026-09-27).

## Root cause (pinned)
`CanonicalSourceWriter.import_staged` (company-wiki `src/company_wiki/source_catalog/canonical_writer.py`) commits the canonical file, then indexes it with `scan_catalog(..., v2_scan_shadow=v2_scan_shadow_from_snapshot(...))` and gates success on `SourceResolver.resolve(exact_request).status == REUSED_EXACT` (lines 185-212).
- `.source_catalog/runtime_policy.json` sets `flags.v2_scan_shadow=true` (updated 2026-09-02), so the import-time scan dispatches **every** root through the v2 adapter path (`scanner.py:855 use_adapter = v2_scan_shadow or root.adapter_id is not None`).
- `config/source_catalog.yaml` declares **no `adapter_id`** for `company_raw` (only `future_lake` has one), and `adapter_dispatch` fails closed when `root.adapter_id is None` — so the company_raw scan contributes **0 files** (`completed_with_errors`, no exception).
- The just-written file is therefore never indexed → the post-write exact-identity resolution returns NOT_FOUND (first attempt, 09-19: only the new file) → `CanonicalImportError("canonical file was written but exact provider identity did not resolve")` → attempt journaled `failed`, canonical file + staging left behind, index never built.
- Replay (09-27): resolver still sees nothing (`not_found`) → re-download; SEC re-serves **different bytes** (6-byte drift) → canonical name occupied by the 09-19 orphan → writer falls back to `__<sha12>` suffix file → same dead scan → same failure. Each replay can only add another unindexed orphan.
- Why not the exact-duplicate group (`duplicate_group_id`): that group is keyed by **identical content** (`document_id` = content sha); the suffix file has a different sha, so it is a different "document" with the same provider identity — it can never join the old file's duplicate group. And with the scan fail-closed, neither file is indexed at all, so no group/handle exists. Two distinct-content documents sharing one provider identity resolve to `AMBIGUOUS` by design (resolver.py:1592) — fail-closed, not dedupable.

## Fix (minimal, per root cause — card candidate (b) + scan-mode correction)
In `canonical_writer.import_staged` only (GP-002 wiring for normal scans untouched):
1. **Scan mode**: import-time verification scan uses the root's declared adapter when it has one, else the legacy v1 scanner (`v2_scan_shadow=bool(self.company_root.adapter_id)`). For a non-adapter root the v2 dispatch cannot ever produce an index (fail-closed by definition), so the import currently can never succeed; the import is a committed write that must index what it writes, not a shadow experiment.
2. **Re-acquisition of bytes already on canonical disk**: when the computed destination (incl. `__<sha12>` fallback) already exists byte-identical to the receipt, do not rewrite the immutable provenance sidecar (it belongs to the first acquisition of these bytes; request_id/retrieved_at differ per attempt → today this dies on "immutable provenance sidecar conflict"). Identity-checked: sidecar `content_sha256`/`provider`/`provider_document_id` must match, else still fail closed.
3. **Verification adoption**: post-scan verification additionally accepts `AMBIGUOUS` when **exactly one** exact-identity match is capture-ready and carries `content_sha256 == receipt.content_sha256` (the bytes this import just committed); the result adopts that single handle as `REUSED_EXACT`. Any other non-REUSED_EXACT outcome still raises (fail closed). Rationale: sibling re-serve variants legitimately exist on disk (the 09-19 orphan stays until the owner disposes it — raw/ is read-only for this card); the committed bytes must still resolve.

## Fix criteria (green — all must hold)
- G1 Rig RED: with pre-fix code, replay `MSFT 10-K` (`--allow-download`) in the isolated rig reproduces `canonical_import_failed` (no index rows for the new sha).
- G2 Rig GREEN: with fix, the same replay ends `capture_ready` (ensure status imported/deduplicated), the committed sha is present in the rig catalog DB (documents+locations active), and no new orphan file is left unindexed.
- G3 Production replay (the single authorized ingestion write): replay `MSFT 10-K` (`--allow-download`) against production company-wiki → `capture_ready`; a new acquisition attempt row with outcome `downloaded_new`/`deduplicated_after_download` (NOT `canonical_import_failed`); the committed sha indexed in `catalog.sqlite3` (read-only check); file count in `annual/` grows by at most 1 (only if SEC served genuinely new bytes — each file on disk must end indexed; no unindexed orphans created by the replay).
- G4 No regression: relevant company-wiki unit tests (canonical writer / acquisition / resolver) pass post-fix.
- G5 Red-by-reversion: reverting each fix element (mutations M1-M3) re-introduces the corresponding failure in the rig harness.

## Mutations (frozen)
- M1: restore `v2_scan_shadow=v2_scan_shadow_from_snapshot(...)` (drop fix element 1) → import-time scan fail-closed → import fails "exact provider identity did not resolve" (the production defect signature). rc expected ≠ 0.
- M2: drop fix element 2 (always rewrite sidecar) → byte-identical re-acquisition fails "immutable provenance sidecar conflict". rc ≠ 0.
- M3: drop fix element 3 (verification demands strictly single-match REUSED_EXACT) → with sibling variant(s) indexed, verification fails "exact provider identity did not resolve". rc ≠ 0.

## Non-goals (owner decisions)
- Deleting/moving the 09-19 orphan canonical file or the 09-27 suffix file (raw/ is read-only for this card; registered in `cleanup_manifest.json`).
- Declaring `adapter_id: company_raw_v1` on the production `company_raw` root (flips the whole production root to v2 scanning — blast radius beyond this defect).
- Fixing the runtime-policy-vs-config inconsistency (`v2_scan_shadow=true` while the production root has no adapter) beyond the import seam.

## Verification addendum (resumed station `a20260926-01`, 2026-09-27)
- Status: **FROZEN** — root cause, fix criteria (G1–G5) and mutations M1–M3 above were already complete on arrival and were used verbatim; nothing in the frozen text was weakened.
- G1 Rig RED ✅ `rig/cases/red_s1.json` (production signature: `canonical_import_failed`, `canonical_path=null`, import scan `files_seen=0` / `v2 scanner unavailable (fail closed)`) and `red_s4.json` (sibling sidecar conflict).
- G2 Rig GREEN ✅ `green_s1.json` (`downloaded_new`, committed sha indexed, no unindexed file left), `green_s4.json` (`deduplicated_after_download`), `dedup_s5.json` (duplicate branch).
- G4 ✅ company-wiki canonical-writer / canonical-ingest / acquisition / resolver contract tests: **39 passed**.
- G5 ✅ red-by-reversion: M1, M2, M3 all re-introduce their failure; extended with M4 (hash-suffix fallback), M5 (identity back-fill), M6 (duplicate branch) ⇒ **6/6 caught**.
- G3 (single production ingestion replay) **deliberately not run by this station** — no production writes; left to the reviewer/owner.
- One correction inside fix element 2's scope (status-label semantics), documented in `fix_diff.md` §3; oracle criteria unchanged.
- Evidence index: `fix_diff.md`, `verification.json`, `handoff.json`, `rig/harness/*`, `rig/cases/*.json`, `rig/diff_report.txt`, `rig/diff_asfound_to_fixed.patch`, `rig/cw_git_diff_canonical_writer.patch`.
