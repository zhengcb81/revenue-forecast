# M15 recovery note

Card M15 (`transport`), attempt `a20260919-01`.

**not_applicable_with_reason.** `calculate_registered_model` for `transport` is a pure in-process
function: no durable state, no lock, no lease, no partial publication, no filesystem side effect.
A raised `ModelRegistryError` leaves nothing to roll back, so there is no restart/retry path to
exercise. The card's own STOP_BRIDGE branch is `not_applicable_with_reason` as well, because this
is a flow model with no opening/closing reconciliation (oracle.md section 4).

What IS covered instead:

- `selfcheck_result.json` proves the runner's exit code carries the verdict
  (0 pass / 1 harness error / 2 no verdict / 3 negative not refused) and that a corrupted
  **scratch** copy cannot pass: ten scenarios were run (including the two F-01 expectation-
  declaration scenarios and their pre-fix-runner counterparts) and every one returned its
  expected code (A-corrupt-value=2, B-corrupt-negative-case=3, C-control=0, D-missing-expectation=2, E-harness-error=1, F-corrupt-shape=2, G-corrupt-case-expected=2, G-pre-fix-runner-corrupt-case-expected=0, H-drop-negative-case=2, H-pre-fix-runner-drop-negative-case=0).
- Every negative case is built from a fresh `deepcopy`, so failures cannot contaminate later
  cases.
- The frozen evidence was hash-verified before and after the self-check
  (`frozen_unchanged_by_the_selfcheck = true`,
  `frozen_still_equals_freeze_time_hashes = true`).
- The two declared non-oracle product units (the metadata enumeration and the labelled post-hoc
  probe) write only inside `evidence/M15/` and `recovery/probes/`.
- **First-invocation raw bytes (review finding F-05):** the raw stdout/stderr of the FIRST failed
  invocation of a command are NOT retained in this attempt. For the M13 sibling attempt that was
  the runner's `NameError` first run; here no first invocation failed. What exists is the raw exit
  code plus the narrative in `commands.json`; every later self-check scenario DOES keep its raw
  stdout/stderr under `recovery/selfcheck/stdout_*.txt` / `stderr_*.txt`. From revision r3 on, any
  first failed invocation is saved verbatim as `recovery/first_invocation_*.<stdout|stderr>.txt`
  and referenced from `commands.json`.
- **Pre-fix runner revision:** `recovery/runner_before_F01_fix.py` (sha256
  `e709408f7f6518be63fc00d5c4c444c8738dbf1ba7a53383c3821882c9054c9e`) is kept because the F-01
  defect is demonstrated by running that revision against the same corrupted scratch copy and
  observing rc=0 where the current revision returns rc=2.

No disclosure extraction, no download and no provider call happens in this attempt at all.
