# CW-TEST-DEBT — recovery (a20260922-01)

Nothing here needs to be done unless the pass must be unwound. This card wrote
exactly **two** files in the company-wiki tree and zero production sources.

## 1. Exact revert = restore the before-pins

The pre-edit bytes were copied out read-only **before** the first edit and are
kept in `before/`. `binding.json → write_targets_before_after[*]` proves
`before/<file>` sha256 == the live pre-edit pin for each file
(`before_copy_matches_live_before_pin = true`), so restoring is byte-exact.

| file | revert to (sha256) | restore command |
|---|---|---|
| `company-wiki/tests/unit/test_readiness_graph.py` | `71893f5d0db8ca675e05ebcda6d7feebefde7ee9a7a19350461efc0ece4708a7` | `Copy-Item <A>/before/test_readiness_graph.py C:\Users\郑曾波\Projects\company-wiki\tests\unit\test_readiness_graph.py -Force` |
| `company-wiki/tests/unit/test_prompt_injection_guard.py` | `c05e25fb4f2e3e1c72143ee3a7c56eccf8a7bddf750efb0394984561484f9bae` | `Copy-Item <A>/before/test_prompt_injection_guard.py C:\Users\郑曾波\Projects\company-wiki\tests\unit\test_prompt_injection_guard.py -Force` |

Verify after any revert:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath \
  "C:\Users\郑曾波\Projects\company-wiki\tests\unit\test_readiness_graph.py", \
  "C:\Users\郑曾波\Projects\company-wiki\tests\unit\test_prompt_injection_guard.py"
```

Expected = the two revert hashes above (they equal the values in the card's
dispatch and in `evidence/raw/live_pins_start.json`).

## 2. Production sources need NO recovery

They were never written: the three live files re-hash at close to their
before-pins —
`f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08`
(`prompt_injection_guard.py`),
`7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618`
(`prompt_injection.py`),
`3f4c43b0049eca71fde4f7d9152b02674a26679b4470f6607383eb1820685acc`
(`readiness_graph.py`) — see `evidence/raw/live_pins_close.json`
(`production_sources_read_only[*].unchanged = true`).

## 3. No mutant left installed (proof)

Mutations M1/M2 were applied to **mirror copies only** (`%TEMP%\cwtd-a20260922-01`),
never to the product tree, and each was restored from the delivered files:
`RESTORE_rdg_matches_after=True`, `RESTORE_pig_matches_after=True`, and the
post-restore run is 26 passed
(`evidence/raw/mut_restored_confirm_green.txt`,
`evidence/raw/mutation_summary.json → R.matches_oracle = true`). The delivered
files therefore hold only the intended edits (their after-pins are the same
values listed in §1's inverse table).

## 4. Scratch cleanup (safe at any time)

```powershell
Remove-Item -Recurse -Force "$env:TEMP\cwtd-a20260922-01"
Remove-Item -Recurse -Force "$env:TEMP\pytest-of-*" -ErrorAction SilentlyContinue
```

Nothing under `%TEMP%` is an input to any later card: the evidence that matters
is already copied into `<A>/evidence/raw/`. Deleting the mirror loses only the
scratch tree; every raw run log is inside the attempt.

## 5. If the pass must be rolled back wholesale

Delete this attempt directory? **No** — keep it: `oracle_freeze.json` is the
proof the oracle preceded the edits, and `evidence/raw/red_unedited_on_merged.txt`
is the only record of the pre-edit RED. Rolling back the *product* only means
§1's two `Copy-Item` commands; the attempt directory stays as the audit record.
