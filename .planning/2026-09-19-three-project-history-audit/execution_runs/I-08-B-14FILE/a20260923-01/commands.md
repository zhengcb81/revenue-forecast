# COMMANDS — I-08-B-14FILE / a20260923-01

All commands run from pwsh (fresh process per call). `RF = C:\Users\郑曾波\Projects\revenue-forecast` (READ-ONLY),
`ATT = <PLAN>\execution_runs\I-08-B-14FILE\a20260923-01`, `TMP = %TEMP%\i08b14file\a20260923-01`.
No `git` command of any kind was executed. No network. Every pytest used
`PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 --basetemp` under `TMP`.

## A. Investigation (read-only)

| # | command (essence) | rc | purpose / result |
|---|---|---|---|
| A1 | `Get-ChildItem` plan/`execution_runs` listings; `read` of I-08-B handoff/oracle/decision/binding.json, I-08-A decision §7.1, B1 decision, TRIAGE decision/oracle/handoff | 0 | freeze authorization: 14-file list + carrier pins + finding #2 + H1/H2 |
| A2 | SHA256 of the 14 product paths in RF | 0 | before-shas (9 exist, 5 absent) |
| A3 | SHA256 of the 14 in carrier `iso/rf` + compare vs `binding.json.post_run_measurements` | 0 | 14/14 after-shas match carrier |
| A4 | `difflib` baseline_tree vs RF vs iso for the 9 edited files | 0 | drift = only revenue_core (327 ln) + revenue_publication (314 ln), content = B1 ec307d20 |
| A5 | grep `attestation_last_failure\|PublicationReceiptOnlyWarning\|SIGNED_RESULT_SHA256_SENTINEL` / `publication_attestation` in RF `*.py` | 0 | B1-only APIs consumed ONLY by the 2 files themselves; no product test/tool imports them |
| A6 | read RF `tests/test_attestation.py`, `tests/adversarial/test_receipt_attacks.py`, `tests/conftest.py`, carrier iso `test_attestation.py`, iso `revenue_publication.py` | 0 | false-green node, E27 face (validator-level in carrier), conftest isolation |

## B. Scratch construction

| # | command | rc | result |
|---|---|---|---|
| B1 | `robocopy RF TMP\before_tree /E /XD .git .planning <caches> /XF NUL` | 1 | copy ok (rc1 = files copied) |
| B2 | purge `__pycache__` from before_tree; re-encode 3 evidence files UTF-16→UTF-8 | 0 | stale-pyc incident closed |
| B3 | `robocopy before_tree after_tree /E /XD __pycache__ .pytest_cache` + `Copy-Item` 13 carrier files | 1/0 | 13/14 applied, each sha printed = carrier pin |
| B4 | `Copy-Item` carrier `tests/golden_behavior_hashes.json` → after_tree (14th) | 0 | `c6b13ada…` |
| B5 | `robocopy after_tree → mut_test, mut_prod, mut_guard, mut_golden, compat_tree` (5 trees) + restore exact before-bytes into each mutation path | 1/0 | all 5 mutation shas printed = live-RF before-shas |

## C. Red / Green / Mutation (frozen in oracle §4)

| # | cmd id | cwd | command | rc | raw evidence |
|---|---|---|---|---|---|
| C0 | first attempt (RETRACTED) | before_tree | `pytest tests/test_attestation.py --basetemp=…\b` | 1 | basetemp parent missing → all-setup errors; superseded by C1 |
| C1 | **R1 RED F1** | before_tree | `pytest tests/test_attestation.py` | 1 | `evidence/r1_red_F1_attestation_before.txt` — 1 failed / 6 passed, node = false-green, `False is not true` |
| C2 | **R4 RED F2** | before_tree | `pytest tests/test_single_owner_guard.py` | 1 | `evidence/r4_red_F2_guard_before.txt` — 1 failed / 2 passed |
| C3 | R0 sanity | before_tree | `pytest tests/test_golden_behavior_lock.py` | 0 | `evidence/r0_sanity_golden_before.txt` — 1 passed |
| C4 | **R7 RED F3** | after (13 files) | `pytest tests/test_golden_behavior_lock.py` | 1 | `evidence/r7_red_F3_golden_13files.txt` — volume output hash changed |
| C5 | R8 GREEN F3 | after (14 files) | `pytest tests/test_golden_behavior_lock.py` | 0 | `evidence/r8_green_F3_golden_14files.txt` — 1 passed 21.40 s |
| C6 | **R2 GREEN F1** (bg job pwsh-203) | after | `pytest tests/test_attestation.py tests/test_attestation_provider_protocol.py tests/test_attestation_legacy.py tests/test_publication_attestation_contract.py` | 0 | `evidence/r2_green_F1_attestation_after.txt` — 118 passed, 34 subtests, 0 failed |
| C7 | **R5 GREEN F2** (bg job pwsh-203) | after | `pytest tests/test_single_owner_guard.py` | 0 | `evidence/r5_green_F2_guard_after.txt` — 5 passed |
| C8 | **R3 MUTATION F1a** | mut_test | `pytest tests/test_attestation.py` | 1 | `evidence/r3_mut_test_original_test.txt` — 4 failed / 3 passed (false-green node red) |
| C9 | **R3b MUTATION F1b** | mut_prod | `pytest tests/test_attestation.py` | 1 | `evidence/r3b_mut_prod_before_product.txt` — 9 failed / 9 passed |
| C10 | **R6 MUTATION F2** | mut_guard | `pytest tests/test_single_owner_guard.py` | 1 | `evidence/r6_mut_guard_original.txt` — 1 failed / 2 passed |
| C11 | **R9 MUTATION F3** | mut_golden | `pytest tests/test_golden_behavior_lock.py` | 1 | `evidence/r9_mut_golden_original.txt` — 1 failed |
| C12 | **R11 census before** (bg pwsh-208) | before_tree | `pytest <15 curated files>` | 1 | `evidence/r11_census_before.txt` — 8 failed / 122 passed |
| C13 | **R11 census after** (bg pwsh-208) | after_tree | same 15 files | 1 | `evidence/r11_census_after.txt` — 4 failed / 139 passed |
| C14 | **R10 compat** | compat_tree | `pytest receipt_attacks zr1102 zr601 zr708 single_owner_guard` | 1 | `evidence/r10_compat_after14_plus_triage7.txt` — 33 passed / 1 failed (pre-existing c1) |
| C15 | **R10b** (current TRIAGE patrol) | compat_tree | `pytest tests/test_zr1102_adversarial_audit.py` | 1 | `evidence/r10b_compat_zr1102_current_triage.txt` — 8 passed / 1 failed (same c1) |
| C16 | **R12 ratchet** | before / after | `pytest tests/test_ca303_arch_quality.py::test_c3_complexity_ratchet_green` | 1 / 1 | `evidence/r12_ratchet_c3_before.txt` / `_after.txt` — red both arms → merge-batch step 2 |

Curated census set (oracle §4 R11, verbatim): test_attestation, test_single_owner_guard,
test_golden_behavior_lock, adversarial/test_receipt_attacks, adversarial/test_anchor_attacks,
test_publication_pipeline, test_publication_registry, test_recognition_bridge, test_output_report,
test_zr1008_new_chain_cutover, test_zr710_publication_txn, test_backtest, test_zr1102_adversarial_audit,
test_zr601_asset_facts, test_zr708_backtest_reverify.

## D. Diff / compat tooling (own scripts, no git)

| # | command | rc | evidence |
|---|---|---|---|
| D1 | `python scratch/gen_diff.py before_tree after_tree changes.diff expected_14.txt` | 0 | `evidence/c1_gen_diff.txt` — 14 files, extras=[], sha 9721711a… |
| D2 | `python scratch/apply_diff.py verify changes.diff before_tree after_tree` (1st) | 1 | `evidence/c2_changes_diff_roundtrip.txt` — CONTEXT MISS (universal-newline bug in verifier) |
| D3 | same after `newline=""` fix | 0 | 14/14 roundtrip_equal=true |
| D4 | `apply_diff.py apply TRIAGE.diff compat_tree expected_14.txt` (forbid list) | 3 | `evidence/c3_triage_apply_compat.txt` — stopped at guard overlap **after** applying sections 1–3 (partial-write incident, disclosed) |
| D5 | extract TRIAGE sections minus guard → apply | 1 | `evidence/c3b…`/`c3e…` — CONTEXT MISS on receipt_attacks = discovered it was already patched by D4 |
| D6 | guard-only section, forbid armed | 3 | `evidence/c3d…` (via c3c) — path-level overlap with my 14 detected |
| D7 | guard-only section, forbid disabled | 1 | `evidence/c3d_triage_guard_context_miss.txt` — CONTEXT MISS @@ -37 = textual conflict vs carrier guard |
| D8 | extract + apply remaining 4 sections (zr601, zr708, daily_t2, mutation_patrol) | 0 | `evidence/c3f_triage_apply_remaining4.txt` — 4/4 applied |
| D9 | section-equality check current TRIAGE diff vs sections used | 0 | session log table — guard+patrol volatile, other 6 identical |
| D10 | apply CURRENT patrol section to compat | 1 | `evidence/c3g_patrol_refresh_current.txt` — CONTEXT MISS = already at that post-state (idempotent), then C15 green |
| D11 | apply CURRENT guard section to compat | 1 | `evidence/c3h_triage_guard_current_conflict.txt` — still CONTEXT MISS (conflict confirmed on latest version) |
| D12 | `gen_diff.py` re-run after all runs | 0 | `evidence/c5_gen_diff_rerun.txt` — sha byte-identical (after-state stable) |
| D13 | SHA256 of the 14 live RF paths + `.pytest_cache` mtime + TRIAGE diff pin | 0 | `evidence/c4_rf_close_hashes.txt` — RF unchanged, 5 added absent, no RF run |
