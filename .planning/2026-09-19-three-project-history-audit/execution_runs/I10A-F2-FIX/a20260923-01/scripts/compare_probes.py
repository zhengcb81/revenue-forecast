#!/usr/bin/env python3
"""Compare probe_before vs probe_after payloads and rc's (oracle I-2 / §4).

Rules:
  * every arm: rc table before vs after (the ONLY expected delta is
    mut_omit_optional 3,3,3,2 -> 2,2,2,2).
  * normal arms: payload must be byte-identical after removing ONLY the
    harness timestamps started_at_local / finished_at_local.
  * mut_omit after: every recorded refusal must carry the frozen message
    "missing driver for {model}: other_revenue has no explicit default"
    with error_type ForecastInputError.
Exit 0 iff all hold; writes evidence/probe_compare.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
CASES = ["ZJ-MIN-M09", "ZJ-SMT-M09", "XM-PHONE-M03", "XM-EV-M03"]
ARMS = ["normal", "red_conv", "mut_swap_ids", "mut_swap", "mut_omit_optional"]
EXPECTED_DELTA = {("mut_omit_optional", c): {"before": None, "after": 2} for c in CASES}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def strip_time(doc: dict) -> dict:
    doc = dict(doc)
    doc.pop("started_at_local", None)
    doc.pop("finished_at_local", None)
    return doc


def main() -> int:
    # argv: [script] [after_dir_name] [report_name]  (defaults keep the frozen run)
    after_dir = sys.argv[1] if len(sys.argv) > 1 else "probe_after"
    report_name = sys.argv[2] if len(sys.argv) > 2 else "probe_compare.json"
    rc_table: dict[str, dict[str, dict]] = {}
    normal_identical = True
    omit_messages_ok = True
    details: dict[str, object] = {}
    only_expected_delta = True

    for case in CASES:
        rc_table[case] = {}
        for arm in ARMS:
            b_path = ATT / "evidence" / "probe_before" / case / arm / "probe_result.json"
            a_path = ATT / "evidence" / after_dir / case / arm / "probe_result.json"
            b, a = load(b_path), load(a_path)
            rc_table[case][arm] = {"before": b["raw_rc"], "after": a["raw_rc"]}
            if b["raw_rc"] != a["raw_rc"]:
                key = (arm, case)
                if key not in EXPECTED_DELTA:
                    only_expected_delta = False
                    details.setdefault("unexpected_rc_delta", []).append(
                        {"case": case, "arm": arm, "before": b["raw_rc"], "after": a["raw_rc"]}
                    )
                elif b["raw_rc"] != 3 or a["raw_rc"] != 2:
                    only_expected_delta = False
            if arm == "normal":
                same = strip_time(b) == strip_time(a)
                normal_identical = normal_identical and same
                details.setdefault("normal_identical", {})[case] = same
                if not same:
                    # locate first difference for evidence
                    sb, sa = strip_time(b), strip_time(a)
                    for key in sorted(set(sb) | set(sa)):
                        if sb.get(key) != sa.get(key):
                            details.setdefault("normal_first_diff", {})[case] = key
                            break
            if arm == "mut_omit_optional":
                model = a["model_id"]
                expected_msg = (
                    f"missing driver for {model}: other_revenue has no explicit default"
                )
                errs = a.get("product_errors", [])
                ok = (
                    a["raw_rc"] == 2
                    and errs
                    and all(
                        e["error_type"] == "ForecastInputError" and e["error"] == expected_msg
                        for e in errs
                    )
                    and len(errs) == 3 * len(a["instances"])
                )
                omit_messages_ok = omit_messages_ok and ok
                details.setdefault("omit_messages", {})[case] = {
                    "expected": expected_msg,
                    "count": len(errs),
                    "ok": ok,
                    "sample": errs[0] if errs else None,
                }

    report = {
        "artifact": "probe_compare",
        "before_dir": "probe_before",
        "after_dir": after_dir,
        "rc_table": rc_table,
        "only_expected_delta": only_expected_delta,
        "normal_arm_payloads_identical_modulo_timestamps": normal_identical,
        "omit_refusal_messages_exact": omit_messages_ok,
        "details": details,
    }
    out = ATT / "evidence" / report_name
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    all_ok = only_expected_delta and normal_identical and omit_messages_ok
    print(
        json.dumps(
            {
                "all_ok": all_ok,
                "only_expected_delta": only_expected_delta,
                "normal_identical": normal_identical,
                "omit_messages_ok": omit_messages_ok,
            }
        )
    )
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
