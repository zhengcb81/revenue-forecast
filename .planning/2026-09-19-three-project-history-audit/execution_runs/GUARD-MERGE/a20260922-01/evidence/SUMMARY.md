# GUARD-MERGE — evidence SUMMARY (a20260922-01)

Oracle: `oracle.md` frozen FIRST, sha256 `c346e4503834db3a197177acd932a093d501d232fb6a3f361c47f0ac78e552d5` (`oracle_freeze.json`).

## RED (pre-merge status quo) → GREEN (merged) — `raw/red_green_status_quo.json`

| id | gap | BEFORE (RED, observed) | MERGED (GREEN, observed) |
|---|---|---|---|
| R1 | over-cap TTL | `raised: null, cache_state: hit` on `ttl=86400*365` | `PromptInjectionGuardError: ttl_seconds exceeds policy cap of 2592000s` |
| R2 | `detected_and_ignored` disposal | write **accepted** with no tuple/trust root/signature | `PromptInjectionReviewError: disposal authorization unavailable: ignore_reason` |
| R3 | unbound write | receipt written with no `source_sha256`/`policy_hash` | `PromptInjectionReviewError: source_sha256 must be a lowercase SHA-256` |
| R4 | past-now resurrect | `cache_state: hit` with `now < reviewed_at` | `not_reviewed/tampered` — `receipt reviewed_at is after now (clock anomaly; now may only tighten freshness)` |

`summary: red_all_four_confirmed=true, green_all_four_ok=true`

## Batteries

| # | battery | result | raw |
|---|---|---|---|
| i | TTL probe suite (REJECT semantics) | **16/16 gating**, `gating_failed=[]`, `guard_sha256=d7125478…` | `raw/battery_i_green.json` |
| i* | TTL's UNMODIFIED script first (honest composition attempt) | crash = conflict C-1 (`evidence_payload must be provided`) | `raw/battery_i_unmodified_conflict.log` |
| i** | after fixture C-1 fix, before C-2 fix | 15/16, `gating_failed=[TTL-G2]` | `raw/battery_i_adapted_probe_r1.json` |
| ii | FIX product tests (RF `test_message_contract_pins` + `test_fc905b`) on %TEMP% mirror importing merged faces | **14 passed** | `raw/battery_ii_rf_product_tests.txt` |
| iii | state_domain four negative forms (FIX's `s_c7_state_domain.py --pkg-dir iso`) | **N1–N4 PASS → C7 SCENARIOS: PASS** | `raw/battery_iii_state_domain_four_negatives.txt` |
| iv | I-06-B 18-case harness, merged faces installed as the `fixed` arm | **16 GREEN / 2 RED**, the 2 = **H2 + L3** (their known blocked pair; deviation: L3a now passes because the pin test exists) | `raw/battery_iv_i06b/summary.json`, `raw/battery_iv_i06b.log` |
| v | mutations (guard): cap-only / cap+isfinite (TTL MUT-1 exact) / past-now / isfinite | killed: `[G1,N1,N2,N3]` / `[G1,N1,N2,N3,N8,N9]` / `[N5,N6]` / `[N8]`; restore byte-identical + confirm **16/16** | `raw/battery_v_mutations_summary.json` |
| v | mutation (disposal gate) → I-06-B case J | mutant **FAIL** (J1/J2 red) → restore **PASS**, pi sha256 back to `88154de4…` | `raw/battery_v_disposal_summary.json` |
| – | rule-4 side battery: I-06-A's 17 cases on merged | 13 PASS / 4 FAIL (`N6` payload, `N8`+`N8b` CLIP, `N10` `state_domain_of`) — attributed in `decision.md §4` | `raw/battery_rule4_i06a_cases_on_merged.json` |
| – | CW product unit tests on merged (informational → handoff debt) | 11 failed/15 passed (adapted seed); 4 failed/5 passed (production seed) | `raw/informational_*.txt` |

## NaN coverage check (oracle §4-v)

TTL's probe already carries an explicit NaN case — `TTL-N8` (`ttl=NaN` must
raise) — and `TTL-N9` for `+inf`.  Mutation **v3** (isfinite line removed)
turns exactly `TTL-N8` red, so no new case and no dated append was needed;
mutation **v1b** reproduces TTL's own MUT-1 frozen set
(`[G1,N1,N2,N3,N8,N9]`) when the whole cap+isfinite block is removed.

## Integrity

* production 3 files: before == close (re-hashed) — `binding.json → before_faces[].production_unchanged=true`
* sibling pins: all matched at attempt start; I-06-A's guard drifted mid-attempt **by its own fix round** — disclosed in `binding.json → sources_read_only[].drift_observed`
* git: zero commands; `changes.diff` = difflib (sha256 `87595cdbad354409579d6ecd1e535783aa418fef04e9d886aad142e9165e201a`, 735 lines, 9+6+3 hunks)
* mutants: none left installed (restore assertions in both mutation scripts)
