# M27 recovery note

**STOP_BRIDGE is not_applicable_with_reason; the formula layer has no recovery path.**

`renewable_generation` is a per-year flow model: it has no `EXTENSION_OPENING_BALANCES` entry, no opening/closing stock and no bridge assertion, so the STOP_BRIDGE continuity check does not apply. `calculate_registered_model` is a pure in-process function with no durable state, no lock, no lease, no partial publication and no filesystem side effect, so a raised `ModelRegistryError` leaves nothing to roll back.

What IS covered instead:

- the applicable continuity check is the cross-year fiscal-year one (the card gives no two-year example): `CONT-BREAK` uses `years=[2027, 2029]` and must be refused;
- the exit-code self-check under `recovery/selfcheck/` proves the runner's exit code carries the verdict: cases A / B / D go red (rc=3) and the restored control C is green (rc=0);
- every negative case runs against a fresh `deepcopy`, so failures cannot contaminate later cases;
- the frozen evidence was hash-verified after the scratch runs to prove they did not touch it.
