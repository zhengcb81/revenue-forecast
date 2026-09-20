"""Post-hoc design probe: what the contract does with a negative signed/optional driver.

This is NOT part of the frozen case set and NOT the formula oracle. It exists because one
frozen M13 observation (OBS-SIGNED-PERF-FEE, base=defaults) could not be built as specified -
the driver is absent from the defaults base, so the observation raised KeyError instead of
recording a contract fact. The frozen fixtures are deliberately NOT rewritten to hide that
(see the r2 section of oracle.md and review.md); the factual question is answered here, in a
separate, clearly labelled probe whose inputs are recorded verbatim.

The probe calls the same single product entry point as the runner
(``model_registry.calculate_registered_model``) on a deepcopy of the frozen positive input,
with the card's most negative-capable optional driver set to the probe value.

Writes ``recovery/probes/signed_driver_probe.json``. Prints ASCII only.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time


def bound_value(raw):
    """The enumeration writes non-finite bounds as the strings 'inf'/'-inf' (JSON has no
    infinity literal), so accept both the string and the float form."""
    if isinstance(raw, str):
        return float(raw)
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--probe-value", type=float, default=-100.0)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", card)
    out_dir = os.path.join(attempt, "recovery", "probes")
    os.makedirs(out_dir, exist_ok=True)

    enum = json.load(open(os.path.join(evidence, "oq_enumeration.json"), "r", encoding="utf-8"))
    input_doc = json.load(open(os.path.join(evidence, "input.json"), "r", encoding="utf-8"))
    model_id = enum["model_id"]
    optional = enum["card_model"]["optional"]
    effective = enum["card_model"]["effective_bounds"]

    signed_unbounded = [d for d in optional
                        if bound_value(effective[d][0]) == float("-inf")
                        and bound_value(effective[d][1]) == float("inf")]
    if signed_unbounded:
        target = signed_unbounded[0]
        target_reason = "optional driver whose effective bounds are (-inf, inf): a legitimate " \
                        "negative (reversal/clawback) is admitted by the driver guard"
    else:
        target = optional[0]
        target_reason = "no optional driver of this model is signed/unbounded, so the first " \
                        "optional driver is probed instead; a negative value is then expected " \
                        "to be refused by the driver bound itself"

    spec = copy.deepcopy(input_doc["positive"])
    spec["drivers"][target] = [args.probe_value]

    sys.path.insert(0, args.code_root)
    import model_registry  # noqa: E402

    outcome = {"raised": None, "actual": None, "message": None}
    try:
        value = model_registry.calculate_registered_model(
            model_id=spec["model_id"], base_revenue=spec["base_revenue"],
            drivers=spec["drivers"], years=spec["years"])
        outcome["actual"] = [float(v) for v in value]
    except Exception as exc:  # noqa: BLE001
        outcome["raised"] = type(exc).__name__
        outcome["message"] = str(exc).encode("ascii", "backslashreplace").decode("ascii")

    doc = {
        "card_id": card,
        "model_id": model_id,
        "purpose": "post-hoc design probe (NOT a frozen case, NOT the oracle): records the "
                   "contract behaviour for a negative optional driver",
        "base_input": "evidence/%s/input.json:positive (deepcopy)" % card,
        "driver_probed": target,
        "why_this_driver": target_reason,
        "probe_value": args.probe_value,
        "probe_input_drivers": spec["drivers"],
        "outcome": outcome,
        "interpretation": ("the signed driver passed the guard and the row was refused later by "
                           "the non-negative-revenue check"
                           if outcome["raised"] == "ModelRegistryError"
                           and "cannot be negative" in (outcome["message"] or "")
                           else ("the driver guard refused the negative value outright"
                                 if outcome["raised"] == "ModelRegistryError"
                                 else "the negative value was accepted and produced a value")),
        "enumeration_source": "evidence/%s/oq_enumeration.json" % card,
        "product_call": "model_registry.calculate_registered_model(model_id, base_revenue, "
                        "drivers, years) - the same single entry point as the runner",
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(out_dir, "signed_driver_probe.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=True, indent=1)
        handle.write("\n")
    print("probe driver %s value %s -> raised=%s actual=%s"
          % (target, args.probe_value, outcome["raised"], outcome["actual"]))
    print("interpretation: %s" % doc["interpretation"])
    print("wrote %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
