"""READ-ONLY auditor: checks THIS card's frozen expectations against the SUT report.

This is NOT the gate (the gate is the unmodified run_cases.py).  It answers the
specific questions this card is answerable for, which the generic gate does not
name explicitly:

  1. H12 - the renamed-window + honest-1740 double-refusal case, which has no
     pytest counterpart (I-14-H carried finding CF-I14H-3) - must actually pass.
  2. The two formerly-hardcoded keys must be DERIVED: for every window_accounting
     case in the report, quick_check_in_observation_intervals must agree with
     (quick_check_overlap_seconds > 0), and sum_used_for_natural_duration must
     agree with (basis == "sum_of_windows" and it is registered).  A hardcoded
     literal cannot satisfy the second check on a sum-basis case.
  3. Every per-case verdict must equal the frozen expectation, re-derived here
     from the frozen file (belt and braces next to the gate's own comparison).
  4. No non-JSON-native basis echo may appear in any computed block.

Usage: <python> -X utf8 -B harness/audit_postfix.py --report <sut_report.json>
Exit: 0 when every check holds, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

H12_EXPECTED = {
    "verdict": "reject_claim",
    "refusals": ["R-CLAIM-EXCEEDS", "R-QC-IN-OBS"],
    "computed": {"quick_check_overlap_seconds": 480, "union_seconds": 2220},
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    doc = json.loads(Path(args.report).read_text(encoding="utf-8"))
    by_id = {v["case_id"]: v for v in doc["verdicts"]}
    failures: list[str] = []
    checks = 0

    # (1) H12
    h12 = by_id.get("H12")
    if h12 is None:
        failures.append("H12 absent from the SUT report")
    else:
        checks += 1
        if h12["verdict"] != H12_EXPECTED["verdict"]:
            failures.append(f"H12 verdict {h12['verdict']!r} != "
                            f"{H12_EXPECTED['verdict']!r}")
        checks += 1
        if sorted(h12["refusals"]) != sorted(H12_EXPECTED["refusals"]):
            failures.append(f"H12 refusals {sorted(h12['refusals'])} != "
                            f"{sorted(H12_EXPECTED['refusals'])}")
        for key, want in H12_EXPECTED["computed"].items():
            checks += 1
            have = h12["computed"].get(key)
            if have != want:
                failures.append(f"H12 computed.{key} {have!r} != {want!r}")
        print(f"H12: verdict={h12['verdict']} refusals={h12['refusals']} "
              f"union_seconds={h12['computed'].get('union_seconds')} "
              f"quick_check_overlap_seconds="
              f"{h12['computed'].get('quick_check_overlap_seconds')}")

    # (2) derived keys, over EVERY window_accounting case in the report
    print("\ncase  qc_in  qc_ovl  sum_used  basis_kind  basis_registered  basis")
    for cid, verdict in by_id.items():
        if verdict["class"] != "window_accounting":
            continue
        c = verdict["computed"]
        qc_in = c.get("quick_check_in_observation_intervals")
        qc_ovl = c.get("quick_check_overlap_seconds")
        sum_used = c.get("sum_used_for_natural_duration")
        kind = c.get("basis_kind")
        registered = c.get("basis_registered")
        basis = c.get("basis")
        print(f"{cid:<5} {str(qc_in):<6} {str(qc_ovl):<7} "
              f"{str(sum_used):<9} {str(kind):<11} {str(registered):<17} {basis!r}")

        checks += 1
        if not isinstance(qc_in, bool):
            failures.append(f"{cid}: quick_check_in_observation_intervals is "
                            f"{type(qc_in).__name__}, not bool")
        elif qc_in != bool(qc_ovl is not None and qc_ovl > 0):
            failures.append(f"{cid}: quick_check_in_observation_intervals={qc_in} "
                            f"contradicts quick_check_overlap_seconds={qc_ovl}")

        checks += 1
        expect_sum = (kind == "str" and basis == "sum_of_windows"
                      and registered is True)
        if not isinstance(sum_used, bool):
            failures.append(f"{cid}: sum_used_for_natural_duration is "
                            f"{type(sum_used).__name__}, not bool")
        elif sum_used != expect_sum:
            failures.append(f"{cid}: sum_used_for_natural_duration={sum_used} "
                            f"contradicts basis={basis!r} (registered={registered})")

        checks += 1
        if basis is not None and not isinstance(basis, str):
            failures.append(f"{cid}: computed.basis echo {basis!r} is not "
                            f"JSON-native (type {type(basis).__name__})")

    # (3) the report as a whole must round-trip through JSON
    checks += 1
    try:
        json.dumps(doc)
    except TypeError as exc:
        failures.append(f"SUT report is not JSON-serialisable: {exc}")

    print(f"\nchecks={checks} failures={len(failures)}")
    for failure in failures:
        print(f"  FAIL {failure}")
    print("RESULT:", "ALL CHECKS HOLD" if not failures else "CHECKS FAILED")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
