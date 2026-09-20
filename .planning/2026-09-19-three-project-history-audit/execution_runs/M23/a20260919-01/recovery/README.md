# M23 recovery note

**not_applicable_with_reason.** `insurance_service` is a pure in-process calculator:
`calculate_registered_model` has no durable state, no lock, no lease, no partial
publication and no filesystem side effect. A raised `ModelRegistryError` leaves
nothing to roll back, so there is no restart/retry path to exercise.

What IS covered instead:

- the exit-code mutation probe `recovery/selfcheck/selfcheck_result.json` proves the
  runner's exit code carries the verdict (0 pass / 2 no-verdict / 3 rejected-not-as-expected)
  and that a corrupted copy cannot pass;
- every negative case is run against a fresh `deepcopy`, so a failure cannot contaminate
  a later case;
- the frozen evidence was hash-verified before and after every probe to prove the scratch
  runs did not touch it;
- the card's cross-year guard, which is what replaces per-year durable state here, is
  exercised by a continuity positive plus a continuity-break negative.

Scratch layout (frozen evidence is never mutated; only these copies are):

```text
recovery/
  README.md
  selfcheck_result.json          # mutation probe report (this card)
  oracle_body_hash.json          # frozen-body byte hash of oracle.md + mtime ordering
  oq_enum_stdout.txt             # raw stdout of the read-only registry enumeration
  oq_enum_stderr.txt             # 0 bytes
  selfcheck/
    scripts/run_card.py          # copy of the shared runner
    evidence/M23/{input,oracle,cases}.json   # copies that ARE mutated by the probe
    run_result_*.json            # one run result per probe tag
    stdout_*.txt stderr_*.txt    # raw outputs per probe tag
```
