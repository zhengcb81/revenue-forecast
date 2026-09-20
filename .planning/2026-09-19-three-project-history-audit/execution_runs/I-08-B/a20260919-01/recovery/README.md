# recovery/ — not applicable, with the reason

This card performs **no stateful product operation**, so there is no failed state to
recover from:

- no publication was issued, no production registry row was appended, no worker was
  started and no lock was taken;
- the production tree is byte-identical to the pre-edit binding
  (`../after/I08B-c10-hash-inventory.stdout.txt` reports
  `PRODUCTION FILES CHANGED BY THIS CARD: 0`), and the production registry still has
  its original 60 lines and sha256 `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`;
- every side effect (fake provider processes, isolated trust domain files, pytest
  temp trees, isolated registry) happened inside `../iso/` and `../scratch/`.

## What WOULD be the recovery surface if the change is later applied to the product repo

If a later card applies `changes.diff` to the production tree and something goes
wrong, the correct rollback is a **revert of that patch**, not a rewrite of history:

| Artefact | Rollback action | Must NOT be done |
|---|---|---|
| the 12 patched files | re-apply the inverse of `changes.diff` (or `git revert` the applying commit) | `git reset --hard` / `stash` over user changes |
| `tests/golden_behavior_hashes.json` | restore the pre-change file kept at `../before/golden_behavior_hashes.json` | hand-editing hashes to match a broken run |
| historical receipts / registry rows | nothing: they are never rewritten by this change | re-signing or re-hashing old artefacts |
| isolated trust domain + test keys | delete the attempt directory (they are attempt-local) | writing a test key into `config/` |

## Contents

- `changes.diff` — a copy of `../changes.diff`, kept here so the rollback surface is
  discoverable from the recovery directory. The authoritative copy is
  `../changes.diff` (its sha256 is in `../binding.json.post_run_measurements`).
