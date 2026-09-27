# evidence index — WC-1 / I-14-D-R8 a20260923-01

Every instrument run is stored raw: `<name>.json` (machine report), `<name>.stdout.txt`
(exactly what the harness printed), `<name>.rc.txt` (process exit code). Failed attempts are
KEPT with their attempt suffix — nothing is silently replaced.

## Red / green / direction matrix

| files | run | expected → measured |
|---|---|---|
| `red_oracle_r8_base.*` | oracle on unfixed r8_base | rc 3, exactly N14-N18+N23-N28 (11) failed ✅ |
| `red_rule_r8_base.*` | rule on unfixed r8_base | rc 3, exactly 13 fidelity failures, touched `[]`, registered_open 7/7 ✅ |
| `green_oracle_r8_fixed.*` | oracle on fixed tree | rc 0, 61/61, registered_open 7/7 ✅ |
| `green_rule_r8_fixed.*` | rule on fixed tree | rc 3 (by design), fidelity_ok true, 113 rows, credential_leaks `[]`, registered_open_leaking 7 (marker row visible) ✅ |
| `base_oracle_product_base.*` | direction on product_base | keep_must_failed `[]`; frozen 11 red; R3c unconfirmed (disclosed) ✅ |
| `base_rule_product_base.*` | direction on product_base | rc 3, touched `[]` — direction only, no pass claim ✅ |

## Mutation

| files | mutant | expected → measured |
|---|---|---|
| `mutants_build.*` | build MUT-A/MUT-B into %TEMP% | rc 0; mutant shas `9ea51391…` / `8217f100…` ✅ |
| `mutA_oracle_*.*`, `mutA_rule_*.*` | FIX-1 reverted | exactly the 5 REM-06 rows red, R3-05 rows green ✅ |
| `mutB_oracle_*.*`, `mutB_rule_*.*` | FIX-2 reverted | exactly 6 form rows + 2 pricing rows red (rule), 6 oracle red; REM-06 rows green ✅ |

## Bidirectional difference (REM-79 criterion)

| files | content |
|---|---|
| `key_domain_sweep.json` | 350-key frozen domain: old\new `[]` ✅, new\old 114 ⊆ digit-suffixed vocab ✅, near-miss never credential ✅, verdict pass |
| `key_sweep_count_diag.json` | audits 120−114 = `secret_key2/3/12` × case — all already old-true (`secret` single atom); fully explained ✅ |
| `value_start_sweep.json` | 95 printable ASCII at the after-break value start: old\new `[]` ✅, new\old = exactly {`,` `;` `&` `\|` `"` `'`} ✅, 95/95 closed after fix, verdict pass |

## Delivery-target apply check

| files | content |
|---|---|
| `production_apply.json` | production read-only (`edcbeccb…` before/`081fdf5e…` after, in-memory), 3/3 edits landed 1:1, py_compile ok, grafted %TEMP% tree: oracle rc 0/61 + rule fidelity_ok/113 → `green_match_with_r8_fixed: true` ✅ |
| `prodapply_oracle_prod_target_r8.json`, `prodapply_rule_prod_target_r8.json` | raw instrument outputs on the production-target tree |
| `make_changes_diff.*` | builder stdout/rc (rc 0; changes.diff `baec3153…`, deterministic across 2 runs) |

## Freeze + build provenance

| files | content |
|---|---|
| `oracle_prefix_proof.json` | CORRECTION W1 append-only proof: pre-append reconstruction (`prefix+LF`, 17992 B) hashes to the pre-run pin `c6cbf869…` ✅ (attempt-1 without-LF mismatch retained in the same JSON) |
| `build_r8.stdout.txt` / `.rc.txt` | successful build (rc 0): pins, edit shas, harness base→r8 shas |
| `build_r8.attempt1_failed_anchor.*` | FAILED first build (rc 1): rule-row anchor used oracle-harness constant names — guard fired, nothing half-written |

## Retained failed attempts (tooling only, never SUT)

- `*_attempt1_loadbug.stdout.txt` — sweep module-load AttributeError (dataclass needs
  `sys.modules` registration).
- `key_domain_sweep.attempt2_countfield.*` — pass run carrying a non-boolean count field
  (field moved out of `criteria` afterwards).
- `value_start_sweep.attempt2_orderbug.*` — false FAIL from list-vs-set comparison of the
  same six characters (criterion text unchanged; comparison made set-based).

## Close-out

- `final_integrity.json` — recomputed pins of every read-only input + zero-write mtime scan
  (production, register, WC-1 decision, sealed I-14-D attempt, REGISTRY-CLOSURE attempt).
- `final_hashes.json` — sha256 of every deliverable + before/after shas of both targets.
