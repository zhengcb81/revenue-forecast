# M18 recovery note — advertising

**not_applicable_with_reason.** `advertising` is a pure in-process calculation:
`calculate_registered_model` has no durable state, no lock, no lease, no partial publication and no
filesystem side effect. A raised `ModelRegistryError` leaves nothing to roll back, so there is no
restart/retry path to exercise on this model.

What IS covered instead:

- `recovery/selfcheck_result.json` (identical copy of `evidence/M18/mutation_selfcheck.json`) records five
  scratch runs that prove the runner's exit code carries the verdict: a corrupted expectation gives rc 3,
  a neutered negative case gives rc 3, a fidelity mismatch gives rc 2, a missing evidence file gives rc 1,
  and the uncorrupted copy gives rc 0. All five ran against COPIES under `recovery/selfcheck/`, and the
  frozen evidence was re-hashed afterwards: `frozen_evidence_unchanged: true`.
- `recovery/regen_verify/` holds a second generation of the frozen oracle from the same script; the
  comparison is recorded in `evidence/M18/oracle_regen_proof.json` (`all_byte_identical: true`).
- `recovery/line_boundary_demo/` holds the scratch file used to demonstrate the r2 hash rule; see
  `evidence/M18/revision_r2.json`.
- Every negative case runs against a fresh in-memory `deepcopy`, so a failure cannot contaminate a later
  case, and no case can be rejected by a JSON parser instead of by the model.
- `recovery/wheels_probe/` is where the offline pytest probe tried to write (unit
  `A0b-pytest-offline-availability`, raw rc 1 — no local wheel; recorded, not worked around).

This card performs no PDF extraction and no network access, so there is no external input to protect.
