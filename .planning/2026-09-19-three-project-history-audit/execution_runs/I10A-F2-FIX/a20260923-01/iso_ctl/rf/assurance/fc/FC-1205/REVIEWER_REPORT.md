# FC-1205 — Independent Review Report (r1)

- **FC**: FC-1205 错误和编码一致性 — PORT-01~03 closure (Phase 12 last FC)
- **Reviewer**: reviewer-fc1205-independent
- **Implementer**: honest-implementer
- **Decision**: ACCEPTED (zero blocking findings)
- **Reviewed at**: 2026-08-13T02:34:38Z
- **Method**: full from-scratch replay in clean worktrees under
  `C:/Users/郑曾波/Projects/.fcap-review/fc-1205/`. F-6 rule honored — zero
  `git checkout <rev> -- <paths>` anywhere; mutations via reverse edits only;
  main checkouts untouched.

## Triplets (rev-parsed, never hand-written)

| repo | base | result (fcap tip) |
|---|---|---|
| revenue | `91cbc137916b1ab7571e199555fddfa4115d914b` | `58db948678d7a04b525fe57006cf9a9658f133bf` |
| filing | `83c638e76e40890262746cdf02b6df495dcb4031` | `83c638e76e40890262746cdf02b6df495dcb4031` (unchanged) |
| wiki | `925b3e8027f9c22c475656efae98142b976244e6` | `b93994ae27201563c6789d1f8242bf53295eda68` |

Worktrees: `fc-1205/revenue-base` @ 91cbc13, `fc-1205/revenue-forecast` @ 58db948
(moved from `revenue-result` — see Step 4 artifact note), `fc-1205/wiki-base` @
925b3e8, `fc-1205/wiki-result` @ b93994a, `fc-1205/filing-fetch` @ 83c638e.
A transient junction `fc-1205/company-wiki -> wiki-result` was created for the
revenue sibling-layout tests and removed afterwards (FC-1204 r3 precedent).

Environment verified: `PYTHONIOENCODING=None`, `PYTHONUTF8=None`
(Python 3.13.9 / Miniconda, Chinese-locale Windows) before every run.

## Step 1 — commits + full diffs

- wiki `b93994a` "fix(fc-1205): UTF-8 stdio reconfigure in unique-test-symbol
  gate": only `tools/check_unique_test_symbols.py`, +12/−0. Exactly the claimed
  reconfigure block (`encoding="utf-8"`, `errors="strict"`) before argparse.
- revenue `e60ed1c` "fix(fc-1205): UTF-8 subprocess decode + stdio reconfigure":
  only `tools/audit_baseline.py`, +23/−1. Exactly the claimed three edits:
  `encoding="utf-8", errors="replace"` on `_git()` and `version_of()`, and the
  stdout/stderr reconfigure block in `main()` before argparse.
- revenue `58db948` "docs(fc-1205)": only `assurance/fc/FC-1205/00_wu_card.md`,
  `11_implementer_receipt.json`, `audit_review/.../progress.md` (+179/−0).
- The base..result range additionally contains `65c2b87` "docs(fc-1204): ACCEPTED
  r3" (FC-1204 acceptance docs: FC-1204 receipts/report + task_plan + registry) —
  attributable to FC-1204 closure, docs-only. Full range stat: 9 files,
  476 insertions / 14 deletions; the ONLY non-docs change is
  `tools/audit_baseline.py`. No extra changes anywhere.

Both fix commits contain a duplicated comment block (the FC-1205 comment is
repeated twice verbatim in each `main()`) — cosmetic, see finding F1.

## Step 2 — RED at base (no PYTHONIOENCODING)

- wiki-base `python -B -m pytest tests/contract/test_check_unique_test_symbols.py -q`
  → **2 failed, 3 passed** — `test_duplicate_test_definition_fails` +
  `test_syntax_error_is_reported_as_failure`. Reader-thread
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd4 ...` and
  `... byte 0xa1 ...` — the exact GBK-pipe mechanism claimed.
- revenue-base `python -B -m pytest tools/tests/test_audit_baseline.py -q`
  → **1 failed, 4 passed** — `test_collects_baseline_facts`, reader-thread
  `UnicodeDecodeError ... byte 0xd4 in position 363`.

## Step 3 — GREEN at result

- wiki-result: same contract file → **5 passed**.
- revenue-forecast: `tools/tests/test_audit_baseline.py` → **5 passed**.

## Step 4 — full suites at result, no PYTHONIOENCODING

- wiki-result `python -B -m pytest tests/ -q` →
  **2232 passed, 3 skipped, 0 failed (458.28s)** — matches the implementer's
  2232/3/0 claim. No worker_bootstrap timing flake this run.
- revenue-forecast `python -B -m pytest tests/ tools/tests/ -q` →
  **516 passed, 2 warnings, 106 subtests passed, 0 failed (249.85s)** — matches
  the implementer's 516/0/106 claim.

  *Layout-artifact episode (recorded for the replay trail, not a code finding):*
  the first full-suite run, in a worktree named `revenue-result`, produced
  14 failed / 502 passed. All 14 were the known isolated-worktree sibling-layout
  artifact: `compatibility/compatibility_manifest.py` (`REPO_DIRS`) and
  `test_fc1101_ci_manifest.py` resolve the revenue repo itself as
  `PROJECT_ROOT.parent / "revenue-forecast"` (WinError 267 / exit 128). Moving
  the worktree to the canonical name `revenue-forecast` (FC-1204 r3 precedent,
  `git worktree move`) made all 33 tests in the 4 affected files pass, and the
  re-run full suite went 516/0. This is the same artifact class FC-1204's
  reviewer documented for its E2E tests; it does not affect the implementer's
  claim (their run was in the main checkout at the correct layout).

Both full suites are the first zero-failure runs observed in this FCAP — the
claim verified directly.

## Step 5 — mutations (reverse edits; kill → revert → re-green)

- **M1 wiki** — removed the reconfigure block from
  `tools/check_unique_test_symbols.py` → contract test **2 failed / 3 passed**
  (GBK 0xd4/0xa1 reader-thread errors return) → reverted via reverse edit →
  **5 passed**, worktree clean.
- **M2 revenue** — removed only the `main()` reconfigure block from
  `tools/audit_baseline.py` (subprocess `encoding/errors` kept) →
  `test_collects_baseline_facts` **FAILS** (GBK 0xd4 reader-thread) → reverted →
  **5 passed**, worktree clean.

Both mutations kill exactly the claimed tests and nothing else; both reverts
restore green with `git status --porcelain` empty.

## Step 6 — PORT-03 CI definitions (result tips)

`runs-on: ubuntu-latest` present in all three workflows at result tips:
- revenue `.github/workflows/quality.yml` line 9
- filing `.github/workflows/quality.yml` line 9
- wiki `.github/workflows/ci.yml` lines 11/63/83/101 (4 jobs)

Linux-golden scenario is not locally reproducible on Windows; the CI
definitions are the claim, and they are as stated. No local fabrication.

## Step 7 — implementer receipt validation

`python tools/receipt_validator.py --receipt assurance/fc/FC-1205/11_implementer_receipt.json`
→ **OK: 1 receipt(s) valid**. Content audit: base_triplet correct (91cbc13 /
83c638e / 925b3e8); result_triplet records the fix commits (revenue e60ed1c,
wiki b93994a, filing 83c638e — excludes the docs-seal commit 58db948, per the
FC-1204 convention); scenario results PORT-01/02/03 and command notes match the
independently measured numbers (516/0/106, 2232/3/0, M1/M2 kills).

## Findings

| id | severity | issue |
|---|---|---|
| F1 | info (cosmetic) | Both fix commits carry the FC-1205 comment block twice, verbatim, in `main()` (wiki `tools/check_unique_test_symbols.py` and revenue `tools/audit_baseline.py`). Zero functional impact; a later tidy-up commit may deduplicate. |
| F2 | info (observation) | The revenue full suite shows 2 pre-existing `PytestUnhandledThreadExceptionWarning`s (reader-thread UnicodeDecodeError, GBK byte 0xd4) from `tests/test_fc1004_platform.py::test_install_sync_gate_detects_drift` — `tools/sync_installations.py` is a third GBK-pipe site outside PORT-01's declared two-site scope. Verified present at base with identical behavior (1 passed, 2 warnings); warning-only today because the test never consumes stdout on success. Recommend a follow-up (same fetch_filing reconfigure pattern) — does not block this FC. |
| F3 | info (process) | Full-suite replay in an isolated worktree requires the canonical sibling names (`revenue-forecast`, `filing-fetch`, `company-wiki`) — see Step 4. Documented for future replays. |

## Verdict

**ACCEPTED.** The two FC-1205 diffs are exactly as claimed (two tool files +
docs; nothing else in the range). RED reproduced at base (wiki 2 failed with
GBK 0xd4/0xa1, revenue 1 failed), GREEN at result (5/5 each), both full suites
run zero-failure without any encoding environment variables (revenue
516/0/106-subtests, wiki 2232/3/0 — the first zero-failure runs in the FCAP),
M1/M2 mutation kills confirmed and reverted, PORT-03 CI definitions verified
at result tips, implementer receipt structurally valid. Three non-blocking
info findings (duplicated comment; pre-existing warning-only GBK site in
sync_installations.py; worktree-naming note for future replays).
