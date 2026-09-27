# RECOVERY — CW-GATE-UNBLOCK-2 / a20260923-01

## Crash-safe state map (successor of an infra-death; assume this attempt may die too)

| artifact | location | state at any point |
|---|---|---|
| frozen oracle (base + APPEND A) | `<attempt>\oracle.md` | written FIRST, complete |
| living docs | `<attempt>\binding.md` `decision.md` `handoff.md` `commands.md` | updated per step |
| evidence raws | `<attempt>\evidence\*.log` | written at run time (long runs tee'd progressively) |
| predecessor attempt (READ-ONLY) | `execution_runs\CW-GATE-UNBLOCK\a20260923-01` | never written |
| predecessor iso (FROZEN, cite-only) | `%TEMP%\cwgu1\repo` | never written |
| my working iso | `%TEMP%\cwgu2\repo` | all product/test edits live here |
| fixed-file backups | `%TEMP%\cwgu2\scratch\` (`prune_fixed_PR4.py`, `testfaces\`) | restore sources after any mutation |
| staged coverage test | `%TEMP%\cwgu2\scratch\test_archive_retired_evidence_fail_closed.py` | copied into iso tests/ only AFTER the coverage-before run |

## Resume recipe (if this attempt dies)

1. Read `<attempt>\oracle.md` (APPEND A) + `decision.md` + `binding.md` — they carry the
   full remaining-work state; evidence logs carry every judged run's raw output.
2. Verify iso pins vs `binding.md` §2 after-shas (`Get-FileHash`); mutation backups in
   `%TEMP%\cwgu2\scratch` restore any half-mutated file (prune fixed sha
   `CE35EAB403F709D2AD8F28D586B44E02DD8C2D5C6844F5215F8699B4BA7C22B9`;
   observability/prompt_injection restore byte-identical from `%TEMP%\cwgu1\repo`).
3. Remaining steps after the last completed one (see decision.md §5/§4 statuses):
   coverage lane measurement → gate full-run → changes.diff build + apply-check →
   docs close → report to parent.
4. changes.diff is the ONLY delivery vehicle; CW production writes stay ZERO.

## Prohibitions (unchanged)

- predecessor attempt + `%TEMP%\cwgu1` READ-ONLY; CW/RF/FF production writes ZERO;
  no network; no git mutations (read-only git + scratch apply-check only);
  no frozen-cap raise; no coverage threshold change; no step bypass.
