# GUARD-MERGE — recovery.md (per-file revert to a chosen sibling iso)

All three merged faces live in `iso/`.  Each can be reverted to ANY sibling's
frozen iso byte-for-byte with one `Copy-Item` (the source attempts are
READ-ONLY, so this only ever writes into this attempt — or, after review +
commit, into production).

Variables:
`RUNS = <plan>/execution_runs`, `A = RUNS/GUARD-MERGE/a20260922-01`,
`CW = C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog`.

## Revert one file (attempt-local)

| target face | command (from the attempt) |
|---|---|
| guard → TTL's REJECT form only | `Copy-Item $RUNS\TTL-30D-POLICY\a20260922-01\iso\prompt_injection_guard.py $A\iso\prompt_injection_guard.py` → `142ae848…d7dd` |
| guard → FIX's C7 face only | `Copy-Item $RUNS\FIX-W06-GAPS\a20260922-01\iso\pi_pkg\prompt_injection_guard.py $A\iso\prompt_injection_guard.py` → `17f0dc58…ed31b` |
| guard → I-06-A's CLIP face (SUPERSEDED — do not ship) | copy from `sources/I06A_guard_live_at_copy_c2af11b3.py` (`c2af11b3…`; the card-pinned pre-fix face `cf9174b5…` was overwritten by I-06-A's own concurrent fix round — see decision.md §0) |
| prompt_injection.py → any sibling | `Copy-Item $RUNS\FIX-W06-GAPS\a20260922-01\iso\pi_pkg\prompt_injection.py $A\iso\prompt_injection.py` → `88154de4…0f33` (TTL/I-06-A never edited it: their face == production `7b22f239…`) |
| readiness_graph.py → any sibling | `Copy-Item $RUNS\FIX-W06-GAPS\a20260922-01\iso\pi_pkg\readiness_graph.py $A\iso\readiness_graph.py` → `50c94de2…c97b` (only FIX edited it) |
| any face → production baseline | `Copy-Item $A\before\<name> $A\iso\<name>` → guard `f900a13d…`, pi `7b22f239…`, readiness `3f4c43b0…` |

Verify after any revert:
`Get-FileHash -Algorithm SHA256 <file>` against the table in `oracle.md §0`
(`before` column = production, sibling `after` columns), or against
`binding.json → before_faces / merged_faces / sources_read_only`.

## Full-rollback of the whole attempt

The attempt is self-contained: delete nothing outside `$A` is required —
every mirror it created lives under `%TEMP%`
(`guardmerge-ttl-mirror`, `guardmerge-rf-tests`, `guardmerge-merged-pkg`,
`guardmerge-merged-src`, `guardmerge-cwtests-origseed`, `guardmerge-statusquo`)
and can be removed with:

```powershell
@("guardmerge-ttl-mirror","guardmerge-rf-tests","guardmerge-merged-pkg",
  "guardmerge-merged-src","guardmerge-cwtests-origseed","guardmerge-statusquo"
 ) | ForEach-Object { Remove-Item -Recurse -Force "$env:TEMP\$_" -ErrorAction SilentlyContinue }
```

Production was never written, so a production rollback is a no-op
(re-verify: `Get-FileHash` on the three CW files must still be
`f900a13d… / 7b22f239… / 3f4c43b0…`).

## Mutant state

No mutant is left installed: `run_mutations_guard.py` and
`run_mutation_disposal.py` restore the merged faces after every mutant and
assert byte-identity (`_restored.restored_byte_identical = true`,
`battery_v_disposal_summary.json.restored_byte_identical = true`), with a
final confirm run of 16/16 and case J PASS.
