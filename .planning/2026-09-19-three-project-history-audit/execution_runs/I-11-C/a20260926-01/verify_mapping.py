#!/usr/bin/env python3
"""verify_mapping.py — I-11-C/a20260926-01 invariant checker (read-only).

Usage: python verify_mapping.py [mapping.json] [handoff.json] [eas.json] [store.json]
Defaults: this attempt's parameter_mapping.json / handoff.json,
          I-11-B expert_assumptions.json (read-only), OPEN2-C2 store hypotheses_v3.json (read-only).
rc=0 iff all invariants hold; rc=1 otherwise (one VIOLATION line each).

Invariants (frozen in oracle.md §4.3):
  J1 release lock      — no value_state claims release; handoff params_released=false,
                         implementer_signed=false, releases_nothing=true, status=review_pending;
                         unmapped/blocked rows must carry an all-null low/base/high triple.
  J2 synthetic + EA    — no quarantined synthetic number appears as a numeric low/base/high value;
                         every row's ea_refs must resolve to an I-11-B EA that still carries a
                         non-empty sensitivity_interval and equivalent_to_disclosure_basis==false.
  J3 store lock        — store side read-only: all low/base/high null, _PLACEHOLDER ids present.
  J4 residual lock     — C3/C5 registrations stay open-form (unverified/...); 'resolved' forbidden.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANNING = HERE.parents[1]
EAS_DEFAULT = PLANNING / "I-11-B" / "a20260926-01" / "expert_assumptions.json"
STORE_DEFAULT = PLANNING / "OPEN2-C2-REGISTRATION" / "a20260926-01" / "hypotheses_v3.json"

QUARANTINE = {2, 8760, 0.5, 0.6, 0.7, 40, 20, 30, 32, 34, 1200,
              264000, 281520, 299040, 17520}
ALLOWED_VALUE_STATES = {"mapped_not_released", "not_executable_no_propagation",
                        "unmapped_declined_no_number"}
ALLOWED_RESIDUAL = {"unverified", "expert_assumption", "verified_by_parent",
                    "erratum_recorded", "parent_erratum"}
PLACEHOLDER_IDS = ("ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER",
                   "MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER")


def load(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def walk(o, key):
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                out.append(v)
            else:
                out.extend(walk(v, key))
    elif isinstance(o, list):
        for it in o:
            out.extend(walk(it, key))
    return out


def main(argv):
    map_p = Path(argv[1]) if len(argv) > 1 else HERE / "parameter_mapping.json"
    hand_p = Path(argv[2]) if len(argv) > 2 else HERE / "handoff.json"
    eas_p = Path(argv[3]) if len(argv) > 3 else EAS_DEFAULT
    store_p = Path(argv[4]) if len(argv) > 4 else STORE_DEFAULT

    v = []
    mapping = load(map_p)
    eas = {a["id"]: a for a in load(eas_p).get("assumptions", [])}

    # J1 release lock
    for row in mapping.get("mapping_rows", []):
        st = row.get("value_state", "")
        if st not in ALLOWED_VALUE_STATES:
            v.append(f"J1 violated: {row.get('parameter_id')} value_state={st!r}")
        elif st == "released" or st.startswith("released_"):
            v.append(f"J1 violated: {row.get('parameter_id')} claims release")
        if st in ("not_executable_no_propagation", "unmapped_declined_no_number"):
            nv = row.get("new_value", {})
            tri = [nv.get(k) for k in ("low", "base", "high")]
            if tri != [None, None, None]:
                v.append(f"J1 violated: {row.get('parameter_id')} unmapped/blocked but "
                         f"new_value not all-null (propagation of numbers forbidden)")
    if hand_p.exists():
        h = load(hand_p)
        if h.get("params_released") is not False:
            v.append("J1 violated: handoff.params_released != false")
        if h.get("implementer_signed") is not False:
            v.append("J1 violated: handoff.implementer_signed != false")
        if h.get("releases_nothing") is not True:
            v.append("J1 violated: handoff.releases_nothing != true")
        if h.get("status") != "review_pending":
            v.append(f"J1 violated: handoff.status={h.get('status')!r} != review_pending")
        # J4 residual lock
        for r in h.get("c3_c5_residuals", []):
            reg = r.get("registration")
            if reg not in ALLOWED_RESIDUAL:
                v.append(f"J4 violated: residual {r.get('id')} registration={reg!r}")
    # J4 also guards the mapping-side residual findings
    for r in mapping.get("unverified_findings", []):
        reg = r.get("registration")
        if reg not in ALLOWED_RESIDUAL:
            v.append(f"J4 violated: finding {r.get('id')} registration={reg!r}")

    # J2 synthetic quarantine (numeric low/base/high only) + EA integrity
    for row in mapping.get("mapping_rows", []):
        nv = row.get("new_value", {})
        for k in ("low", "base", "high"):
            val = nv.get(k)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if float(val) in {float(q) for q in QUARANTINE}:
                    v.append(f"J2 violated: {row.get('parameter_id')}.{k}={val} "
                             f"is a quarantined synthetic number")
        for ref in row.get("source", {}).get("ea_refs", []):
            a = eas.get(ref)
            if a is None:
                v.append(f"J2 violated: {row.get('parameter_id')} references unknown EA {ref!r}")
                continue
            si = a.get("sensitivity_interval")
            if not isinstance(si, dict) or not si:
                v.append(f"J2 violated: {row.get('parameter_id')} relies on {ref} "
                         f"which has no sensitivity_interval (EA template broken)")
            if a.get("equivalent_to_disclosure_basis") is not False:
                v.append(f"J2 violated: {row.get('parameter_id')} relies on {ref} "
                         f"with equivalent_to_disclosure_basis != false")

    # J3 store lock (read-only)
    store = load(store_p)
    txt = json.dumps(store, ensure_ascii=False)
    for pid in PLACEHOLDER_IDS:
        if pid not in txt:
            v.append(f"J3 violated: store missing {pid}")
    for key in ("low", "base", "high"):
        vals = walk(store, key)
        if not vals:
            v.append(f"J3 violated: store has no {key!r} fields (schema drift)")
        for val in vals:
            if val is not None:
                v.append(f"J3 violated: store {key} != null (got {val!r}) — release detected")

    if v:
        for line in v:
            print("VIOLATION:", line)
        return 1
    print("ALL_INVARIANTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
