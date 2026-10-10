# P7-RF M3 independent review (agent, read-only) — 2026-10-10

Scratch only under %TEMP%/p7-rf-review/verify_invariants.py; no repo file modified.

## Verdict

- INVARIANT A (unrelated scope/period cannot promote): PASS — all three mutations demote; FY2026 outputs drop out of magnitude support.
  - A.1 conversion obs scope="Unrelated Business Line" → unverified, reasons 3x `conversion_observation_unverified_scope:conversion_{low,base,high}:claim_parameter_conversion_{...}`, magnitude []
  - A.2 conversion obs period="FY2031" → unverified, reasons 3x `conversion_observation_unverified_period:...`, magnitude []
  - A.3 quantitative_reference obs + calibration scope = "Unrelated Product X" → unverified, reasons `calibration_scope_not_native_business:Unrelated Product X` + 3x `calibration_output_scope_mismatch:0_{low,base,high}_2026:Unrelated Product X->Segment A`, magnitude []
- INVARIANT B (legal independent endpoint preserved): PASS — unmutated fixture referenced_range, reasons==[], magnitude={0_low_2026,0_base_2026,0_high_2026}; reference_upper binding_status=="unverified_scope" (parameter_scopes empty, never in revenue DAG) causes no demotion; cross-checked through run_forecast.
- API shape: PASS — keys exactly [schema_version research-adequacy/1, inventory, evidence_roles, calibrations, documentary_presence, mechanism_adequacy, magnitude_adequacy, inventory_counts, limitations]; operating_research absent → None.

## Extra adversarial probes (all correct)

1. Unbinding only the `base` conversion alone demotes with a reason naming exactly that parameter/claim (per-conversion, not all-or-nothing).
2. Conversion observations scoped to the company name "Test Co" stay referenced_range with reasons==[] (legal company-wide scope).
3. A sibling segment that exists ("Segment B") but does not consume the parameters is rejected — binding follows actual parameter flow, not any known segment name.

Existing tests/test_research_evidence_roles.py: 11/11 passed under reviewer environment. Fix reviewed at scripts/research/evidence_roles.py::_calibration (consuming binding_status via observation_binding, scripts/research/native_dependencies.py).
