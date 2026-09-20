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
  **scratch** copy cannot pass: ten scenarios were run - A, F and D return 2, B returns 3, E
  returns 1, the control returns 0, the two F-01 scenarios (renamed case expectation, deleted case)
  return 2, and their pre-fix-runner counterparts return 0. The full `exit_code_matrix` is in
  `selfcheck_result.json`.
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
- **F-05 (independent review, 2026-09-20) - first-invocation raw bytes are NOT retained.** The raw
  stdout/stderr of that first failed invocation no longer exist; only its raw exit code (rc=1) and
  the narrative in `commands.json` are evidence for it. The same provenance gap applies to the
  bytes of the earlier revision of `scripts/setup_isolation.ps1` (its first run also returned rc=1
  before the git-stderr capture was fixed); that gap is registered in `commands.json`
  (`A0b-setup-isolation.first_invocation.script_revision_note`) and is not papered over. From
  revision r3 on, every self-check scenario keeps its raw stdout/stderr under
  `recovery/selfcheck/stdout_*.txt` / `stderr_*.txt`, and any future first failed invocation is
  saved verbatim as `recovery/first_invocation_*.<stdout|stderr>.txt` with `commands.json` pointing
  at it.
- **F-01 (independent review, 2026-09-20) - pre-fix runner revision kept.** `run_card.py` revision
  r1 decided a negative case purely by `isinstance(exc, ModelRegistryError)` and never read the
  case's declared `expected`, so a renamed expectation or a deleted case still gave rc=0. The
  pre-fix bytes are preserved at `recovery/runner_before_F01_fix.py` (sha256
  `e709408f7f6518be63fc00d5c4c444c8738dbf1ba7a53383c3821882c9054c9e`) and the defect is reproduced
  by running that revision against the same corrupted scratch copy (rc=0) while the current
  revision returns rc=2.
- `oracle_md_before_boundary_repair.bin` keeps the pre-repair bytes of `oracle.md` so the r2
  boundary repair is auditable byte-for-byte (exactly one separator byte was removed; the frozen
  body prefix hash is identical before and after).
- `before_fixes/` keeps the pre-r3 bytes of every evidence file this revision regenerated, so each
  old→new hash in `revision_r3.json` can be recomputed rather than trusted.

The only non-pure step in this card would be read-only disclosure extraction, which this attempt
does not perform at all (no D-stage mapping).
