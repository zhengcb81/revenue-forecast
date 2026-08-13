# FC-1204 Independent Review — Replay Report

- **Reviewer**: reviewer-fc1204-independent (fresh-context replay, clean worktrees only)
- **Implementer receipt**: `11_implementer_receipt.json` (validated OK structurally)
- **Date**: 2026-08-13T00:43Z
- **Decision**: **REJECTED** — 1 blocking finding (committed CI mypy steps red for filing + wiki), 1 major finding (false mutation records in the implementer receipt), 4 info findings.
- **F-6 compliance**: zero `git checkout <rev> -- <paths>` anywhere. All reproduction in git worktrees under `C:/Users/郑曾波/Projects/.fcap-review/fc-1204/` (base-* at the base triplet, result worktrees first at result-*, then `git worktree move`d to `layout/{revenue-forecast,filing-fetch,company-wiki}` so revenue's sibling-relative tests resolve the same way they do in the real checkout layout). All mutations reverted via reverse edits / backup-file restore (mv back). Main checkouts' working files untouched throughout (read-only git show/log/diff/rev-parse + receipt validator only).

## Environment

- Python 3.13.9 (global), pytest 9.0.1, pytest-cov, mypy 1.19.0, radon 6.0.1 — same toolchain the implementer recorded (findings 61).
- Six worktrees created via `git worktree add` at: base {revenue 9315ddf, filing b7ef9cc, wiki 460d273}, result {revenue 4750fec, filing 93aa5ad, wiki f03142c}. All rev-parsed; all match the implementer receipt's triplet values exactly.
- The wiki `.venv` has no pytest/mypy (verified) — the implementer must have used the global interpreter; I did the same.

## Step 1 — Commits + per-commit diffs

- All commits exist on fcap: revenue `17e6354 → 4750fec → e83feca`; filing `93aa5ad`; wiki `f03142c`. `e83feca` verified docs-only (adds `11_implementer_receipt.json` only).
- **revenue 17e6354**: mypy.ini (namespace_packages=True, explicit_package_bases=True, follow_imports=skip), quality.yml mypy step, document.py (4 edits: filtered-generator isclose check with walrus, 2 asserts, 1 annotation removal), evidence.py (require() bool→Any truthiness gate + 3 asserts) — matches the brief exactly. 8 narrowing edits total.
- **revenue 4750fec** (the split): exhaustive verification performed.
  - Four extracted blocks vs base line ranges — all VERBATIM modulo indentation (whitespace-normalized equality, line counts equal):
    - `_recompute_consolidated_paths` base[342-427] = 86 lines = helper body 86
    - `_validate_confidence_block` base[906-926] = 21 = 21
    - `_validate_theme_analysis` base[1093-1146] = 54 = 54
    - `_validate_receipt_blocks` base[1147-1165] = 19 = 19
  - Call sites pass the exact parameter sets (each found exactly once).
  - Whole-file multiset diff (every non-blank content line, multiplicity-aware, after removing only the 4 def lines / 4 docstrings / 4 call lines): the ONLY difference is one extra `if theme is not None:` line (see F3). Nothing else added, removed, or reordered.
  - CC with the ratchet's own algorithm (`test_complexity_ratchet._max_complexity`): base revenue_report.py = **174**, result = **150**; helpers 15/2/8/4 (all ≤15).
- **filing 93aa5ad**: exactly 3 files (quality.yml + 2 new test files). Gap test count verified = 21 (5 auth + 8 envelope + 3 handle + 5 client guards). Ratchet frozen {fetch_filing 33, filing_contracts 39}, NEW_FILE_MAX 10.
- **wiki f03142c**: exactly 6 files (ci.yml, pyproject.toml, requirements.txt, 3 new test files). Coverage ratchet: TIER1 16 modules floor 95, TIER2 8 frozen, FROZEN 57, `FC1204_COVERAGE_GATE=1` env gate, 0.5pt tolerance, combined formula `(covered_lines+covered_branches)/(num_statements+num_branches)`. tier1_gaps = 13 tests. Complexity ratchet: 81 frozen files + NEW_FILE_MAX 10.
- Changed-files cross-check vs receipt: revenue 9/9 (excluding the receipt itself), filing 3/3, wiki 6/6 for the FC-1204 commit itself. The wiki base..result delta additionally contains 3 FC-1203 acceptance files from the intermediate commit `2268970` (FC-1203 closure) — correctly not listed as FC-1204 changed files (see F5).

## Step 2 — Focused tests (result worktrees)

- revenue `python -B -m pytest tests/test_output_report.py tools/tests/test_complexity_ratchet.py -q` → **25 passed** (23+2).
- filing `python -B -m pytest tests/test_fc1204_coverage_gap.py tests/test_complexity_ratchet.py -q` → **23 passed**.
- wiki `python -B -m pytest tests/contract/test_fc1204_tier1_gaps.py tests/contract/test_fc1204_complexity_ratchet.py -q` → **15 passed** (13+2); coverage ratchet alone → 2 skipped (in-suite skip by design).

## Step 3 — Type checks (exact CI commands) → BLOCKING FINDING

- revenue `python -m mypy scripts/contracts/ scripts/schema_compatibility.py scripts/filing_fetch_client.py scripts/trust_anchor.py` → **Success, 0 errors in 7 files** ✓ (base without mypy.ini: 35 errors — matches findings 61).
- filing `python -m mypy scripts/filing_contracts.py scripts/fetch_filing.py` → **1 error**: `fetch_filing.py:709: Argument "gap_plan" to "_close_gap_and_return_handle" has incompatible type "Any | None"; expected "dict[Any, Any]"`. The callee is local (line 803, `gap_plan: dict`), the code is unchanged from base, and the error reproduces under `--python-version 3.12` and with `PYTHONPATH=<wiki>/src` (CI's exact setup). The receipt's "Success: no issues found (0 errors)" is **not reproducible** with any documented invocation.
- wiki (11 modules, exact CI command) → **78 errors in 17 files** (67 excluding the 11 Windows-fcntl errors in lock.py — the remaining 67 are platform-independent: normalizer 18, scanner 15, security_identity 7, adapter_process 6, acquisition_service 6, source_contract/* ~10, etc.). `--no-check-untyped-defs` does not change the count. Only `--follow-imports=skip` (a flag present in **no committed config and no CI step**) reproduces the receipt's "Success: no issues found in 11 source files". With the committed pyproject (`mypy_path=src`, `python_version=3.11`, `check_untyped_defs=true`, yaml override only), the import-followed dependency modules fail.
- **Consequence**: both committed CI mypy steps (filing quality.yml, wiki ci.yml) are red as written. The FC-1204 exit gate "mypy 契约模块集三仓 0 error（CI 门）" is not met for 2 of 3 repos. Likely fix: add `follow_imports = skip` to the wiki pyproject `[tool.mypy]` (mirroring revenue's mypy.ini), and narrow/annotate `fetch_filing.py` around line 709 (or otherwise make the CI command green), then re-verify — see F1.

## Step 4 — RED-at-base (base worktrees)

- revenue: copied result ratchet test onto base → `FAILED ... revenue_report.py max 174 > 150` (1 failed / 1 passed) — exactly the right reason; the split was necessary for the 174→150 downward move. Copy removed.
- filing: copied the 2 new test files onto base → 23 passed (guards pre-exist at base; honest RED is measurement, per the brief). Base coverage run: **TOTAL 88.05%** (fetch_filing 87%, contracts 91%), and with `--cov-fail-under=90` → **EXIT=1** ("Required test coverage of 90.0% not reached"). Result run: 91.03% / 97% / EXIT=0. Files removed.
- wiki: copied the 3 new test files onto base → 15 passed + 2 skipped (behavior pre-exists; RED is measurement). Base full coverage (2215 passed / 2 failed / 1 skipped, the PORT-01 pair — identical at result): per-module gate formula gives **restore.py 93.0, policy.py 93.1, admission.py 94.0, scheduler_policy.py 92.9, visibility_bridge.py 93.2** — all below the 95 floor; running the unmodified gate with `FC1204_COVERAGE_GATE=1` against the base coverage.json FAILS (`admission.py branch coverage 94.0% < 95% (required)`). Result deltas: restore 100.0, policy 100.0, admission 98.8, scheduler_policy 100.0, visibility_bridge 100.0. Files removed; artifacts cleaned.

## Step 5 — Mutations (result worktrees; reverse-edit reverted; re-verified green)

- **M1 (revenue, in-line the theme block back into `_validate_forecast_output`, delete helper)** → KILL CONFIRMED: `revenue_report.py max 156 > 150`. Reverted (backup mv); ratchet re-green 2 passed; clean.
- **M2 (wiki, remove the FC1204_COVERAGE_GATE env check; in-suite against a STALE coverage.json = the base measurement)** → KILL CONFIRMED: `admission.py branch coverage 94.0% < 95% (required)` (1 failed / 1 passed). Also verified: unmutated + `FC1204_COVERAGE_GATE=1` + stale base coverage.json → FAILS (gate correctly refuses stale data); unmutated + no env → 2 skipped. Reverted; clean; re-green.
- **M3 (filing, raise FROZEN_MAX fetch_filing 33→90)** → **NO KILL: 2 passed.** The committed ratchet asserts `actual <= frozen`, so weakening the table passes. The implementer receipt records "KILL CONFIRMED — inner pytest exited 1" for this exact mutation; it does not reproduce. (Additional check: the implementer's wiki M2 variant, lowering the restore floor 95→90 with env=1 on fresh data, also passes — 2 passed. The tier-1 table has no integrity assertion.) The ratchets are one-directional by design (table edits are the deliberate-review path), which is a defensible design — but the receipt's mutation records are factually wrong. See F2.

## Step 6 — Full coverage + suite validation (result worktrees)

- filing (hermetic + coverage + gate): **312 passed / 6 skipped / 54 subtests; TOTAL 91.03%; filing_contracts 97%; "Required test coverage of 90% reached"; EXIT=0** — exact match to the receipt.
- wiki (full + coverage): **2230 passed / 2 failed / 3 skipped (479s); TOTAL 81%**. The 2 failures = the pre-existing PORT-01 pair (`test_check_unique_test_symbols`), identical names at base. Then `FC1204_COVERAGE_GATE=1 python -B -m pytest tests/contract/test_fc1204_coverage_ratchet.py -q` → **2 passed** on the fresh coverage.json. Exact match to the receipt.
- revenue (`python -B -m pytest tests/ tools/tests/ -q`, run from the `layout/revenue-forecast` worktree so sibling resolution matches the real checkout): **510 passed / 6 failed**. Failure decomposition: 1 = `tools/tests/test_audit_baseline.py::test_collects_baseline_facts` — verified **pre-existing** (fails identically at base 9315ddf); 5 = chain tests (fc1002 ×3, fc1003 ×1, fc1004 ×1) that hard-code `as_of_date: "2026-08-12"` — today (2026-08-13) "published <= captured <= as_of" rejects captures stamped after as_of. Proven environmental: rolling the fixture dates to 2026-08-13 makes all 10 chain tests in those files pass (then reverted). None of these tests is touched by FC-1204. Net: matches the brief's "513-ish passed / 1 failed" modulo the day boundary.

## Step 7 — E2E golden identity (revenue)

- `python e2e/run_revenue_forecast_e2e.py` on the result worktree → **E2E PASS, result hash fedcd224acf28dee — IDENTICAL to the pre-split golden**, deterministic double-run identical (STEP 9/10 ok), `repo_head=4750fecd`. Strongest behavior-preservation evidence for the split.

## Step 8 — Receipt validation

- `python tools/receipt_validator.py --receipt assurance/fc/FC-1204/11_implementer_receipt.json` → **OK: 1 receipt(s) valid** (structural; the validator does not verify claim truthfulness — claims were verified independently above).

## Findings

- **F1 (BLOCKING)** — Committed CI mypy steps red for filing (1 error) and wiki (78 errors; 0 only with an undocumented `--follow-imports=skip`). The implementer receipt's 0-error claims for both repos are unreproducible with the committed commands/config. The wiki pyproject `[tool.mypy]` lacks `follow_imports = skip` (present in revenue's mypy.ini for the same reason), and `fetch_filing.py:709` needs narrowing/annotation. Required before acceptance: make both CI commands actually green and re-verify from clean checkouts.
- **F2 (MAJOR)** — Implementer receipt mutation records do not reproduce: M3 (filing frozen 33→90) and the receipt's M2 variant (floor 95→90) both **pass** against the committed tests — the recorded "KILL CONFIRMED — inner pytest exited 1" for each is false. The ratchets are one-directional by design (the table edit is the deliberate-review path, which the receipt's own note half-acknowledges for M2); either the tests need table-integrity assertions or the receipt must describe the true behavior. My independent mutations M1 and M2 (env-check removal, per the brief) killed with exactly the right reasons.
- **F3 (INFO)** — The `_validate_theme_analysis` extraction duplicates the `if theme is not None:` guard: base line 1093 was moved into the helper AND retained at the call site (multiset diff shows exactly one extra line). Behavior-identical; adds +1 CC to the helper (CC 8, still ≤15). Verbatim check against the brief's stated range [1093-1146] holds.
- **F4 (INFO)** — Implementer docs are inconsistent on the revenue mypy baseline: findings 61 says 35 errors, the receipt command note says 45. Independent base measurement: 35.
- **F5 (INFO)** — The wiki result_triplet spans two commits: `2268970` (FC-1203 acceptance artifacts) + `f03142c` (FC-1204). The receipt's changed_files correctly lists only f03142c's 6 files; the 3 FC-1203 files in the delta belong to FC-1203's closure.
- **F6 (INFO)** — Revenue chain tests (fc1002/fc1003/fc1004) hard-code `as_of_date: 2026-08-12`; they fail on any date after 2026-08-12 regardless of code state (proven by date-roll experiment). Pre-existing fixture pattern, not FC-1204 scope, but worth a follow-up FC.

## Verdict

REJECTED. Everything verified positive except the type-check gates (F1, blocking) and the receipt's mutation records (F2, major). The split itself is exemplary — verbatim blocks, exact parameter sets, CC 174→150 with helpers ≤15, golden E2E hash identical, focused tests green, and all three coverage claims (filing 91.03%/97%, wiki 2230-passed + gate green, tier1 deltas 93→100) reproduce exactly. Recommended remediation: (1) add `follow_imports = skip` to wiki pyproject `[tool.mypy]` and fix `fetch_filing.py:709` narrowing (or annotate), re-run both CI commands to 0; (2) correct the receipt's M2/M3 mutation records (or add table-integrity assertions to the ratchet tests); (3) optionally fix the duplicate theme guard. Re-review only needs to cover the remediated mypy step + receipt corrections.

---

# FC-1204 r2 Re-Review (remediation of F1-F6)

- **Reviewer**: reviewer-fc1204-independent (r2 replay, clean worktrees only)
- **r2 result commits**: revenue `387e6ac` (F2/F3/F6 remediation + receipt update), filing `83c638e` (F1: gap_plan assert + ratchet 33→34), wiki `925b3e8` (F1: follow_imports=skip)
- **Date**: 2026-08-13T01:24Z
- **Decision**: **REJECTED — 1 blocking finding (F7) remains; F1/F2/F3/F5/F6 all verified fixed.** The remaining item is trivial (3 new ruff E402 violations introduced by the F6 fix itself).

## r2 verification (fresh worktrees under `.fcap-review/fc-1204/r2/{revenue-forecast,filing-fetch,company-wiki}` at the fcap tips; F-6 honored; mutations reverted via reverse edits)

### a) mypy — exact CI commands → 0/0/0 ✓ (F1 FIXED)
- wiki (11 modules, committed pyproject with `follow_imports = "skip"`): **Success: no issues found in 11 source files**.
- filing (`PYTHONPATH=<r2 wiki>/src python -m mypy scripts/filing_contracts.py scripts/fetch_filing.py`): **Success: no issues found in 2 source files** — the `assert isinstance(gap_plan, dict)` narrows line 709. `--python-version 3.12` also clean.
- revenue (7 files): **Success: no issues found in 7 source files** (unchanged from r1).

### b) M2/M3 real mutations — replayed ✓ (F2 FIXED)
- **M2 (wiki)**: env-check removal + a legitimately stale coverage.json (partial `tier1_gaps`-only coverage run: admission 49.7 / restore 82.5 / policy 75.9) → mutated gate fails in-suite: `acquisition.py branch coverage 24.4% < 78% (frozen)` + `module not measured: adapters/sidecar.py`. Reverted → 2 skipped; clean. Matches the corrected receipt record (r1's independent `admission.py 94.0% < 95%` kill on the true base measurement stands as the cited evidence).
- **M3 (both repos)**: remove `fetch_filing.py` from the filing FROZEN_MAX table → `fetch_filing.py max 34 > 10` (new-files rule) — kill; remove `cli.py` from the wiki table → `new file cli.py has max complexity 140 > 10` — kill. Both reverted; ratchets re-green; clean. Matches the corrected receipt record (receipt text says "33>10"; actual is 34>10 post-assert — immaterial lag).

### c) Split still verbatim after guard removal ✓ (F3 FIXED)
- All 4 helpers VERBATIM: 86=86, 21=21, 53=53 (theme helper now = base 1094-1146 without the guard), 19=19.
- `if theme is not None:` guard exists only at the call site (base 1093); helper contains no duplicate.
- Whole-file multiset diff vs base: **empty** — zero extra lines; the split is now a pure move with no duplication.
- Focused tests: revenue 25 (23+2), filing 23, wiki 15 + gate 2 skipped.

### d) Receipt structure ✓
- `receipt_validator.py` → **OK: 1 receipt(s) valid** on the updated receipt.
- base_triplet.wiki = `2268970...` (true FC-1203 final HEAD) ✓ (F5 FIXED); changed-file lists match the r2 commits exactly (wiki pyproject.toml only; filing fetch_filing.py + ratchet test; revenue receipt + revenue_report.py + 3 test files).
- Corrected mutation records (M2 env-gate removal; M3 FROZEN-entry removal) are now TRUE and reproduce (see b).

### e) F6 + behavior evidence ✓ (F6 FIXED)
- Chain tests with dynamic `_AS_OF = today+7`: fc1002/fc1003/fc1004 → **10 passed**.
- Full revenue suite at r2: **515 passed / 1 failed** — the 1 = pre-existing `tools/tests/test_audit_baseline.py::test_collects_baseline_facts` (fails identically at base 9315ddf). All 5 r1 date-failures gone. This now matches the original brief's "513-ish passed / 1 failed" exactly.
- E2E golden at r2 (`repo_head=387e6ac5`): **result hash fedcd224acf28dee — IDENTICAL**, deterministic double-run. Guard removal is behavior-preserving.
- Filing full coverage at r2 (code changed by the assert): **312 passed / 6 skipped / 54 subtests; TOTAL 91.04%; contracts 97%; gate green EXIT=0** (0.01 drift from the added line; receipt's 91.03 is r1-era).

### f) NEW FINDING — ruff (blocking) → F7
- `python -m ruff check scripts tests tools e2e` (ruff 0.15.18, same as the CI pin; no ruff config exists in the revenue repo) at r2: **4 errors** — 3 **NEW E402** `Module level import not at top of file` at the `import datetime as _dt` lines added by 387e6ac in tests/test_fc1002_three_process_e2e.py:34, test_fc1003_uj.py:32, test_fc1004_platform.py:30 (the files' own convention is `# noqa: E402` on mid-module imports, or plain top-of-file placement), plus 1 **pre-existing** F401 (unused FROZEN_BASELINE import, tests/test_compatibility_manifest.py:26 — present at base 9315ddf, outside FC-1204's delta).
- The committed CI ruff step ("Ruff + compileall + unique test symbols (WU-1.2)") therefore fails — the FC-1204 WU card exit gate requires ruff green, and the F6 remediation commit itself added the 3 new violations. Fix is trivial: move the three datetime imports to the top of their files (stdlib import, does not depend on the sys.path block) or add the files' customary `# noqa: E402`. The pre-existing F401 must also be fixed (or explicitly waived) for the step to actually go green.

### Remaining info findings
- **F8 (info)**: The commit message claims "F4 doc baseline corrected" but the receipt's revenue mypy command note still reads "baseline 45 errors" (line 130); the measured baseline is 35.
- **F9 (info)**: The receipt's result_triplet still lists the pre-remediation commits (4750fec/93aa5ad/f03142c) rather than the actual fcap tips 387e6ac/83c638e/925b3e8. The reviewer receipt below uses the rev-parsed actual tips.
- **F10 (info)**: Filing TOTAL is now 91.04% (receipt says 91.03%) — one-line drift, gate unaffected.

## r2 Verdict

REJECTED with one blocking finding (F7: 3 new ruff E402s from the F6 fix — CI ruff step red on FC-1204's own new lines; plus the pre-existing F401 required for the step to go green) and three info findings. Everything else in r2 — mypy 0/0/0 on exact CI commands, corrected M2/M3 mutations replay-killed, cleaner verbatim split, honest receipt structure, dynamic-date chain tests (full suite 515/1), E2E golden identity, filing coverage gate — verifies exactly as claimed. Recommended final remediation: fix the 3 E402 imports + the F401, re-run `ruff check scripts tests tools e2e` to 0, and optionally touch up F8/F9 in the receipt. A final r3 review can be limited to the ruff step and the receipt touch-ups.

---

# FC-1204 r3 Re-Review (F7 + receipt touch-ups)

- **Reviewer**: reviewer-fc1204-independent (r3 replay, scoped per the r2 disposition)
- **r3 commits**: revenue `e40a52c` (F7: 3 datetime imports to top import block + pre-existing F401 removed from test_compatibility_manifest.py) and `91cbc13` (receipt seal — changes only result_triplet.revenue)
- **Date**: 2026-08-13T01:46Z
- **Decision**: **ACCEPTED** — the blocking F7 is cleared; residual receipt bookkeeping items remain as info findings.

## r3 verification (fresh worktree `.fcap-review/fc-1204/r3/revenue-forecast` @ 91cbc13; filing/wiki re-verified in the r2 worktrees at their unchanged fcap tips; F-6 honored)

### a) ruff — exact CI commands on all three repos → 0 ✓ (F7 FIXED)
- revenue (`ruff check scripts tests tools e2e`): **All checks passed!** — first fully-green revenue ruff (the pre-existing F401 removed in the same commit).
- filing (`ruff check scripts tests tools e2e`): **All checks passed!**
- wiki (`ruff check src tests/unit tests/contract scripts`): **All checks passed!**
- Diff review of e40a52c: the three `import datetime as _dt` lines moved into the top import block (E402 x3 gone); the unused `FROZEN_BASELINE` import removed. One cosmetic note: the fc1002 comment block is now duplicated (old F6 comment kept + new line added) — immaterial.

### b) Receipt — structural OK; F8/F9/F10 corrections only partially landed (info)
- `receipt_validator.py` → **OK: 1 receipt(s) valid**.
- F9: result_triplet.revenue → `e40a52c...` (the last code commit before the seal — consistent with the repo's r1-era convention of excluding the receipt-seal commit). **filing still `93aa5ad` and wiki still `f03142c`** — the actual fcap code tips are 83c638e / 925b3e8 (stale).
- F8: the receipt's revenue mypy note **still reads "baseline 45 errors"** (line 130); measured baseline is 35.
- F10: the filing coverage note **still reads "TOTAL 91.03%"** (measured 91.04%) and the M3 record **still reads "33>10"** (actual 34>10 post-assert).
- Net: 1 of the claimed receipt corrections landed (revenue triplet entry). The r3 message's "receipt 修正 F8/F9/F10" overstates the committed state.

### Regression safety of the r3 changes
- `git diff 387e6ac 91cbc13 -- scripts/` is **empty** — production code byte-identical to r2, so the r2 full-suite (515/1) and E2E golden (fedcd224acf28dee) evidence carries unchanged.
- All r3-changed test files re-run (with sibling junctions for the layout-dependent tests): fc1002 + fc1003 + fc1004 + test_compatibility_manifest → **29 passed** (an initial 11-failure run was the known sibling-layout artifact of the isolated worktree, eliminated by junctions; F-6 compliant).

## r3 Verdict

**ACCEPTED.** The only blocking finding (F7) is fixed and verified across all three repos (ruff 0/0/0 on the exact CI commands, revenue's first fully-green ruff). Receipt structure valid; behavior evidence (full suite, E2E golden, mypy, coverage, mutations) all carry from r1/r2 with production code byte-identical. Residual info findings, to be folded into the acceptance commit (FC-1203 F1 precedent): the implementer receipt still carries "45 errors" (F8), stale filing/wiki result_triplet entries 93aa5ad/f03142c (F9, actual 83c638e/925b3e8 — the reviewer receipt records the true tips), and stale "91.03%"/"33>10" texts (F10). None is blocking.
