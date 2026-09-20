# M13 recovery note

Card M13 (`asset_management`), attempt `a20260919-01`.

**not_applicable_with_reason.** `calculate_registered_model` for `asset_management` is a pure
in-process function: no durable state, no lock, no lease, no partial publication, no filesystem
side effect. A raised `ModelRegistryError` leaves nothing to roll back, so there is no
restart/retry path to exercise. The card's own STOP_BRIDGE branch is
`not_applicable_with_reason` as well, because this is a flow model with no opening/closing
reconciliation (oracle.md section 4).

What IS covered instead:

- `selfcheck_result.json` proves the runner's exit code carries the verdict
  (0 pass / 1 harness error / 2 no verdict / 3 negative not refused) and that a corrupted
  **scratch** copy cannot pass: scenarios A, F and D return 2, B returns 3, E returns 1, and the
  control returns 0.
- Every negative case is built from a fresh `deepcopy`, so failures cannot contaminate later
  cases.
- The frozen evidence was hash-verified before and after the self-check
  (`frozen_unchanged_by_the_selfcheck`, `frozen_still_equals_freeze_time_hashes` in
  `selfcheck_result.json`).
- The one harness failure that really happened is kept in the record rather than replayed away:
  the first `run_card.py` invocation returned rc=1 (`NameError: name 'key' is not defined` in the
  runner while assembling the positive block). It was a runner defect, not a product or oracle
  defect; it was corrected before any verdict existed, and the frozen evidence was never touched
  (`commands.json` unit `B-product-run`, field `first_invocation`).
- `oracle_md_before_boundary_repair.bin` keeps the pre-repair bytes of `oracle.md` so the r2
  boundary repair is auditable byte-for-byte (exactly one separator byte was removed; the frozen
  body prefix hash is identical before and after).

The only non-pure step in this card would be read-only disclosure extraction, which this attempt
does not perform at all (no D-stage mapping).
