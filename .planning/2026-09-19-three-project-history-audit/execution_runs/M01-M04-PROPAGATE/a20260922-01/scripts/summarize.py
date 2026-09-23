"""Build evidence/arms_summary.json — the per-batch arm table with RAW rc,
cross-checked against the FROZEN oracle (written before any run)."""
from __future__ import annotations

import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ATTEMPT, "evidence")
CARDS = ("M01", "M02", "M03", "M04")
ARMS = ("E", "F", "G", "S", "B")


def main() -> int:
    records = json.load(open(os.path.join(EVIDENCE, "arms_raw.json"), encoding="utf-8"))
    by_key = {(r["card"], r["arm"]): r for r in records}

    table, checks = {}, []
    negcard_verdicts = {}
    for card in CARDS:
        row = {}
        for arm in ARMS:
            r = by_key[(card, arm)]
            row[arm] = {
                "raw_rc": r["raw_rc"],
                "expected_rc_frozen": r["expected_rc"],
                "meets_frozen_expectation": r["meets_expectation"],
                "verdict": r["verdict"],
                "out_written": r["out_written"],
                "mismatch_ids": r["mismatch_ids"],
                "unusable_ids": r["unusable_ids"],
                "missing_count": r["missing_count"],
                "no_verdict_reason": r["no_verdict_reason"],
                "mutated_case": r["mutated_case"],
                "runner_sha256": r["runner_sha256"],
            }
            checks.append(r["meets_expectation"])
        # deep checks from the out.json artefacts
        f_out = json.load(open(os.path.join(EVIDENCE, card, "F", "out.json"),
                               encoding="utf-8"))
        negcard = next(e for e in f_out["negatives"] if e["id"] == "NEG-CARD")
        negcard_verdicts[card] = {
            "verdict": negcard["verdict"],
            "raised": negcard["raised"],
            "declared": negcard["declared"],
            "declared_expectation_mismatch": negcard["declared_expectation_mismatch"],
            "judged": negcard["judged"],
            "comparison": negcard["declared_expectation_comparison"],
        }
        e_out = json.load(open(os.path.join(EVIDENCE, card, "E", "out.json"),
                               encoding="utf-8"))
        checks.append(
            e_out["negative_summary"]["declared_expectations_in_cases_json"]
            == ["ModelRegistryError"])
        checks.append(e_out["negative_summary"]["declared_expectations_enforced"] is True)
        g_rec = by_key[(card, "G")]
        checks.append(g_rec["no_verdict_reason"]
                      == "cases_json_declared_expectation_missing:NEG-CARD")
        checks.append(g_rec["missing_count"] == 1)
        checks.append(g_rec["mismatch_count"] == 0)
        checks.append(negcard_verdicts[card]["verdict"]
                      == "FAIL_declared_expectation_mismatch")
        s_err = open(os.path.join(EVIDENCE, card, "S", "stderr.txt"),
                     encoding="utf-8", errors="replace").read()
        checks.append("KeyError: 'kind'" in s_err)
        s_out_absent = not os.path.exists(os.path.join(EVIDENCE, card, "S", "out.json"))
        checks.append(s_out_absent)
        b_out = json.load(open(os.path.join(EVIDENCE, card, "B", "out.json"),
                               encoding="utf-8"))
        checks.append(b_out["exit_code_semantics"]["exit_code"] == 0)
        checks.append("declared_expectations_enforced" not in b_out.get("negative_summary", {}))
        table[card] = row

    uniform = {
        "E": sorted({table[c]["E"]["raw_rc"] for c in CARDS}),
        "F": sorted({table[c]["F"]["raw_rc"] for c in CARDS}),
        "G": sorted({table[c]["G"]["raw_rc"] for c in CARDS}),
        "S": sorted({table[c]["S"]["raw_rc"] for c in CARDS}),
        "B": sorted({table[c]["B"]["raw_rc"] for c in CARDS}),
    }
    summary = {
        "card": "M01-M04-PROPAGATE",
        "attempt": "execution_runs/M01-M04-PROPAGATE/a20260922-01",
        "oracle_frozen_before_runs": {
            "sha256": "9ff1dedec8f2687298f6d083418558e16f85db5c247cb8c2213d2e6327dae0f4",
            "record": "evidence/oracle_freeze.json"},
        "authority": "OWNER_DECISIONS.md §18 A-1 = 1 (①扩权); expected E=0/F=3/G=2/S=1",
        "runner_new": {"sha256": by_key[("M01", "E")]["runner_sha256"],
                       "patched_copy": "iso/run_card.py"},
        "runner_old": {"sha256": by_key[("M01", "B")]["runner_sha256"],
                       "byte_copy": "iso/run_card_before.py",
                       "identical_to_historical": True},
        "arm_table_raw_rc": {c: {a: table[c][a]["raw_rc"] for a in ARMS} for c in CARDS},
        "arm_table_expected": {"E": 0, "F": 3, "G": 2, "S": 1, "B": 0},
        "uniform_raw_rc_per_arm": uniform,
        "all_arms_meet_frozen_expectation": all(checks),
        "deep_checks_passed": sum(bool(c) for c in checks), "deep_checks_total": len(checks),
        "per_card": table,
        "arm_F_negcard_verdicts": negcard_verdicts,
        "interpretation": {
            "E": "green control: the new gate does not false-red the frozen fixtures (0)",
            "F": "the gate FIRES: usable-but-different declaration -> rc=3 (historically "
                 "F=0 fabricated green on these four batches, REM-80)",
            "B": "inertness control: historical byte-copy on the SAME mutated fixture -> "
                 "rc=0 = the fabricated green, re-measured in this attempt",
            "G": "declaration unusable decided BEFORE any case -> rc=2 + no_verdict + "
                 "cases_json_declared_expectation_missing:NEG-CARD; missing_count=1, "
                 "never counted as mismatch (historically G=1 KeyError crash)",
            "S": "exactly one structural fault (extra case entry missing `kind`) -> "
                 "uncaught KeyError, no out.json, rc=1 (structural stays rc=1)",
        },
        "manifest_verification": json.load(
            open(os.path.join(EVIDENCE, "manifest_verification.json"), encoding="utf-8")),
    }
    out = os.path.join(EVIDENCE, "arms_summary.json")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("arm_table:", json.dumps(summary["arm_table_raw_rc"]))
    print("uniform:", json.dumps(uniform))
    print("deep_checks: %d/%d all_arms_meet=%s"
          % (summary["deep_checks_passed"], summary["deep_checks_total"],
             summary["all_arms_meet_frozen_expectation"]))
    print("manifest:", summary["manifest_verification"]["result"])
    return 0 if (summary["all_arms_meet_frozen_expectation"]
                 and summary["manifest_verification"]["result"] == "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
