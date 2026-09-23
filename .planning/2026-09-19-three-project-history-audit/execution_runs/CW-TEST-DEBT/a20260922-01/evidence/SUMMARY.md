# CW-TEST-DEBT / a20260922-01 — evidence SUMMARY

All runs: cwd = `%TEMP%\cwtd-a20260922-01` (production `src` copy + the **3
merged GUARD-MERGE iso faces** overlaid + prod `conftest.py`/`pytest.ini`/`tests`
copied), `python -X utf8 -m pytest … -q --no-header -p no:cacheprovider`,
`PYTHONIOENCODING=utf-8`. RF/CW product trees were never opened for write by a
run; mutations were mirror-local and restored.

| # | run | result | raw |
|---|---|---|---|
| 0 | oracle frozen BEFORE any edit/run | sha256 `9334302aa236da374e74f69d9cbfa95e40aaf5ae0d3e76afd0f246079e820a42` @ 2026-09-22T23:59:56.707Z | `../oracle_freeze.json` |
| 1 | start pins (2 tests + 3 production + 3 iso faces) | production == before pins; iso == reviewer ACCEPT pins | `raw/live_pins_start.json` |
| 2 | mirror scaffold, overlaid faces re-hashed | `d7125478…` / `88154de4…` / `50c94de2…` | `raw/mirror_setup.json` |
| 3 | **RED** — UNEDITED tests, merged faces | **15 failed / 11 passed** (4 F readiness + 11 F pi) = reviewer Run 1, names byte-identical | `raw/red_unedited_on_merged.txt` |
| 4 | **GREEN (a)** `test_readiness_graph.py` | **9 passed / 0 failed** (4 F → 0) | `raw/green_a_readiness.txt` |
| 5 | **GREEN (b)** `test_prompt_injection_guard.py` | **17 passed / 0 failed** (11 F → 0) | `raw/green_b_prompt_injection_guard.txt` |
| 6 | **GREEN combined** | **26 passed / 0 failed** | `raw/green_combined.txt` |
| 7 | **M1** − `"state_domain": "review"` from `_seed` (mirror-local) | **4 failed / 5 passed**, the same 4 RED names → seed tag is load-bearing | `raw/mut1_seed_tag_removed.txt` |
| 8 | **M2** − `evidence_payload=` from `_write_receipt` (mirror-local) | **7 failed / 10 passed**, exactly the 7 payload-dependent names → payload is load-bearing | `raw/mut2_payload_removed.txt` |
| 9 | **restore** from the delivered files (sha256 == after-pins) | **26 passed** | `raw/mut_restored_confirm_green.txt` |
| 10 | after-pins of the 2 edited files | `a5db0c9c…f368c2` / `d3bde1a3…23eec3f` | `raw/live_pins_after_edits.json` |
| 11 | machine-checked oracle checks | 5/5 true (`red_matches_reviewer_run1`, `green_a_9_of_9`, `green_b_0_failed_17_passed`, `green_combined_26`, `mutations_as_oracle_pinned`) | `raw/oracle_checks.json` |
| 12 | mutation detail + `matches_oracle` per mutation | M1/M2/R all true | `raw/mutation_summary.json` |
| 13 | close pins: 3 production sources (read-only) + 2 targets + 3 iso faces; `git_commands = 0` | production 3/3 unchanged | `raw/live_pins_close.json` |
| 14 | deliverable hashes (oracle == freeze, sources == before pins, targets == after pins) | see that file | `../evidence/final_deliverable_hashes.json` |

**Card-number note**: the dispatch's 「22/22」 for `test_prompt_injection_guard.py`
is void — the file has exactly 17 tests (proved read-only before the freeze, and
by the reviewer's own 11 F / 6 P). Binding expectation = oracle (b'):
**0 failed, collected == 17, the 11 RED names map one-for-one to GREEN** — met.
Combined GREEN is 26/26 = 9 + 17. Parent ruling recorded in `decision.md §3`.
