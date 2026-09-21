{
  "oracle_id": "I-10-B-a20260919-01",
  "card_id": "I-10-B",
  "attempt_id": "a20260919-01",
  "authority": "OWNER_DECISIONS.md section 13 T1-22 (authorises the card for BOTH defects on one card)",
  "nature": "INDEPENDENT EXPECTATION — frozen BEFORE the fix. Expected values are hand-derived from the card text and the measured baseline, NOT produced by calling the fixed function.",
  "code_root_anchors": {
    "rf_scripts_model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "rf_scripts_model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
    "note": "both recomputed at attempt open and required to match; a mismatch stops the attempt"
  },

  "baseline_measurement_at_freeze": {
    "models_total": 31,
    "optional_driver_without_explicit_default_slots": 31,
    "models_affected": 24,
    "note": "31 slots / 24 models — measured, and it matches the figure the card states exactly",
    "slots_by_driver": {
      "other_revenue": 14, "usage_revenue": 3, "milestone_revenue": 2,
      "service_revenue": 2, "fixed_revenue": 1, "backlog_remeasurements": 1,
      "reserve_revisions": 1, "performance_fee_revenue": 1,
      "franchise_system_sales": 1, "recognized_fee_rate": 1,
      "supply_revenue": 1, "ancillary_revenue": 1, "royalty_revenue": 1,
      "recognized_performance_fees": 1
    }
  },

  "defect_1_silent_zero": {
    "site": "scripts/model_registry.py:335",
    "current": "values = drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))",
    "problem": "an optional driver with NO explicit default is silently filled with 0.0, encoding 'absent' and 'not found' as the SAME input",
    "chosen_fix": "raise ModelRegistryError when the driver is absent AND spec.defaults has no explicit entry",
    "rejected_alternative": "supply an EXPLICIT 0.0 instead of an implicit one — rejected by the card (point 1) because it still cannot distinguish 'not found' from 'absent'",
    "cases": [
      {
        "id": "R-B1-N1",
        "kind": "negative",
        "case": "a model with an optional driver that has no explicit default, driver omitted",
        "expected": {"raises": "ModelRegistryError"},
        "note": "must FAIL on the unfixed baseline (baseline returns a result with an implicit 0.0)"
      },
      {
        "id": "R-B1-P1",
        "kind": "positive",
        "case": "the SAME model with a default-bearing optional driver omitted",
        "expected": {"raises": null, "uses_declared_default": true},
        "note": "omission remains legal ONLY where spec.defaults carries an explicit value; the declared default must be the value used"
      },
      {
        "id": "R-B1-N3",
        "kind": "negative",
        "case": "driver explicitly supplied with the value the old code would have injected (0.0)",
        "expected": {"raises": null, "accepted_explicit_zero": true},
        "note": "explicit 0.0 must still be ACCEPTED — the fix forbids IMPLICIT filling, it does not forbid the value 0"
      }
    ]
  },

  "defect_2_sign_name_based": {
    "site": "scripts/model_registry.py:265",
    "current": "_SIGNED_DRIVERS = frozenset({contract_changes, other_revenue, fixed_revenue, ancillary_revenue, milestone_revenue, royalty_revenue, service_revenue, performance_fee_revenue, fee_revenue})",
    "problem": "sign is decided by hard-coded NAME membership. other_revenue is signed while usage_revenue (same dimension, revenue) is not; franchise_system_sales / supply_revenue are revenue-role and arguably reversal-capable yet sit in [0, inf).",
    "measured_proof_that_name_membership_is_arbitrary": [
      "recognized_performance_fees is NOT in _SIGNED_DRIVERS yet reaches (-inf, inf) — via driver_bounds metadata, not the set",
      "reserve_revisions is NOT in _SIGNED_DRIVERS yet reaches (-inf, inf) — likewise",
      "backlog_remeasurements is NOT in _SIGNED_DRIVERS yet reaches (-inf, inf) — likewise"
    ],
    "chosen_fix": "decide sign by SEMANTIC ROLE derived from declared metadata (dimension + an explicit reversal-capable role bit), never by driver name",
    "cases": [
      {
        "id": "R-B2-N1",
        "kind": "negative",
        "case": "franchise_system_sales supplied negative",
        "expected": {"accepted": true, "bounds": "(-inf, inf)"},
        "note": "semantic role is reversal-capable revenue; a negative must be ACCEPTED"
      },
      {
        "id": "R-B2-N2",
        "kind": "negative",
        "case": "a driver whose name is not in ANY role table",
        "expected": {"must_not_gain_guessed_sign": true},
        "note": "an unlisted new driver must NOT silently acquire a sign by name guessing"
      },
      {
        "id": "R-B2-P1",
        "kind": "positive",
        "case": "a genuine quantity driver (e.g. closing_stores) supplied negative",
        "expected": {"raises": "ModelRegistryError"},
        "note": "widening signedness must NOT leak into quantities: the semantic rule must keep [0, inf) here"
      },
      {
        "id": "R-B2-P2",
        "kind": "positive",
        "case": "a genuine ratio driver",
        "expected": {"bounds_still_enforced": true}
      }
    ],
    "compatibility_requirement": "every one of the 25 existing drivers whose bounds CHANGE must be listed individually, each with which M-card case is affected. Historical expectations are corrected ADDITIVELY only (T1-12); freeze-bodies are never rewritten."
  },

  "boundaries": {
    "does_not_touch_M01_to_M31_formulas": true,
    "does_not_touch_frozen_evidence": true,
    "iso_only": true,
    "no_product_merge": true,
    "disclosure_adaptation": "unmapped",
    "accuracy": "unproven"
  }
}
