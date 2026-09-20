# M02 · decision record — not NA

Card step D is `[professional_decision_required]`, so this file is **required** and is not marked NA
(unlike a purely mechanical card). It is intentionally **not duplicated** here:

- The full record is `evidence/M02/accounting_decision.md`, containing four recorded decisions
  (DEC-M02-1 revenue definition, DEC-M02-2 whether a constructive identity can satisfy the reconciliation
  requirement, DEC-M02-3 whether an ignored `base_revenue` must still be domain-checked, DEC-M02-4
  unidentifiable parameters), one observation, and two special-review flags (SR-M02-A/B).
- Steps E/F are **not implemented**: E belongs to I-10-A (it needs `calculate_model_path` wiring that this
  attempt only inspected read-only, see `evidence/M02/forecast_integration.json`), and F requires the I-12
  frozen design, which does not exist.

**Status of every decision in the record: PROPOSED, NOT APPROVED.** A named industry/accounting reviewer
must sign, reject or amend each one. The implementer does not sign, and nothing here may be read as
`disclosure_adaptation` granted.
