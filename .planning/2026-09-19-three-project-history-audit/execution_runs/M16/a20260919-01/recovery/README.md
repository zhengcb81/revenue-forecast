# M16 recovery note

Card M16 (`real_estate_rental`), attempt `a20260919-01`.

**not_applicable_with_reason.** `calculate_registered_model` for `real_estate_rental` is a pure in-process
function: no durable state, no lock, no lease, no partial publication, no filesystem side effect.
A raised `ModelRegistryError` leaves nothing to roll back, so there is no restart/retry path to
exercise. The card's own STOP_BRIDGE branch is `not_applicable_with_reason` as well, because this
is a flow model with no opening/closing reconciliation (oracle.md section 4).

What IS covered instead:

- `selfcheck_result.json` proves the runner's exit code carries the verdict
  (0 pass / 1 harness error / 2 no verdict / 3 negative not refused) and that a corrupted
  **scratch** copy cannot pass: six scenarios were run and every one returned its expected code
  (A-corrupt-value=2, B-corrupt-negative-case=3, C-control=0, D-missing-expectation=2, E-harness-error=1, F-corrupt-shape=2).
- Every negative case is built from a fresh `deepcopy`, so failures cannot contaminate later
  cases.
- The frozen evidence was hash-verified before and after the self-check
  (`frozen_unchanged_by_the_selfcheck = true`,
  `frozen_still_equals_freeze_time_hashes = true`).
- The two declared non-oracle product units (the metadata enumeration and the labelled post-hoc
  probe) write only inside `evidence/M16/` and `recovery/probes/`.

No disclosure extraction, no download and no provider call happens in this attempt at all.
