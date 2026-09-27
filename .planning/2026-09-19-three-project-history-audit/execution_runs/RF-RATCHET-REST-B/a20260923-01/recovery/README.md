# recovery/README.md — RF-RATCHET-REST-B a20260923-01

## What this card changed (delivery surface only)

`changes.diff` (sha256 `bcca249844b39dc3c48e86c4bacacd9a4d97fe4f250f64860ba588ba4d6731e9`,
23626 B) contains EXACTLY three sections, one per owned file:

| file | before (= owner-authorized promotion payload, production bytes at card start) | after (refactored) |
|---|---|---|
| `scripts/model_registry.py` | `62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081` (30116 B) | `2154ad4f3c6490a3e79c9abf6d46f3bf794094ba66f8623e8719496eec9edc07` (32306 B) |
| `scripts/revenue_core.py` | `8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883` (25842 B) | `678f5f1b7d7141c6d00d25f9ddfa7dfdc36df2d26aa90cd4721246f52db5381a` (27234 B) |
| `scripts/revenue_publication.py` | `bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0` (24917 B) | `1910e2761a5cac4a5c2346762dcd9d68c676371bffb57dbf0433c0b6a707f3e4` (25634 B) |

Full machine-readable form: `refactored/manifest.json`. Pinned refactored copies:
`refactored/scripts/*.py`.

**Production was NEVER written by this card** — at card end the three production files still
hash to the promotion-payload values in the left column (verified post-run;
`evidence/integrity/porcelain_scoped_check.txt`: zero product-surface porcelain entries in
baseline and after; all 46 new porcelain lines belong to concurrent parent/sibling planning
activity, none under `scripts/ tests/ tools/ config/ e2e/`).

## Rollback

1. **Applying this card's refactor**: apply `changes.diff` to the three files (parent holds
   commit rights; this card never commits).
2. **Reverting this card's refactor** (back to promotion-payload bytes): restore from
   `recovery/before_images/{model_registry,revenue_core,revenue_publication}.py` — byte-exact
   copies of the production state at card start (shas in the table above), cross-checked
   against the PROMOTION manifest pins (`promotion_batch_manifest.md` `6759d1eb…`) and
   RF-RATCHET-FIX's `binding_before.json` (identical pins).
3. After any restore: re-run `python -X utf8 -B -m pytest tools/tests/test_complexity_ratchet.py
   -q -p no:cacheprovider` — expect the pre-card state (my three rows red again, sibling rows
   unchanged), i.e. the RED captured in `evidence/red/ratchet_red_judged.txt` plus the
   two card rows masked exactly as documented.

## Scratch trees (disposable)

`%TEMP%\rf-rest-b\iso_after` (refactored runnable tree), `iso_revert` (pre-promotion overlay
probe), `mut_tree` (mutation copies, rebuilt per mutation), `basetemp*` (pytest tmp).
All under `%TEMP%`; deleting them loses nothing (everything judged is pinned in this attempt).

## Boundary record

- sources read-only honored; zero git writes (git used: `status`, `log -1`, `show -s/show --stat` only);
- sibling cards' files (RF-RATCHET-FIX: `analysis/confidence.py`, `model_extensions.py`;
  RF-RATCHET-REST-A: `forecast/calc.py`, `generate_input_template.py`, `research/targets.py`)
  never written — their rows byte-identical before/after (row numbers unchanged in every scan);
- frozen ratchet table: `tools/tests/test_complexity_ratchet.py` sha256
  `eb1a36cfd54a8b96e3b5dca6ca4b7a89ca6b1e1605d22eedb69f643245edd10a` before == after;
  literal block sha before == after (`78c06a87…`, extraction rule in `binding_before.json`).
