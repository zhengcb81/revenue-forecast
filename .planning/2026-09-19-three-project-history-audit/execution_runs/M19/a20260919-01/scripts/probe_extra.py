"""Extra boundary probes: measured, NON-GATING observations of the documented domains.

These probes are deliberately NOT part of the frozen oracle and NOT part of the runner's
exit code.  They exist because the enumeration (scripts/enumerate_registry.py) reports the
effective bounds, and a bound is only a claim until a value at or beyond it is actually
fed to the calculator.

Each probe states its expectation BEFORE the call, computed by plain arithmetic in this
file (never by the product), and records whether the measured value matched.

Writes <attempt>/evidence/<CARD>/extra_probes.json.  The frozen evidence is read only.

Usage:
  python -X utf8 -B probe_extra.py --card M17 --attempt-root <attempt> --code-root <iso>
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import traceback

# expectation_source documents WHERE the pre-registered expectation comes from.
PROBES = {
    "M17": [
        {"id": "PROBE-NEG-MILESTONE",
         "why": ("the enumeration reports milestone_revenue's effective bounds as (-inf, inf) because "
                 "it is a signed driver, while card_M17.md L8 calls the other licensing items "
                 "'confirmed amounts'; this probe measures whether a small NEGATIVE confirmed amount "
                 "is accepted. The patch REPLACES milestone_revenue, so the arithmetic is "
                 "40 x 2 + (-5) + 5 + 10 = 90"),
         "patch": {"milestone_revenue": [-5]},
         "expectation_source": "signed-driver bounds from the enumeration",
         "expected_if_signed": 90.0,
         "expected_if_non_negative": "ModelRegistryError"},
        {"id": "PROBE-NEG-TOTAL-REVENUE",
         "why": ("probes the only negative guard in calculate_registered_model: the TOTAL revenue "
                 "must not be negative, even though individual components may be"),
         "patch": {"milestone_revenue": [-200]},
         "expectation_source": "calculated revenue cannot be negative",
         "expected_if_signed": "ModelRegistryError",
         "expected_if_non_negative": "ModelRegistryError"},
    ],
    "M18": [
        {"id": "PROBE-FILL-EXACT-1",
         "why": ("the ratio domain [0,1] must be inclusive at its upper edge for fill_rate; expected "
                 "1000000 / 1000 x 1.0 x 10 + 100 = 10100"),
         "patch": {"fill_rate": [1.0]},
         "expectation_source": "inclusive upper edge of the ratio domain",
         "expected_if_inclusive": 10100.0,
         "expected_if_exclusive": "ModelRegistryError"},
    ],
    "M19": [
        {"id": "PROBE-ACTIVE-ZERO",
         "why": ("the quantity domain starts at 0; expected 0 x 0.05 x 20 + 10 = 10"),
         "patch": {"active_users": [0]},
         "expectation_source": "inclusive lower edge of the quantity domain",
         "expected_if_inclusive": 10.0,
         "expected_if_exclusive": "ModelRegistryError"},
    ],
    "M20": [
        {"id": "PROBE-TIMING-ZERO",
         "why": ("timing_factor = 0 is the lower edge of the ratio domain declared for this model; "
                 "expected 95 x 2 x 0 + 5 = 5"),
         "patch": {"timing_factor": [0.0]},
         "expectation_source": "inclusive lower edge of the ratio domain",
         "expected_if_inclusive": 5.0,
         "expected_if_exclusive": "ModelRegistryError"},
        {"id": "PROBE-CONTINUITY-TOLERANCE-BAND-INSIDE",
         "why": ("the cross-year continuity and intra-year bridge checks use "
                 "math.isclose(rel_tol=1e-9, abs_tol=1e-9), so the admissible imbalance is "
                 "delta <= max(1e-9 * max(|a|,|b|), 1e-9); at the 120-customer magnitude that is about "
                 "1.2e-7 customers, NOT the 1e-12 that the first draft of this probe implied. This "
                 "probe feeds delta = 1.2e-7 (inside the band): the run must be ACCEPTED and the "
                 "year-2 revenue must be 2 x 120.00000012 = 240.00000024"),
         "base_input": "continuity_positive",
         "patch": {"opening_customers": [100, 120.00000012], "ending_customers": [120, 120.00000012]},
         "expectation_source": "math.isclose(rel_tol=1e-9, abs_tol=1e-9) evaluated at magnitude 120",
         "expected_if_tolerant": "accepted",
         "expected_if_exact": "ModelRegistryError"},
        {"id": "PROBE-CONTINUITY-TOLERANCE-BAND-OUTSIDE",
         "base_input": "continuity_positive",
         "why": ("the other side of the same band: delta = 1.201e-7 exceeds "
                 "1e-9 * 120.0000001201 = 1.2000000012e-7, so the cross-year continuity check must "
                 "REJECT with 'cohort customer continuity failed: FY2028' - the same failure mode as "
                 "the frozen CONT-BREAK case, only six orders of magnitude smaller"),
         "patch": {"opening_customers": [100, 120.0000001201],
                   "ending_customers": [120, 120.0000001201]},
         "expectation_source": "math.isclose(rel_tol=1e-9, abs_tol=1e-9) evaluated at magnitude 120",
         "expected_if_tolerant": "ModelRegistryError",
         "expected_if_exact": "ModelRegistryError"},
    ],
}

CARDS = {
    "M17": "licensing_commercial",
    "M18": "advertising",
    "M19": "gaming",
    "M20": "cohort_subscription",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--code-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    with open(os.path.join(evidence, "input.json"), "r", encoding="utf-8") as handle:
        input_doc = json.load(handle)

    sys.path.insert(0, os.path.abspath(args.code_root))
    import model_registry  # noqa: E402

    results = []
    for probe in PROBES[card]:
        spec = copy.deepcopy(input_doc[probe.get("base_input", "positive")])
        for driver, values in probe["patch"].items():
            spec["drivers"][driver] = copy.deepcopy(values)
        entry = {k: v for k, v in probe.items() if k not in ("patch", "base_input")}
        entry["base_input"] = probe.get("base_input", "positive")
        entry["patch"] = probe["patch"]
        entry["mutated_input_repr"] = (repr(spec["drivers"])[:400] + " years=" + repr(spec["years"]))
        try:
            value = model_registry.calculate_registered_model(
                model_id=spec["model_id"], base_revenue=spec["base_revenue"],
                drivers=spec["drivers"], years=spec["years"])
            entry["raised"] = None
            entry["actual"] = [float(v) for v in value]
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
        if entry["raised"] is None:
            for key, expected in probe.items():
                if key.startswith("expected_if_") and isinstance(expected, (int, float)):
                    entry["matches_" + key] = (
                        len(entry["actual"]) == 1 and abs(entry["actual"][0] - expected) <= 1e-9)
        results.append(entry)

    doc = {
        "card_id": card,
        "model_id": CARDS[card],
        "gating": False,
        "purpose": ("measured boundary observations of the documented domains; they are NOT part of "
                    "the frozen oracle and NOT part of the runner's exit code"),
        "expectation_rule": ("each expectation is computed by plain arithmetic in this file before the "
                             "call and never taken from the product"),
        "code_root": os.path.abspath(args.code_root),
        "probes": results,
    }
    out = os.path.join(evidence, "extra_probes.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    for entry in results:
        print("probe", entry["id"], "raised=", entry["raised"], "actual=", entry.get("actual"),
              {k: v for k, v in entry.items() if k.startswith("matches_")})
    print("written", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
