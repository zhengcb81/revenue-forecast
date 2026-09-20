# recovery - not applicable

Card M04 is a **pure function** card: it calls `calculate_registered_model(model_id, base_revenue,
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
