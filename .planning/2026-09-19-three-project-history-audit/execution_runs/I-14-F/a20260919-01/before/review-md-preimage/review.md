# I-14-F review — AWAITING INDEPENDENT REVIEWER (not self-signed)

Status: **review_pending**. This file is a stub for the independent reviewer; the implementer
makes no acceptance claim here. Start from `handoff.json` → `binding.json` → `oracle.md`
(Addenda A–C are part of the frozen record) → `decision.md` → `after/evidence_index.json`.

## Suggested reviewer spot-checks (card-specific oracles)

1. Re-run one RED counterexample: extract a pristine company-wiki HEAD tree, run
   `test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths` with cwd_len 166 and
   `--basetemp <cwd>\pytest` — expect the literal `WinError 206` (frozen I-14-C §4a + this
   attempt's `before\deep\pad55\P0-logon_wrapper_quoted-*`).
2. Re-run one GREEN case WITH `iso\tree\conftest.py`: same geometry, expect
   `relocated: true` and a pass (see `after\deep\pad777` logon rows 3/3).
3. Mutation: same tree + `CW_SHORT_BASETEMP_DISABLE=1` at cwd 167/166 → 206/Errno-2 return
   (`after\external-summaries\mutation-disabled-exact167-166.json`).
4. Recompute the criterion: `BASETEMP_MAX_CHARS == 210 - 124 == 86` and the calibration
   table in decision.md against the falsifier rows in
   `after\falsified-normal-r1\` (literal 206 at basetemp 155) and
   `after\external-summaries\addendumC-falsifier-basetemp116.json` (degradation at 116).
5. Unit tests: 13/13 in `after\unit-P0-run4\stdout.txt` (run with the attempt venv).
