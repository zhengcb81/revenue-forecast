# B3-PREREQ a20260922-01 — Recovery / how to verify or undo

Nothing here is destructive; every mutation was already restored and hash-verified
(`../evidence/tree_integrity.txt`). This file tells a reviewer or a future owner how to
re-check each claim or to roll back the one out-of-attempt write.

## Layout

```
a20260922-01/
  oracle.md + oracle.sha256     frozen before any run (one recorded pre-run amendment)
  iso/conftest.py               THE FIX (REM-47 guard + conflict-aware provenance)
  iso/fixed2/                   copy of B3's iso/fixed + REM-49 comment fix (only source_preparation.py differs)
  b3_reference/iso/             byte-exact copy of B3's delivered iso/ = read-only RED baseline
  tests/                        property tests + probe harness (own fixtures)
  scratch/                      run artifacts, mutation backups (*.bak), compare_fc904.py
  evidence/                     raw stdout of every run + SHA256SUMS.txt
  binding.json commands.json decision.md handoff.json changes.diff
```

## Re-verify everything (read-only)

```powershell
cd <this attempt>
python -X utf8 -B -m pytest -q -p no:cacheprovider tests/          # expect 11 passed
python -X utf8 -B scratch/compare_fc904.py                          # expect per_node_identical=true (needs the two junit xml files in evidence/)
# RED halves (expect rc=1):
$env:B3P_GUARD_CONFTEST='b3_reference/iso/conftest.py';   python -X utf8 -B -m pytest -q -p no:cacheprovider tests/test_rem47_guard_order.py
$env:B3P_PROV_CONFTEST='b3_reference/iso/conftest.py';    python -X utf8 -B -m pytest -q -p no:cacheprovider tests/test_rem47_provenance_conflict.py
Remove-Item Env:B3P_GUARD_CONFTEST, Env:B3P_PROV_CONFTEST
Get-FileHash evidence\rem48_superseded\handoff.json.pre-correction -Algorithm SHA256   # CEE4B0DD…
Get-FileHash ..\B3-I05C-delivery-fixes\a20260921-01\handoff.json -Algorithm SHA256      # E33D82A9… (corrected)
```

Byte pins: see `binding.json` and `evidence/_pin_hashes.txt`; per-file evidence hashes in
`evidence/SHA256SUMS.txt`.

## Mutation backups (all restores already applied and verified)

| file | backup | current must equal backup |
|---|---|---|
| `iso/conftest.py` | `scratch/conftest_pre_MUT1.bak`, `scratch/conftest_pre_MUT2.bak` | yes (sha `7437BA9D…`) |
| `iso/fixed2/rf_scripts/source_preparation.py` | `scratch/sp_pre_MUT3.bak` | yes (sha `91A6DC32…`) |

To re-enact a mutation for review: copy the current file aside, apply the edit described in
`commands.json` (`MUT-*`), run the named test, then copy the backup back and re-check the hash.

## Roll back the REM-48 record correction (if an owner prefers the original wording)

```powershell
Copy-Item evidence\rem48_superseded\handoff.json.pre-correction `
          ..\B3-I05C-delivery-fixes\a20260921-01\handoff.json -Force
```
That restores sha256 `CEE4B0DD…` (the pre-correction bytes) — but note the false
"compares every frozen hash … all matched" claim returns with it, and the
`NOT_REHASHED` flag at `after/integrity.json:23` was never deleted either way.

## Boundaries a recovery must keep

- B3's accepted `iso/fixed/**` in `../B3-I05C-delivery-fixes/a20260921-01/iso/fixed/` must
  remain byte-identical (pinned in `binding.json`); this attempt never wrote it.
- Production (`C:\Users\郑曾波\Projects\revenue-forecast`, `…\Projects\company-wiki`) stays
  read-only; no git write was made by this attempt; frozen `before/` stays untouched.
- `handoff.status` stays `review_pending`; promotion of the fixed bytes stays a separate
  owner decision.
