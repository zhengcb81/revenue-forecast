#!/usr/bin/env python3
"""verify_plan.py — I-11-B/a20260926-01 invariant checker (read-only).

Usage: python verify_plan.py [plan.json] [eas.json] [handoff.json] [store.json]
Defaults to this attempt's files and the sealed hypotheses_v3.json (read-only).
Exit rc=0 iff all invariants hold; rc=1 otherwise (one line per violation).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE_DEFAULT = HERE.parents[1] / "OPEN2-C2-REGISTRATION" / "a20260926-01" / "hypotheses_v3.json"


def load(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def main(argv):
    plan_p = Path(argv[1]) if len(argv) > 1 else HERE / "calibration_plan.json"
    eas_p = Path(argv[2]) if len(argv) > 2 else HERE / "expert_assumptions.json"
    handoff_p = Path(argv[3]) if len(argv) > 3 else HERE / "handoff.json"
    store_p = Path(argv[4]) if len(argv) > 4 else STORE_DEFAULT

    v = []
    plan = load(plan_p)
    eas = load(eas_p)

    # I1: every expert assumption has sensitivity_interval + equivalent_to_disclosure_basis=false
    for a in eas.get("assumptions", []):
        si = a.get("sensitivity_interval")
        if not isinstance(si, dict) or not si:
            v.append(f"I1 violated: {a.get('id')} missing sensitivity_interval")
        if a.get("equivalent_to_disclosure_basis") is not False:
            v.append(f"I1 violated: {a.get('id')} equivalent_to_disclosure_basis != false")

    # I2: proposed values never claim release; declined slots must hold null values
    for p in plan.get("parameters", []):
        nv = p.get("action2_parameter_mapping", {}).get("new_value", {})
        st = p.get("action2_parameter_mapping", {}).get("value_state", "")
        if st.startswith("declined"):
            flat = json.dumps(nv)
            if flat not in ('{"low": null, "base": null, "high": null}',):
                if '"low": null' not in flat or '"base": null' not in flat:
                    v.append(f"I2 violated: {p.get('parameter_id')} declined but new_value not all-null")
        if st == "released":
            v.append(f"I2 violated: {p.get('parameter_id')} value_state=released")

    # I3: management target never independent accuracy evidence
    if plan.get("value_policy", {}).get("management_target_is_not_independent") is not True:
        v.append("I3 violated: management_target_is_not_independent != true")

    # I4: store side untouched — every low/base/high null and _PLACEHOLDER ids present
    store = load(store_p)
    txt = json.dumps(store, ensure_ascii=False)
    for pid in ("ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER",
                "MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER"):
        if pid not in txt:
            v.append(f"I4 violated: store missing {pid}")

    def walk(o, key):
        out = []
        if isinstance(o, dict):
            for k, val in o.items():
                if k == key:
                    out.append(val)
                else:
                    out.extend(walk(val, key))
        elif isinstance(o, list):
            for it in o:
                out.extend(walk(it, key))
        return out

    for key in ("low", "base", "high"):
        vals = walk(store, key)
        if not vals:
            v.append(f"I4 violated: store has no '{key}' fields (schema drift)")
        for val in vals:
            if val is not None:
                v.append(f"I4 violated: store {key} != null (got {val!r}) — release detected")

    # I5: handoff invariants (if present)
    if handoff_p.exists():
        h = load(handoff_p)
        if h.get("params_released") is not False:
            v.append("I5 violated: handoff.params_released != false")
        if h.get("implementer_signed") is not False:
            v.append("I5 violated: handoff.implementer_signed != false")
        if h.get("releases_nothing") is not True:
            v.append("I5 violated: handoff.releases_nothing != true")
        allowed = {"unverified", "expert_assumption", "verified_by_parent",
                   "erratum_recorded", "parent_erratum"}
        for r in h.get("c3_c5_residuals", []):
            st = r.get("registration")
            if st not in allowed:
                v.append(f"I5 violated: residual {r.get('id')} registration={st!r} (must stay open-form)")

    if v:
        for line in v:
            print("VIOLATION:", line)
        return 1
    print("ALL_INVARIANTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
