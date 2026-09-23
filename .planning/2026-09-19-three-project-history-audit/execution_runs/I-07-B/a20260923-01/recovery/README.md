# I-07-B recovery / retention README (attempt a20260923-01)

Exit clause (verbatim from the card): `恢复：保留已取得raw，只回退当前隔离变更。`

## What MUST be kept (raw obtained this attempt)

- `%TEMP%\i07b\cases\<case>\cwroot\companies\**` — every raw/sidecar copy of the three
  frozen samples, including the three **canonical imports produced by the simulated
  downloads** in S-CN-3 / S-US-3 (CN `2026-03-20_cninfo_1225023658_…pdf`,
  US `2026-07-29_sec_0001193125-26-323660_….htm`, and the HK canonical file written under
  S-HK-3). These are the "已取得raw" of this attempt: they are copies/fixtures, never
  production originals — production originals were re-hashed after every run and are
  unchanged (`evidence/snapshot_after.json`).
- All evidence under `execution_runs/I-07-B/a20260923-01/evidence/**` (including the
  superseded `run2.pre_scaffold*/run2.pre_fix2*` directories — they are part of the honest
  run history and must not be deleted or re-run over).
- `fixtures/*.provider.json` (frozen provider simulation fixtures) — needed to reproduce
  the S-3 authorized arms.

## What may be reverted (isolation changes only)

1. `%TEMP%\i07b\cases\**` isolated company-wiki roots (rebuilt catalogs, rebound configs,
   asset copies, empty adapter scaffolding dirs) — **only after the independent review has
   signed off**; delete with
   `Remove-Item -Recurse -Force "$env:TEMP\i07b"` .
   Until then, retain them: they are the state the review may re-run against.
2. `execution_runs/I-07-B/a20260923-01/evidence/wprobe_tmp\**` and
   `evidence\wprobe.json` throwaway probe catalog may be deleted after review (regenerable
   via `CMD-I07B-WPROBE`).
3. Nothing else. No production file, no CW file, no RF product file was modified by this
   attempt (witness: `changes.diff` — 20/20 hashed anchors byte-identical before/after,
   production catalog bytes+mtime identical). If any stray file outside the attempt dir is
   found, STOP and hand it to the owner (do not reset/stash user changes).

## What was never touched (so there is nothing to restore)

- production catalog, production raw/sidecars/derived artifacts, all three git repos
  (no git command in the registry), worker processes (none started; none stopped).

## If a re-run is needed

Use only the argv forms in `commands.json` (I-00-B-bound entry contract), with
`PYTHONPATH=<attempt>/harness/spy;<RF>/scripts;<CW>/src` and `I07B_SPY_DIR` set; rebuild a
case first with `harness/build_iso.py case …` (state templates are deterministic and
hash-recorded in `evidence/cases/<id>/initial_state.json`). Do NOT edit `oracle.md`.
