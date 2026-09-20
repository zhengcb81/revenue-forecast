# recovery - not applicable

Card M03 is a **pure function** card: it calls `calculate_registered_model(model_id, base_revenue,
drivers, years)` in-process and writes only JSON/text evidence. There is no

* durable state, registry row, lock, lease, transaction or staging directory,
* process, worker, scheduler or network call,
* partially published artefact that could be left half-written.

`review_and_handoff.md` says "recovery/ # 异常后恢复；纯函数可说明NA", so recovery is recorded as
**not_applicable_with_reason** rather than filled with a manufactured crash case.

The nearest real failure that did occur was a **harness** defect (a wrong `base_input` key before the
first M01 product run), not a product-state failure. Its handling is recorded in
`evidence/M01/first_run_forensics.json` and in `review.md` (F-M01-01).

If a future revision makes this card stateful (e.g. it starts writing a catalog or publishing an
artefact), this NA no longer holds and a real crash/restart case becomes mandatory.

## PERMANENT provenance event: the frozen body of `oracle.md` WAS modified once

This is recorded permanently and **must not be rewritten as "never modified"**.

- **What happened:** the `NEW-1` fix (point-review follow-up) changed the *frozen body* of `oracle.md`
  inside `## 7. 披露映射`: the printed derived unit price on the mapping-1/mapping-2 lines went from
  `123,751.5203...` to `123,751.503987` (full precision). The pre-change file was
  `d0bed79bd868cda3dd2a0a7f3fcd45fca738f7a0f3fdd5c4abe16cb52a208764`; after the change it is
  `45f10b58008f6020a97243d92375927170c69502ef9e2c32986d973a236ab2f3` (both stated in the r3 note in
  `oracle.md`).
- **Why it was allowed:** the edited text was a *transcription typo in a derived unit price*, not a
  formula expectation, tolerance, negative-case count or disclosure figure. The frozen decision values
  (`[305]`, 13/13 negatives, the 2% tolerance, the 14.3667% gap) were not touched, and `oracle.json` has
  not changed since the first freeze. The implementer disclosed it in the same revision.
- **Consequence for how this card must be described:** for M03 the statement "the frozen expectations
  were not rewritten" is **NOT** available. The correct statement is:
  **"the frozen body was modified once, for a printed typo, and was self-disclosed."**
- **Why it is not reverted:** reverting would restore a value inconsistent with the printed result, and
  would hide a real provenance event. The append-only form was broken once; that fact is permanent.
