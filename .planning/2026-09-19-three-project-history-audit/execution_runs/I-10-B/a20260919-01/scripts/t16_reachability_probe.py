#!/usr/bin/env python3
"""T1-6 reachability probe — which guard does each candidate patch reach?

T1-6 asks for a NEW case whose input DIFFERS from the existing CONT-BREAK and
which reaches the FY2027 *own-balance* guard ("stock-flow balance failed:
FY2027"), not the FY2028 cross-year anchoring guard.

This script runs every candidate patch against the registry and prints the
EXACT refusal message, so the claim "the value is reachable" is measured, not
asserted. It also re-derives what the CARD's own negative_patch actually does,
because that turns out to be a different guard.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent
ISO = RUN / "iso" / "rf" / "scripts"

sys.path.insert(0, str(ISO))
_spec = importlib.util.spec_from_file_location("mr_t16", ISO / "model_registry.py")
m = importlib.util.module_from_spec(_spec)
sys.modules["mr_t16"] = m
_spec.loader.exec_module(m)

MODEL = "subscription_arr_bridge"
YEARS = [2027, 2028]

# M24 continuity_positive drivers, verbatim from evidence/M24/input.json
BASE = {
    "opening_arr": [200, 250],
    "gross_retention_rate": [0.9, 1],
    "expansion_arr": [30, 0],
    "new_arr": [40, 0],
    "closing_arr": [250, 250],
    "lost_arr_revenue_fraction": [0.75, 0.75],
    "expansion_revenue_fraction": [0.5, 0.5],
    "new_arr_revenue_fraction": [0.25, 0.25],
    "usage_revenue": [5, 0],
}


def run(patch: dict, label: str) -> dict:
    d = json.loads(json.dumps(BASE))
    d.update(patch)
    try:
        out = m.calculate_registered_model(MODEL, 0, d, list(YEARS))
        rec = {"label": label, "outcome": "ok", "value": out,
               "opening_arr": d["opening_arr"], "closing_arr": d["closing_arr"]}
    except Exception as e:  # noqa: BLE001
        rec = {"label": label, "outcome": "raised", "exc": type(e).__name__,
               "message": str(e),
               "opening_arr": d["opening_arr"], "closing_arr": d["closing_arr"]}
    print(f"  {label}")
    print(f"      opening={rec['opening_arr']} closing={rec['closing_arr']}")
    if rec["outcome"] == "ok":
        print(f"      -> ok {rec['value']}")
    else:
        print(f"      -> {rec['exc']}: {rec['message']}")
    return rec


def main() -> int:
    out = {"model": MODEL, "years": YEARS, "probes": []}

    print("=== (0) unbroken positive (control) ===")
    out["probes"].append(run({}, "control: continuity_positive unbroken"))

    print()
    print("=== (1) CURRENT cases.json CONT-BREAK ===")
    out["probes"].append(run(
        {"opening_arr": [200, 251], "closing_arr": [250, 251]},
        "current CONT-BREAK (opening[200,251], closing[250,251])"))

    print()
    print("=== (2) T1-6 reviewer-given value ===")
    out["probes"].append(run(
        {"opening_arr": [200, 250], "closing_arr": [251, 251]},
        "T1-6 value (opening[200,250], closing[251,251])"))

    print()
    print("=== (3) card_M24.md negative_patch, byte-for-byte ===")
    out["probes"].append(run(
        {"opening_arr": [200, 251], "closing_arr": [250, 251]},
        "card_M24.md negative_patch (same as current)"))

    # classify
    def msg_of(i):
        p = out["probes"][i]
        return p.get("message", "")

    out["classification"] = {
        "control_is_ok": out["probes"][0]["outcome"] == "ok",
        "current_reaches_continuity_FY2028": "continuity failed: FY2028" in msg_of(1),
        "t16_reaches_balance_FY2027": "stock-flow balance failed: FY2027" in msg_of(2),
        "card_patch_equals_current": (
            out["probes"][1]["opening_arr"] == out["probes"][3]["opening_arr"]
            and out["probes"][1]["closing_arr"] == out["probes"][3]["closing_arr"]
        ),
        "t16_input_differs_from_current": (
            out["probes"][1]["opening_arr"] != out["probes"][2]["opening_arr"]
            or out["probes"][1]["closing_arr"] != out["probes"][2]["closing_arr"]
        ),
    }
    print()
    print("CLASSIFICATION:", json.dumps(out["classification"], ensure_ascii=False, indent=1))

    (RUN / "t16_reachability_probe.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
