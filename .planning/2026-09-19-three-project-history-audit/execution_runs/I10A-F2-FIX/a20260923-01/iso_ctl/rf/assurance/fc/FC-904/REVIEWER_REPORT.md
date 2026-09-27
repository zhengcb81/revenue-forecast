# FC-904 Independent Review Report

Reviewer: `reviewer-fc904-independent` (distinct agent from `fc904-implementer`)
Clean checkout: `C:/Users/郑曾波/Projects/.fcap-review/fc-904` (detached HEAD)
Date: 2026-08-11

## 1. Triplet & checkout verification (passed)

- Worktree HEAD = `0cef23d53b774219c573fd15c85d4a143bb51951` — matches result triplet revenue hash. `git status --porcelain` clean.
- Filing repo HEAD = `959d04cdbe2115c8e01fa39a2d5dfe748cc4fedd`; wiki repo HEAD = `fd4f50b7566bf26997062404594bc78209246a1f` — both match result triplet; base commit `07578a3c` exists and is the parent of HEAD.

## 2. Hash recomputation (passed)

- plan `task_plan.md` sha256 = `0bc6b9f7d6707e470e55c22759d37c18404172081ecd176d2883e184c61fafaa` ✓ (expected 0bc6b9f7...)
- `compatibility/command_registry.json` sha256 = `215b8077169126b2c4a5eca9d8d6237f291757c2559f6ae6e0ae8ff1c806b089` ✓ (expected 215b8077...)

## 3. Dependency receipts (passed)

- filing-fetch `assurance/fc/FC-903/12_reviewer_receipt.json`: verdict `accepted`, reviewer `reviewer-fc903-independent`, 2026-08-11T09:40:00Z.
- company-wiki `assurance/fc/FC-902/12_reviewer_receipt.json`: verdict `accepted`, reviewer `reviewer-fc902-independent`, 2026-08-11T08:15:20Z.
- Both repos' HEADs match the result triplet; receipts fresh (same day).

## 4. Implementer receipt

- sha256 = `46f96653035fe5c1d11fa8e21e8f79c513b458a2a9f134a851c5fd24b864ce2d`
- Schema 2.0, status `independent_review`, mode `honest-implementer`, dependency receipts listed, base/result triplets correct.

## 5. Diff scope (passed with 2 documentation-only extras)

`git diff 07578a3c..HEAD --stat` → 10 files. The 8 allowlisted files (2 scripts + 4 migrated test fixtures + new 11-test file + change contract) are present. Two extras, both plan-directory documentation, no runtime impact:

1. `audit_review/2026-08-09_full_completion_assurance_plan/progress.md` (+17) — established convention (every prior FC commit updates it).
2. `audit_review/2026-08-09_full_completion_assurance_plan/fc_904_change_contract.md` (added) — byte-identical duplicate of `assurance/fc/FC-904/03_change_contract.md`; no precedent in history. Recorded as finding FC-904-F2 (low).

## 6. Code + tests adversarial read (all checks passed)

- **DAG-ancestor gate correct**: `_dag_ancestors` walks `ROLE_DEPENDENCIES[role]` (direct parents) transitively — direction verified against company-wiki `src/company_wiki/source_catalog/artifact_dag.py` (`ROLE_DEPENDENCIES = {normalized: [], markdown: [normalized], summary: [markdown], sections: [normalized], consumer_analysis: [summary]}`). A role is read only when every ancestor is reusable (AR-03).
- **producer_events = DAG closure**: `_dag_closure` returns role + transitive dependents, matching company-wiki's own `_downstream`; computed only over non-reusable roles — never blind full recompute (AR-02: closure of summary = summary+consumer_analysis only).
- **ROLE_DEPENDENCIES imported** from `company_wiki.source_catalog.artifact_dag` in both helpers — no duplicated literal (contract single-source-of-truth honored).
- **Unsourced path gone**: `payload.get("selected_artifacts")` absent from source_preparation.py (only a comment remains); receipt now carries `artifact_read` + `producer_events` sourced from the envelope bundle.
- **bundle=None honest**: `_bundle_from_handle` None (bundle_status=unavailable) → `artifact_read=[]`, `producer_events=all roles` — honest, not faked (2 tests cover this at both selector and prepare_source levels).
- **Malformed bundle fail-closed**: non-dict bundle and non-dict `valid_handles` both raise `CompanyWikiSourceError`.
- **4 migrated fixture files** use the envelope contract consistently (`resolution_envelope.bundle`); leftover `source_bundle` strings are comments/docstrings only (grep-verified, no code path).
- **No new catalog/root writes**: only file I/O in company_wiki_source.py is a pre-existing read (line 64, outside the diff).
- **ruff-clean** on all changed files; `py_compile` OK; exactly 1 production caller of the selector (source_preparation.py:110).

## 7. Command replays

| Command | Result |
|---|---|
| `python -B -m pytest tests/test_fc904_artifact_selection.py -q` | **11 passed** (0.40s) — matches receipt |
| `python -B -m pytest <5 fixture files> -q` | **36 passed** (1.03s) — receipt claims 38; actual collected count at HEAD is exactly 36 (11+6+4+6+9; identical at base). No skips/xfails. Finding FC-904-F1. |
| `python -B -m ruff check <2 scripts + 5 test files>` | **All checks passed** |
| `python -B -m pytest tests/ -q` (full suite) | **396 collected / 384 passed / 106 subtests / 12 failed** (20.31s). Registry `revenue.unit.tests` expects ≥347 — met. |
| RED replay: `git show 07578a3:scripts/company_wiki_source.py | grep -c select_artifact_roles` | **0** — selector did not exist at base (RED honest) |

### Full-suite failure attribution (all 12 environmental, proven by base comparison)

The 12 failures at HEAD are all sibling-repo layout artifacts of the review worktree (`.fcap-review/fc-904` has no `../filing-fetch`, `../company-wiki`, or the `filing_contracts` package):

- 9 x `tests/test_compatibility_manifest.py` — `git merge-base` subprocess cwd invalid (NotADirectoryError WinError 267).
- 1 x `tests/test_contract_registry.py::test_every_contract_canonical_doc_exists_on_disk` — expected ADR-010 at `.fcap-review/company-wiki/docs/adr/...` (missing sibling).
- 1 x `tests/test_dropbox_full_chain_fc505.py` — `ModuleNotFoundError: filing_contracts`.
- 1 x `tests/test_preparation_e2e_success.py::test_full_chain_hits_fixture_record` — `filing-fetch script not found at .fcap-review/filing-fetch/scripts/fetch_filing.py`.

**Base comparison**: same suite at base `07578a3c` in an identical worktree layout → `12 failed, 373 passed, 106 subtests`. The 12-failure set is byte-identical (diff of sorted FAILED lists = empty). HEAD therefore adds exactly the 11 new FC-904 tests to the passing set and introduces **zero new failures**. None of the 12 touch FC-904 changed code.

## 8. Mutation replays (all three killed; each restored; 11 passed re-verified)

| Mutation | Change | Target test | Result |
|---|---|---|---|
| FC-904-M1 | DAG gate `and all(...)` → `and True` | test_ar03_normalized_missing_dag_invalidation | **FAILED** (killed) |
| FC-904-M2 | `_bundle_from_handle` → `return None` | test_ar01_valid_roles_read | **FAILED** (killed) |
| FC-904-M3 | `missing = list(roles)` (blind recompute) | test_ar02_only_summary_missing | **FAILED** (killed) |

After restores: `git status --porcelain` clean, `test_fc904_artifact_selection.py` 11 passed.

## 9. Side-effect reconciliation (passed)

Selection is in-memory over the envelope bundle; zero new file reads/writes; no catalog/root writes; downloads/llm/parser counts unchanged (0 in receipt paths). Matches receipt's side_effect_counts.

## 10. CodeGraph reachability (passed with note)

Index (124 files / 2201 nodes) contains `select_artifact_roles` at `scripts/company_wiki_source.py:147` with correct signature and the test import edge. The index emits **no** caller edges repo-wide (pre-existing `build_revenue_source_record`, `_analysis_provenance_matches` also report zero callers), so the production edge `prepare_source → select_artifact_roles` was verified by direct source read + passing prepare_source tests; exactly 1 production caller as claimed.

## 11. Rollback (passed)

Single commit `0cef23d`; revert = revert commit. No data migration, no external state.

## Findings

- **FC-904-F1 (low)**: implementer receipt overclaims counts — "38 passed" vs actual 36 for the focused suite (reproducible in no checkout); "396 passed, zero failures" vs 384 passed + 12 env-layout failures in the clean checkout (identical at base; total collected 396 is correct). No test skipped/hidden.
- **FC-904-F2 (low)**: commit adds byte-identical duplicate change contract under audit_review/ (outside allowlist, no precedent).

## Verdict

**accepted** — all 8 AR/RECEIPT scenarios pass, 11/11 focused tests, 3/3 mutations killed, zero new failures vs base, side-effect budget respected, rollback trivial.
