# M10 recovery note

**not_applicable_with_reason for stateful recovery.** `reserve_depletion` is a pure in-process function:
`calculate_registered_model` has no durable state, no lock, no lease, no partial publication and no
filesystem side effect. A raised `ModelRegistryError` leaves nothing to roll back, so there is no
restart/retry path to exercise.

What IS covered instead:

- `recovery/selfcheck_result.json` proves the runner's exit code carries the verdict and that a corrupted
  expectation cannot pass (cases A and D -> rc 2, cases B and C -> rc 3, control E -> rc 0);
- every negative case and every observation runs against a fresh `deepcopy`, so a failure cannot
  contaminate a later case;
- the frozen evidence and the code under test were hash-verified after the self-check to prove the scratch
  runs did not touch them (`frozen_evidence_not_modified`,
  `product_code_under_test.unchanged`);
- `recovery/regenerate/` holds a second, byte-identical generation of the frozen expectations, which is the
  restore path for the oracle: the frozen `oracle.json` can be rebuilt from
  `scripts/oracle_cards_M09_M12.py` with no residual state.

The only non-pure step in this card is reading the frozen evidence files; nothing under a production
repository was written by any command of this attempt.
