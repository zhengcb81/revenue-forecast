# M06 recovery note

**not_applicable_with_reason.** `usage_platform` is a pure in-process function:
`calculate_registered_model` has no durable state, no lock, no lease, no partial publication and no
filesystem side effect. A raised `ModelRegistryError` leaves nothing to roll back, so there is no
restart/retry path to exercise.

What IS covered instead:

- the exit-code self-check (`recovery/selfcheck_result.json` in the M05 attempt) proves the runner's exit
  code carries the verdict and that a corrupted copy cannot pass;
- every negative case is run against a fresh `deepcopy`, so failures cannot contaminate later cases;
- the frozen evidence was hash-verified after the self-check to prove the scratch runs did not touch it.

The only non-pure step in this card is read-only PDF extraction, whose input (the company-wiki PDFs) is never
written to.
