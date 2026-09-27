# RF-RATCHET-REST-A · a20260923-01 — Independent reviewer report

- Card: **RF-RATCHET-REST-A** (3 checkpoint-introduced complexity-ratchet rows: `forecast/calc.py` 22→18 ≤21, `generate_input_template.py` 17→9 ≤9, `research/targets.py` 114→72 ≤88)
- Attempt: `a20260923-01` · attempt root = `.planning/2026-09-19-three-project-history-audit/execution_runs/RF-RATCHET-REST-A/a20260923-01`
- Reviewer: delegated independent reviewer (parent session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`), 2026-09-23
- Method/boundary: read / grep / pwsh operations, **no product writes** (RF `scripts|tools|tests` untouched by reviewer), scratch confined to `%TEMP%`, no network, no state-changing git (`log`/`status`/`diff --cached`/`show`/`rev-parse`/`hash-object`/`apply --check` — read-mode git, zero mutations), this file + `reviewer_report.sha256` are the reviewer's 2 written outputs
- Sign-off: **ACCEPT** — handoff stays `review_pending` / `signed:false` (reviewer does not self-sign; parent applies the signature on this ACCEPT)

---

## 1. Verdict

**ACCEPT (no blockers).** Every card rule I could test was re-derived independently, most of them re-executed on my own runs. 7 findings, all LOW/INFO documentation or EOL-label issues: **none of them changes the delivered bytes, the gate numbers, or the merge decision.**

| id | sev | one-liner |
|---|---|---|
| F-01 | LOW | "12/12 pre-existing failures corroborated by RF-STEP9-TRIAGE win_head evidence" is overstated: exact test-id search over the whole TRIAGE attempt finds **6 of the 12** ids; the other 6 appear nowhere in TRIAGE. Outcome unaffected (12 still pre-existing: same 14 ids fail in baseline, after, and my own re-run). |
| F-02 | LOW | Recorded pre-image shas `98f2b591a62d902…/e4593b146fd10aff…/f8b6f0737b120a78…` are **sha256 of `pre70dd/*.blob`**, not git object ids (`git cat-file -t` → "Not a valid object name"). Real pre-image blobs verified separately: `15a4d644…/49fb703f…/f8b88446…`, byte-identical to their `.blob` files. |
| F-03 | LOW | `binding.json sources_after_sha256["scripts/research/targets.py"]=E7E8ED6B…` is a **CRLF-byte** hash of their copy; applying `changes.diff` under RF's `.gitattributes` yields the **LF** form `5BE517C9E7196AC1…`. Content identical after EOL normalization (verified); `calc`/`template` after-shas reproduce byte-exactly. |
| F-04 | INFO | `handoff.changes_diff.diff_bytes = 43880` is the **character** count; the file is **43882 bytes** (one U+2014 em dash, 3 bytes). |
| F-05 | INFO | `evidence/README.md` cites 3 filenames that do not exist (`mutation_scripts_forecast_calc.py.txt` etc.); actual names are `mutation_forecast_calc.py.txt` / `mutation_generate_input_template.py.txt` / `mutation_research_targets.py.txt`. The other 25 referenced paths resolve. |
| F-06 | INFO | `decision.md` says the attempt dir holds "the 12 intended artifacts"; attempt root actually holds **13 files** (7 step artifacts + 6 tooling scripts) + the 4 dirs it does name. |
| F-07 | INFO | Card text says calc helper `_recognition_parameter_ids`(5); ratchet-semantics cc measured by me = **6** (= 1 + the 5 branch points the card counts). `decision.md`/`handoff.json` say 6 — their docs are right, the card paraphrase is loose. |

---

## 2. Verification detail (reviewer's own measurements)

### V1 — Deliverables / ORACLE / diff (PASS)

- All 8 step artifacts present at attempt root: `ORACLE.md` (7806 B, 21:08:25), `binding.json`, `commands.md`, `decision.md`, `changes.diff`, `handoff.json`, `recovery.md`, `evidence/README.md` (index covers 28 evidence files + 5 run dirs).
- **Frozen-first timeline** (mtimes): `scan_red.*` 20:53:25 → `family_inventory.*` 21:03:37 → `family_shas_before.txt` 21:06:51 → `ORACLE.md` 21:08:25 → **first edit** `refactored/forecast/calc.py` 21:12:28. Oracle + baseline pins predate any edit ✓.
- `changes.diff`: **exactly 3 files** (3 `--- a/` + 3 `+++ b/`: `scripts/forecast/calc.py`, `scripts/generate_input_template.py`, `scripts/research/targets.py`), 1038 lines, LF-only, difflib-style headers (no `diff --git`), 43882 B.
- **Reviewer's own `git apply --check` in `%TEMP%`** against fresh copies of the 3 live production files: `Checking patch …×3`, **rc = 0** ✓ (run twice, incl. `--verbose`).
- Applying the patch under RF-equivalent EOL rules (`.gitattributes` `*.py text eol=lf`, `core.autocrlf=true`) reproduces `calc` = `605BE6E8…` and `template` = `06591BE0…` **byte-exactly**; `targets` lands as LF `5BE517C9…` vs their pinned CRLF `E7E8ED6B…` → F-03 (content equal after normalization, verified both directions).
- `handoff.json`: `status = review_pending`, `signed = false`, `unmapped_hunks = []`, `unproven_claims = []` ✓.
- `evidence/README.md` spot-index: 25/28 referenced names resolve → F-05.

### V2 — CC numbers re-measured (PASS)

Instrument: the ratchet test's own `_max_complexity` **imported live from RF** `tools/tests/test_complexity_ratchet.py` (sha `EB1A36CF…`) **plus a reviewer-written independent twin** (ast.walk / same branch semantics), run over both their `refactored/` copies and the live tree. Agreement **43/43 files, 0 disagreements** (both scans).

| file | production (live) | refactored (delivered) | frozen | verdict | driver table (top-level, ratchet semantics) |
|---|---|---|---|---|---|
| `forecast/calc.py` | **22** | **18** | 21 | PASS | `base_segment_parameter_ids` 18 (new file max), `_evaluate_formula_node` 17, `collect_parameter_roles` **17** (was 22), `_recognition_parameter_ids` **6**, `base_forecast_parameter_ids` 12 |
| `generate_input_template.py` | **17** | **9** | 9 | PASS | `build_template` **9** (was 17), `main` 8 (untouched), `_build_segments` **6**, `_build_historical` 2, `_build_research_coverage` 2, `_build_management_coverage` 2 |
| `research/targets.py` | **114** | **72** | 88 | PASS | `_validate_management_target` **72**, `_normalize_communication_coverage` **35**, `validate_management_target_coverage` (orchestrator) **9**, `add_management_target_analysis` 12 (untouched) |

- The 12 function-level numbers those two artifacts state for these three files match my independent measurement (F-07 concerns the card's paraphrase, not `decision.md`/`handoff.json`).
- Delivered-byte shas re-hashed by me = binding's `sources_after_sha256` (`605BE6E8…`, `06591BE0…`, `E7E8ED6B…`) ✓.
- **Frozen-table sha before==after**: live `tools/tests/test_complexity_ratchet.py` = `EB1A36CFD54A8B96E3B5DCA6CA4B7A89CA6B1E1605D22EEDB69F643245EDD10A` = their `sha_reverify_final.txt` = the sha inside their `scan_green_iso.json` = the sha in my iso copy. Four-way equality, no cap changed ✓.
- **Sibling rows untouched**: the 5 sibling files (`analysis/confidence.py`, `model_extensions.py`, `model_registry.py`, `revenue_core.py`, `revenue_publication.py`) are byte-identical to live production in **all 5 of their trees** I hashed (their `%TEMP%` iso2 + `scratch/green` + all 3 `scratch/mut_*`) — **25/25 hash checks match**. Only the ratchet *table* was re-pinned in scratch, and only for sibling rows (see V6).
- **Violations 8 → 5 (iso-state) / REST-A's 3 rows PASS**:
  - Live production scan (mine, both impls): **8 failing rows**, identical set+numbers to their `scan_red.json` — `confidence 32>23`, `calc 22>21`, `template 17>9`, `model_registry 28>9`, `targets 114>88`, `revenue_core 23>6`, `revenue_publication 16>10`, `model_extensions 27>10[new]`.
  - Final-byte iso scan (mine, both impls, fresh copy of their iso): **5 failing rows**, all sibling-owned (`confidence 32`, `registry 28`, `core 23`, `publication 16`, `extensions 27`), `MY 3 ROWS failing = 0` ✓ → the 8→5 claim reproduces.
  - Caveat for the parent: **the live repo still shows 8** because no diff has been applied yet; 5 is the iso-state number, and 0 arrives with the merge batch (§5).

### V3 — Families (PASS, independently re-run)

- **Main-family identity (55 tests, 16-module upward closure)**: `evidence/family_shas_before.txt` and `family_shas_after.txt` are **byte-identical** (55 lines each, both sha256 `365B5094…`), and **each of the 55 recorded per-file sha256s matches the live RF test file** (0 mismatches in 55). The aggregate `947AB2EC03BA8082514413E5314F1F5DAF9FB8B6133F3C197B615B7218715387` in `binding.json` (before == after) reproduces exactly under the formula sha256 over the lines `"<SHA256>  <path>"` joined with `"\n"` (no trailing newline) — the formula is not documented by them (I reverse-engineered it; suggest documenting). *Note: no artifact in this attempt records a "56" count — inventory/report say 55 throughout, so the 56→55 correction narrative is not evidenced inside the attempt itself.*
- **Supplement family (6 files in `supplement_family.json`)**: raws show `4 failed / 42 passed / 3 skipped` on **both** sides (`supp_before`, `supp_after`), `compare_supp_before_after.json` = `all_outcome_changes {}`, `regressions []` ✓.
- **after(final)**: their `family_after` raw = `14 failed / 554 passed / 3 skipped / 130 subtests`; `compare_before_after.json` = `all_outcome_changes {}`, `regressions_green_to_notgreen []`, `only_before/only_after []` ✓; failure-id list in before == after == 14 ids (12 pre-existing + 2 ratchet-body reds) ✓.
- **Reviewer's own re-run** (fresh `%TEMP%` copy of the final-byte iso, the 55 files from `family_files.txt`, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`):
  - family: **`14 failed, 554 passed, 3 skipped, 130 subtests passed`** (360.6 s) → compared with their baseline junit: `all_outcome_changes {}` / `regressions []` / `only_* []`, rc 0; compared with their after junit: `{}` / `[]` ✓.
  - supplement (6 files): **`4 failed, 42 passed, 3 skipped`** (82.6 s) → compared with their `supp_before`: `{}` / `[]` ✓.
- **12 pre-existing failures**: same-name check I did — the 14 failing ids are identical in their before, their after, and my re-run; 2 of the 14 are the ratchet body itself. Corroboration by TRIAGE: **6/12 → F-01** (I spot-read both raws for 2 names as instructed: `win_head_tests_test_attestation_py.out` shows `test_configured_provider_means_host_signed_publication` FAIL at `rf_sha=b0d016a6…`; `win_head_tests_adversarial_test_receipt_attacks_py.out` shows `test_context_fabrication_is_rejected_by_final_validation` FAIL at the same rf_sha; `git diff --stat b0d016a6..HEAD -- scripts tests tools` = 2 unrelated test files (`tests/test_cross_repo_chain_e2e.py`, `tests/contract/host_assumption_allowlist.json`), neither in the 55-test family, so those two corroborations still bind to HEAD).
- **The 2 ratchet-body reds = sibling rows (KEEP-RED)**: I ran the ratchet test itself on live production (`python -B`, read-only) → first `AssertionError` = `analysis/confidence.py max 32 > 23`, second = `model_extensions.py max 27 > 10` (my 3 rows never reached at abort); in the final-byte iso the same two abort first. Expected posture: overall gate stays RED for sibling rows until the merge batch; the supplement wrapper `test_ca303::test_c3_complexity_ratchet_green` carries the same RED on both sides.

### V4 — Type gate honesty (PASS)

- Incident is recorded in `decision.md` §"Type gate (mypy, C4) incident": helper annotated `dict[str, Any]` widened `target.get(...)` to `Any|None` and invented 8 errors → C4 red → reverted to `target: Any`; net −2 on the 3 owned files (5 → 3).
- **Reviewer's own targeted replication** (`mypy --no-error-summary --ignore-missing-imports --follow-imports=skip`, cache in `%TEMP%`, production bytes vs refactored copies): **originals 5 errors → refactored 3 errors**; the 2 dropped ones are the coverage-shape errors of the original (`len`/`enumerate` at old L44/L49), the 3 kept are pre-existing in untouched blocks (calc `set.add`, targets `enumerate`, targets `union-attr`). **No new error introduced** ✓.
- **Final full-gate count on final bytes**: their `evidence/mypy_full_after.txt` contains **67** `: error:` lines (≤ MYPY_BASELINE 69) ✓; **my own full re-run** `mypy scripts --no-error-summary --ignore-missing-imports` in the final-byte iso = **67** ✓ (fresh cache, no reliance on theirs).
- No lingering type-intrusion: `refactored/research/targets.py:182` reads `target: Any` with the explanatory comment at L179-181 (the `dict[str, Any]` form is gone) ✓.
- **Family re-run happened on FINAL bytes** — mtimes: last edit `refactored/research/targets.py` **22:36:11** → `changes.diff` 22:37:28 → `probe_new.json` 22:38:20 → `mypy_full_after.txt` 22:38:43 → `scan_green_iso.*` 22:39:06 → `mutation_*` 22:39:12-27 → `family_after/junit.xml` **22:43:39** → `supp_after/junit.xml` **22:44:12** → `sha_reverify_final.txt` 22:44:43 → `handoff.json` 22:47:58 ✓ (the earlier `family_after`/`supp_after` dir creation at 22:11 is the superseded pre-fix run, consistent with the incident narrative).

### V5 — Strategy proof: tested-not-shipped revert (PASS with F-02)

- `evidence/compare_before_vs_pre70dd.json`: before `14F/554P/3S`, pre-70dd `20F/548P/3S`, **8 green→red regressions** (template ×2, independent_targets ×3, industry_e2e, models ×2), **2** improvements (the zr601 pair), junit totals 571/571 both sides; console raws: `14/554/…/130 subtests` → `50/551/…/97 subtests` = **−33 passing subtests ≡ 33 failing subtests (vs 0 at baseline)** ✓ — reads as "tests distinguish ⇒ forced refactor" under the card rule (revert allowed only if distinguish fails → it did not fail).
- `git log 70dd9f6e..HEAD -- <the 3 files>` is **empty** → live content == checkpoint content (the pre-70dd images really are the pre-images) ✓.
- Pre-image authenticity: `git rev-parse 70dd9f6e^:<path>` = `15a4d644d824cb970e1019751f38b250699b9657` (calc) / `49fb703fae152e0004bd568e71a9b3c29c0a3022` (template) / `f8b8844694aad160c728a5982ad884de4812c1a9` (targets), each `type=blob`; `git hash-object pre70dd/*.blob` returns **the same three ids** → their `.blob` files are the exact git pre-image bytes ✓; `commands.md` #10 documents that those `.blob` files were the bytes swapped into the iso ✓. The three *recorded* shas are sha256 digests, not blob ids → F-02. (Side note: `pre70dd/*.py` are LF-normalized duplicates, 387/309/546 B smaller than their `.blob` twins; per `commands.md` #10 the `.blob` twins are what the iso swap used.)

### V6 — Mutation non-vacuity (PASS; row 1 replicated by me)

- `green_unittest.txt`: scratch ratchet (sibling rows re-pinned only) → **both tests `ok`, `Ran 2 tests … OK`, rc 0** ✓.
- Scratch-table honesty, diffed by me against the production table: `mut_forecast_calc` = `analysis/confidence 23→32` + `NEW_FILE_MAX 10→30`; `mut_research_targets` = confidence + `model_registry 9→28` + `NEW_FILE_MAX`; `green` = confidence + `model_registry` + `revenue_core 6→23` + `revenue_publication 10→16` + `NEW_FILE_MAX 10→30`. **My caps 21/9/88 are byte-identical in each of the 5 scratch tables** ✓; no table edit is in `changes.diff` ✓.
- Per-row raws carry exactly the predicted messages: `22 not less than or equal to 21 : forecast/calc.py max 22 > 21`, `17 not less than or equal to 9 : generate_input_template.py max 17 > 9`, `114 not less than or equal to 88 : research/targets.py max 114 > 88` (rc 1 each, `test_new_files_stay_simple` ok in each) ✓.
- **Reviewer's own replication of row 1**: copied `scratch/mut_forecast_calc` to `%TEMP%`, verified `scripts/forecast/calc.py` == production original (`BC4F33D9…`), the other two == refactored (`06591BE0…`/`E7E8ED6B…`), table diff = confidence + NEW_FILE_MAX as its sole delta, then ran the test → **rc 1, first `AssertionError: 22 not less than or equal to 21 : forecast/calc.py max 22 > 21`** — matches both my live measurement of the production original (22) and their claim ✓. Rows 2/3: raws + tree classification (each `mut_*` swaps exactly one file back to production original — 9/9 hash checks) accepted without re-execution.
- **Differential probes**: reviewer re-ran `diff_probe.py` **twice myself** — ORIG against live production `scripts/`, NEW against the final-byte iso: **my ORIG == my NEW (25 probes), and both equal their stored `probe_orig.json` / `probe_new.json`** (diff key list empty) ✓. The `sorted()` fix is disclosed in `decision.md`/`handoff.json` and present in `diff_probe.py:402-404` with the rationale comment (`MANAGEMENT_COMMUNICATION_STATUSES` is a `set` → `list()` order is hash-randomized) ✓; both their `probe_*.err` files are 0 B.

### V7 — AUDIT-INTEGRITY tmp flag (CLEARED)

- Reviewer's own recursive `-Force` rescan of the attempt root: **0** files matching `*.tmp` / `.decision*` / `*.tmpdir*`, **0** `__pycache__` or `*.tmpdir*` directories ✓.
- Attempt root = 13 files + 4 dirs (`evidence`, `pre70dd`, `refactored`, `scratch`) ✓ (the "12" count is F-06).
- `decision.md` records「tmp 残留已清（AUDIT-INTEGRITY 旗）：重扫无残留，`__pycache__` 已删」 ✓.

### V8 — Boundary at close (PASS)

- **Production 3 before-shas re-verified live, twice** (direct `Get-FileHash` and the copies fed to `git apply --check`): `BC4F33D92738029A…`, `F7C57911D5F85204…`, `1C885DEAF4168BAC…` → prefixes **BC4F33 / F7C579 / 1C885D** ✓, i.e. production sources were never written.
- Frozen table live = `EB1A36CF…` ✓ (no cap change shipped).
- `changes.diff` contains **no skip/xfail markers** (one hit for the word "baseline" = line 352 comment "…against the frozen type baseline", a mypy note, not a gate bypass) ✓.
- **Zero git writes by this attempt**: reflog's newest entry is the pre-attempt commit `b7a6a116` at 19:51 (attempt started 20:53); `git diff --cached --name-only` is empty (nothing staged); `git status --porcelain -- scripts tools tests` = **0 entries** ✓.
- **RF product surface clean at snapshot**: only 2 non-`.planning` porcelain entries repo-wide (`.tmp-r41-mutation/`, `assurance/unified_completion/manifests/plan_inputs.json.bak`), both created 09-20/09-21 → pre-date this attempt, excluded by attribution; the `.planning` churn (97 → 112 entries during my review) is sibling/parent bookkeeping ✓.
- Reviewer's own footprint: writes confined to `%TEMP%` and these two report files; python invocations inside RF used `-B` / `PYTHONDONTWRITEBYTECODE=1` (`tools/**/__pycache__` mtimes are 09-21/09-22/08:20, i.e. pre-date this review); `git status` refreshed the `.git/index` stat-cache alone (mtime, no content/state change) — disclosed here.

---

## 3. Unverified / not re-executed by me

1. **The pre-70dd revert family run itself** (50F/551P, 5:19) was read and cross-checked from stored raws + compare + git-object authenticity, **not re-executed** (would require re-swapping pre-images and another ~6 min run; the raws are internally consistent: 571 testcases both sides, 8 regressions, −33 passing subtests).
2. **Mutation rows 2 and 3** were verified from their raws + tree/table classification, not re-executed; row 1 alone was replicated end-to-end by me.
3. **TRIAGE corroboration for 6 of the 12 ids** (fc505, zr1103 ×2, zr803, zr804, zr1102::test_c1_no_orphaned) — no such raws exist anywhere in `RF-STEP9-TRIAGE` (F-01); the "pre-existing" property itself rests on their baseline run and my identical re-run, which I did verify.
4. **Sibling card diffs** (`RF-RATCHET-REST-B`, `RF-RATCHET-FIX-2`, `RF-STEP9-TRIAGE`) — content not reviewed (out of scope); I only counted their files and read their handoff statuses (§5).
5. **Non-`.py` fixtures in the iso**: I re-hashed each `.py` under `tests|tools|scripts` in their final-byte iso against RF (202 compared, exactly the 3 shipped files differ); JSON/YAML/other fixtures were not individually re-hashed.
6. **The family aggregate-sha formula** is not documented by them; I reproduced `947AB2EC…` with the formula in §V3 but cannot prove it is the formula they used (it matches, and before/after files are byte-identical anyway).
7. Probe coverage = their 25 probes (re-executed twice by me); behavior equivalence beyond probe+family+supplement scope is accepted as the card's method, not proven exhaustively.

---

## 4. F-01 evidence detail (the one substantive bookkeeping issue)

`handoff.json` claims: `"all_preexisting_corroboration": "12/12 main non-ratchet failures reproduced identically at HEAD by sibling RF-STEP9-TRIAGE win_head_* evidence"`, and `decision.md` lists the 12 ids under "independently reproduced by sibling RF-STEP9-TRIAGE win_head_* evidence".

Exact test-id search over **each file** in `execution_runs/RF-STEP9-TRIAGE` (recursive, docs included; broader than `win_head_*`) finds **6 of 12**:

| in TRIAGE | test id |
|---|---|
| yes | `test_attestation::test_configured_provider_means_host_signed_publication` |
| yes | `test_receipt_attacks::test_context_fabrication_is_rejected_by_final_validation` |
| yes | `test_zr1102::test_c4_mutation_patrol_capabilities` |
| yes | `test_zr601::test_c1_negative_asset_drivers_rejected` |
| yes | `test_zr601::test_c1_recovery_rate_out_of_range_rejected` |
| yes | `test_zr708::test_c2_accuracy_record_consumed_by_confidence` |
| **no** | `test_zr1102::test_c1_no_orphaned_script_without_main` |
| **no** | `test_dropbox_full_chain_fc505::test_fc505_chain_exact_hit_zero_side_effects` |
| **no** | `test_zr1103::test_c2_processed_reuse_single_flight` |
| **no** | `test_zr1103::test_c3_three_markets_covered_in_t3_suite` |
| **no** | `test_zr803::test_lock_held_write_transaction_does_not_block_read_journey` |
| **no** | `test_zr804::test_case_swapped_project_dir_runs_identical_journey` |

Recommended correction on landing: change 12/12 → **6/12 corroborated by TRIAGE raws; 12/12 shown pre-existing by the REST-A baseline run (iso of production bytes) and by the reviewer's identical re-run**. The ACCEPT is unaffected: zero outcome changes between before and after is proven by three independent junit comparisons (theirs before-vs-after, mine vs their before, mine vs their after), each with `all_outcome_changes {}` / `regressions []`.

---

## 5. Scope if ACCEPTING (merge batch)

- **This card ships exactly 3 files**: `scripts/forecast/calc.py`, `scripts/generate_input_template.py`, `scripts/research/targets.py` (`changes.diff`, 43882 B, `git apply --check` rc 0 by reviewer).
- **Sibling deliveries observed at my snapshot** (file counts read from their `changes.diff`, statuses from their `handoff.json`):
  - `RF-RATCHET-FIX-2/a20260923-01` — **2 files** (`scripts/analysis/confidence.py`, `scripts/model_extensions.py`), `status=accepted_scoped`, `signed=false`, `reviewer_report.md.sha256` 23:13 + `review.md` 23:36 present.
  - `RF-RATCHET-REST-B/a20260923-01` — **3 files** (`scripts/model_registry.py`, `scripts/revenue_core.py`, `scripts/revenue_publication.py`), `status=review_pending` (its own `reviewer_report.md` written 23:37), i.e. **not yet accepted at my snapshot**.
  - `RF-STEP9-TRIAGE/a20260923-01` — **8 files** (6 tests + `tools/daily_t2_runner.py` + `tools/mutation_patrol.py`; diff mtime 23:46), `status=accepted_scoped` → **card's "TRIAGE's7" is stale at my snapshot; plan for 8.**
  - (`RF-RATCHET-FIX` has no `changes.diff` — superseded by FIX-2.)
- **One apply + commit + push batch** therefore = 3 + 2 + 3 = **8 `scripts/` files = exactly the 8 ratchet rows → 8/8 rows green**, plus TRIAGE's 8 files for the step9 intrinsic fixes (16 files total at my snapshot vs the card's 12-file framing).
- **Ratchet residual after merge = 0 rows**, conditional on all four reviews ACCEPT — **REST-B is still `review_pending`, so the residual is 3 rows (28/9, 23/6, 16/10) if REST-B's review rejects**; FIX-2 and TRIAGE are already `accepted_scoped`; REST-A is this report (ACCEPT).
- **KEEP-RED row-pass posture transcribed**: today's overall gate RED is caused only by sibling rows (`analysis/confidence 32>23`, `model_extensions 27>10` = FIX-2; `model_registry 28>9`, `revenue_core 23>6`, `revenue_publication 16>10` = REST-B). REST-A's 3 rows are green **under the test's own code** (per-row proof: full-row scan in the final-byte iso = 0 of my rows failing, scratch-pinned green case rc 0, my own mutation replication naming each file/message). The 2 ratchet-body reds are expected KEEP-RED until the batch lands; live repo scan (reviewer's, 43 files × 2 impls) still reports **8** because nothing is applied yet — "8 → 5" is an iso-state claim, verified; "8 → 0" happens at the batch.

---

## 6. Reviewer's own runs (audit trail)

Runs below executed under `%TEMP%` (nothing written into RF):

| run | result |
|---|---|
| `rev_scan.py` (ratchet `_max_complexity` imported live + reviewer twin) | production 8 rows failing; refactored 18/9/72 PASS; 43 files, 0 disagreements |
| iso scan (final-byte copy) | 5 rows failing, all sibling; `MY3 failing = 0`; frozen sha `EB1A36CF…` |
| `git apply --check` (fresh `%TEMP%` copies of live production) | rc 0, 3 patches |
| `git apply` under RF `.gitattributes` (sim repo in `%TEMP%`) | calc/template byte-equal to delivered; targets LF-normalized equal (F-03) |
| family (55 files, final-byte iso) | `14F/554P/3S/130 subtests`, 360.6 s → vs their before: `{}`/`[]`; vs their after: `{}`/`[]` |
| supplement (6 files) | `4F/42P/3S`, 82.6 s → vs their before: `{}`/`[]` |
| `mypy scripts --no-error-summary --ignore-missing-imports` (fresh cache) | **67** errors ≤ 69 |
| targeted mypy (`--follow-imports=skip`) | originals **5** → refactored **3**, no new error |
| ratchet test on live production (`python -B`) | first failure `analysis/confidence 32>23`, then `model_extensions 27>10` (KEEP-RED at sibling rows) |
| `diff_probe.py` ORIG (production) vs NEW (iso) | 25/25 identical; both equal their stored probe raws |
| mutation row 1 replication | rc 1, `AssertionError: 22 not less than or equal to 21 : forecast/calc.py max 22 > 21` |
| tmp/`__pycache__` rescan of attempt root | 0 / 0 |
| product-surface `git status --porcelain -- scripts tools tests` | 0 entries |

## 7. REM-79 self-check

`python <REM79-MECHANIZATION attempt>/tools/check_domain_assertions.py reviewer_report.md` → **exit 0** (no universal-quantifier claim without its domain; run with `PYTHONIOENCODING=utf-8`).
