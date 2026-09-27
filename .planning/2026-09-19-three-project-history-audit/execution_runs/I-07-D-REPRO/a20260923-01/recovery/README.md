# recovery/ — 异常后恢复 / continuity record (I-07-D-REPRO a20260923-01)

This card is a re-run + preservation card (no product code change), so "recovery" here =
the continuity/anti-death record and the crash-recovery rule set for this attempt.

## Crash / interruption recovery rule (carried from START_HERE 无法完成时的确定动作)

1. Evidence is incremental: each sub-run writes argv/stdout/stderr/evidence.json before the
   next starts. On death mid-case: KEEP the partial evidence (never delete — I-07-D §7.1
   precedent: overwrites are disclosed forever), re-bind hashes, resume from the first
   unexecuted command id in commands.json.
2. Preserved raws are the recovery anchor: once CMD-REPRO-F0X-PRESERVE has run, that
   case's judged bytes survive regardless of %TEMP% cleanup. A death between a case run and
   its preserve step = re-copy from the (still-live) scratch tree immediately on resume.
3. Holder/lock processes (hold_file.py / lock_catalog.py) are self-terminating
   (max-hold 300 s / fixed hold 75 s); a crashed driver leaves at most a ≤300 s holder,
   which releases by deadline. Kill-gated PIDs are manifest-registered only.
4. Two identical failures ⇒ stop, compare failure cause with binding, record here; no
   blind retry.

## Incidents this attempt (filled if any occur)

- _(none yet)_

## Re-run reproducibility (the D3 point)

From a clean machine: create a new attempt, copy harness+fixtures+iso template+venv
(copy-fidelity hashes in binding.json), run commands.json in order. The verdicts of
F02/F03/F04 additionally recompute from THIS attempt's preserved raws alone:
`TEMP=<ATT>\evidence\preserved\temp <PY> harness\run_d_matrix.py f02v|f03v|f04v`.
