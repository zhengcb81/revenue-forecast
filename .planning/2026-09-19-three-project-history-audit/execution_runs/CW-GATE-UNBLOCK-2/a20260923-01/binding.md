# BINDING — CW-GATE-UNBLOCK-2 / a20260923-01 (LIVING DOC — updated as measurements land)

Status legend: ✅ measured+pinned · 🔄 in progress · ⏳ pending.

## 0. Attempt identity

| item | value |
|---|---|
| card | CW-GATE-UNBLOCK-2 (successor of CW-GATE-UNBLOCK/a20260923-01) |
| attempt | `execution_runs\CW-GATE-UNBLOCK-2\a20260923-01` |
| predecessor attempt (READ-ONLY) | `execution_runs\CW-GATE-UNBLOCK\a20260923-01` |
| predecessor oracle sha256 | `017C41BD58D071667F6FFA817441A14D13E59761332D373563A4B68D2CB05C39` |

## 1. Repo pins (read-only git; no mutations) ✅

| item | value |
|---|---|
| CW root | `C:\Users\郑曾波\Projects\company-wiki` |
| HEAD (fcap) | `bf0c8b27e83c3ee7e533c6031fefad8e27e5e121` (bf0c8b2) |
| origin/master | `f39bd5a64224cd0c7aa098f23f64bf3811fa8939` (f39bd5a) |
| ahead/behind | 3/0 — fcap ahead (ac4ebd0, 5d72529, bf0c8b2) |
| dirty worktree (pre-existing, NOT mine, NOT in changes.diff) | ` M CLAUDE.md`, ` M README.md`, ` M src/company_wiki/source_catalog/artifact_dag.py` |

## 2. File pins — ALL changed files, before (CW) / after (my iso) incl. reuse-vs-rederive

CW-before shas ✅ measured 2026-09-23; ISO-after shas: predecessor-done rows are **reused**
(sha taken over from predecessor iso `%TEMP%\cwgu1\repo` into my iso `%TEMP%\cwgu2\repo`,
identity re-verified at copy); rows I finish are **re-derived** (sha measured after my edit).

| # | file | group | before sha256 (CW) | after sha256 (iso) | provenance |
|---|---|---|---|---|---|
| 1 | `tools/pre_push_gate.py` | RC-1 | `28338622CC3BFBD0DD3D98547844DC3500C2EC9A5FE656FAED641C7B8743EDC3` | `D3F308B4A63B37D1A2C44994D824A45FB1BD956BFEF370427BF4FE36EBD1C490` | REUSED (predecessor GREEN, re-verify) |
| 2 | `src/company_wiki/source_catalog/archive_retired_evidence.py` | RC-2a | `BBE855E4495E82D2A40B0185C9DB8EFA2639449FDD5F768120538ABB992B28AC` | `2A236072E0C3CB3C3379020E855A1433091FBBDA42865C04AD0A6FDBC2AE01AD` (predecessor; re-measure) | REUSED + re-verify/mutation |
| 3 | `src/company_wiki/source_catalog/observability.py` | RC-2b | `EDCBECCB9B13778EFE2D80C58A401C345856BF04220462E1FBBE56EA96111F4E` | `D398F92176AA91B49DC5B431C22BF7F98525D167B18DA20659742AE3B1FAA5D8` | REUSED (predecessor →6 GREEN) |
| 4 | `src/company_wiki/source_catalog/prompt_injection.py` | RC-2c | `88154DE4AB7630606C2545CDCDF9C3AC44FAF32BCAE0F83F33A1CEBC6D490F33` | `815691D1EB2B2A896CAB0B5A82B46A2A06A6AF978E720B46E2179D19523FD5D0` | REUSED (predecessor →15 GREEN) |
| 5 | `src/company_wiki/source_catalog/prune_retired_evidence.py` | RC-2d | `0C99BBE0C5F4EF16E7F84BA8AAE0548EF6F59A0080274D5BD1CE83A7D37990B0` | `CE35EAB403F709D2AD8F28D586B44E02DD8C2D5C6844F5215F8699B4BA7C22B9` ✅ | RE-DERIVED (PR4 completed by me) — RED/GREEN/MUT done |
| 6 | `tests/contract/test_fc906a_producer_binding_metadata.py` | TEST-faces | `5D1B23FD3695…` (sha full at close) | `5C4E3FCB8F4CE04A310B474A3A69D7E174747E2B4E3EC775E1F89A6B5CEA322A` | REUSED (predecessor adaptation) + verified |
| 7 | `tests/contract/test_source_catalog_archive_retired.py` | TEST-faces | `0A4195B1CF54…` | `CF5D8D1A0C6606E917CAB7FF444F5D3A220FBABAD550A9ABE2ABD4EC7DB7BE21` | REUSED (predecessor) + verified |
| 8 | `tests/contract/test_source_catalog_prune_retired.py` | TEST-faces | `E0727C70414B…` | `D70EECF3CE70CD6D548A067081766048F45CBC277BC583EEA297B6DE2C8763DA` | RE-DERIVED (this attempt: `now=` + D1 manifest-gated fixtures) |
| 9 | `tests/contract/test_fc905_receipt_envelope.py` | TEST-faces (stale6) | `555D15C1B847…` | `429DCA0FCE477419EE5B39A64A53EFE8CBBF26D173F0907639BD89F84FA5DD0A` | REUSED (predecessor) + verified |
| 10 | `tests/contract/test_gp003_llm_exit_receipt_privacy_gate.py` | TEST-faces (stale6) | `6DC6A87885D4…` | `768CF10D102D15C56C8B7E5B52E304CB6B94D781D6545FE0F8B3D46E60562C7D` | REUSED (predecessor) + verified |
| 11 | `tests/contract/test_r4b05_metadata_provenance.py` | TEST-faces (stale6) | `BD87715433EC…` | `7FCC2F91D82BF21C4DCBC38F6FB456FC1A72A882EEC0C639E1A84D3BB7E9BDC4` | REUSED (predecessor) + verified |
| 12 | `tests/contract/test_source_catalog_focus_admission.py` | TEST-faces (stale6) | `62F35F780E64…` | `F6A5B932A3A77C75B1E69C49919726DCC76F57B608E271E7BD28A20C1E34FF39` | REUSED (predecessor) + verified |
| 13 | `tests/contract/test_source_catalog_worker.py` | TEST-faces (stale6) | `0993C90E0AFE…` | `970FD40855549B5B040241E6ADB85E16AB86CF3DC684FDC91A90D216EF71DA85` | REUSED (predecessor) + verified |
| 14 | `tests/contract/test_zr1003_shadow_assertions.py` | TEST-faces (stale6) | `8853FC7157F6…` | `3185F67630D28356BD130CB1A0F70050E1F6A14941EB12EB97628D09101A8E61` | REUSED (predecessor) + verified |
| 15 | `tests/contract/test_archive_retired_evidence_fail_closed.py` (NEW file — COVERAGE vehicle) | COVERAGE | (new file — none) | `⏳ at close` | RE-DERIVED (this attempt: 12 fail-closed tests) |

Untouched-but-pinned (sha before == after, checked at close):

| file | sha256 | role |
|---|---|---|
| `tests/contract/test_fc1204_complexity_ratchet.py` | `BCD01361E3025F99A78D8DB8452116D05D81DE685A4895D7B6FF34D7E93BB3F2` | frozen CC table (archive 7 / observability 6 / prompt_injection 15 / prune 12) |
| `tests/contract/test_fc1204_coverage_ratchet.py` | `FA0001209BB43BF49E63CA9B9D9463485E6F35B1B8ACCB69D0E7F78DEFE31C85` | coverage floor 95 (archive) |
| `tests/unit/test_prompt_injection_guard.py` | `D3BDE1A3D5EC2495474AAE5B91595362B2CAAD4C8A0178C6927BF2D8023EEC3F` | already-adapted unit face — UNTOUCHED (17 green) |
| `tests/unit/test_stage_taxonomy.py` | `073195190BBF322AFC2200DD6C00B0EE42F9050CAA286C2D9A5F206D6EECA612` | already-adapted unit face — UNTOUCHED (20 green) |

## 3. Complexity BEFORE/AFTER — 4-row RC-2 family (ratchet test's own AST counter)

BEFORE numbers = CW files; AFTER numbers = iso files. Per-function tables live in
decision.md; row summary:

| row | file | frozen | max BEFORE | max AFTER | status |
|---|---|---|---|---|---|
| RC-2a | archive_retired_evidence.py | 7 | 19 | 6 ✅ | RED/GREEN/MUT done (`16*`) |
| RC-2b | observability.py | 6 | 27 (`_redact_assignments`) | 6 ✅ (predecessor `24-CC-observability-AFTER.log`) | RED/GREEN/MUT done (`23*`) |
| RC-2c | prompt_injection.py | 15 | 17 (`record_prompt_injection_review`) | 15 ✅ (predecessor `24-CC-prompt_injection-AFTER.log`) | RED/GREEN/MUT done (`24*`) |
| RC-2d | prune_retired_evidence.py | 12 | 27 (`prune_retired_evidence` main; `_load_verified_archives` 16) | 12 ✅ (main 9, `_build_plan` 12) | PR4 + F821 fix + RED/GREEN/MUT done (`11`–`15*`) |

## 4. Iso harness

| item | value |
|---|---|
| predecessor iso (FROZEN, cite-only) | `%TEMP%\cwgu1\repo` |
| my iso (working) | `%TEMP%\cwgu2\repo` — full copy of cwgu1 (robocopy /E, caches excluded), identity re-verified by sha of the 7 pinned src/tool/test files |
| layout | `src` `tests` `scripts` `config` `tools` `.source_catalog\security_master` + root `conftest.py` `pytest.ini` `pyproject.toml` (targeted copy — CW tree is 133 GB) |
| DIFF vehicle | `<attempt>\changes.diff` (git diff --no-index OLD→NEW; scratch apply-check + byte-identity proof) |
| scratch | `%TEMP%\cwgu2\verify` (apply-check repo), evidence scripts in `<attempt>\evidence` |
| tests' basetemp | pytest default derived from %TEMP% (predecessor `CW-BASETEMP-DECISION` logs: no relocation needed) |

## 5. Environment (inherited from predecessor binding, re-verified at first run)

| item | value |
|---|---|
| `python` (PATH) | `C:\Miniconda\python.exe` — 3.13.9 (matches push protocol) |
| alt interpreter | `<CW>\.venv\Scripts\python.exe` — 3.14.2 (interpreter-sensitivity fallback) |
| `ruff` (PATH) | `C:\Miniconda\Scripts\ruff.exe` — 0.15.18 |
| pytest | 9.1.1 (+timeout 2.4.0, asyncio 1.3.0 auto) |

## 6. Test-face authorization map (what may be edited)

| authorization | file(s) | notes |
|---|---|---|
| fc906a fix | `tests/contract/test_fc906a_producer_binding_metadata.py` | evidence_payload etc. per new writer contract |
| archive test stale | `tests/contract/test_source_catalog_archive_retired.py` | stale API after split |
| prune test now= | `tests/contract/test_source_catalog_prune_retired.py` | `now=` keyword-only arg |
| 6 stale contract tests | fc905 / gp003 / r4b05 / focus_admission / source_catalog_worker / zr1003 (contract tier) | final stale list = repo-wide grep `record_prompt_injection_review(` (8 hits: 6 stale + fc906a + unit guard) |
| tests/unit two faces | UNTOUCHED | `test_prompt_injection_guard.py` (17 green), `test_stage_taxonomy.py` (20 green) — already adapted |
| coverage lane | 1 vehicle only: new test file OR existing archive family additions | covering archive file's NEW exception paths |
| product sources | ONLY the 5 files (4 product + gate) | zero other product edits |
