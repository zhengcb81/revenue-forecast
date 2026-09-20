# M28 recovery note

**not_applicable_with_reason for the formula layer; the BRIDGE layer IS covered.**

`aum_fee_bridge` is a pure in-process function: `calculate_registered_model` has no durable state, no lock, no lease, no partial publication and no filesystem side effect. A raised `ModelRegistryError` leaves nothing to roll back, so there is no restart/retry path to exercise.

What IS covered instead:

- the stock-flow bridge and the cross-year continuity identity are exercised explicitly (`CONT-BREAK` breaks exactly the year-over-year opening = prior closing identity while keeping each year individually balanced);
- the exit-code self-check under `recovery/selfcheck/` proves the runner's exit code carries the verdict: cases A / B / D go red (rc=3) and the restored control C is green (rc=0);
- every negative case runs against a fresh `deepcopy`, so failures cannot contaminate later cases;
- the frozen evidence was hash-verified after the scratch runs to prove they did not touch it.

The only non-pure step in this card is reading the read-only product snapshot for the first time, which is never written to.
