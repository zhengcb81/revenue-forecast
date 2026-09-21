"""Post-run verification for the M05-M08 REM-21 batch: read the arm outputs and
assert every claim the contract requires, then print the measured facts."""
import json
import os
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = "M05-M08"
SCRATCH = os.path.join(ATTEMPT, "_scratch", BATCH)
CARDS = ["M05", "M06", "M07", "M08"]


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    rows = load(os.path.join(SCRATCH, "arms_raw.json"))
    idx = {(r["arm"], r["card"]): r for r in rows}
    problems = []

    def need(cond, msg):
        need.calls += 1
        if not cond:
            problems.append(msg)
    need.calls = 0

    for arm in ("E", "F", "B", "G"):
        for card in CARDS:
            r = idx[(arm, card)]
            out = load(r["out_json"])
            negs = {e["id"]: e for e in out["negatives"]}
            target = negs["CONT-BREAK"]
            if arm == "E":
                need(r["raw_rc"] == 0, f"E/{card} rc={r['raw_rc']}")
                need(out["negative_summary"]["failed"] == [], f"E/{card} failed non-empty")
                need(out["negative_summary"]["passed"] == 11, f"E/{card} passed != 11")
                need(all(e["verdict"] == "PASS_rejected" for e in out["negatives"]),
                     f"E/{card} non PASS_rejected present")
                need(out["negative_counts"]["declared_expectation_mismatch"] == 0,
                     f"E/{card} mismatch != 0")
                need(target["verdict"] == "PASS_rejected", f"E/{card} target != PASS_rejected")
            if arm == "F":
                need(r["raw_rc"] == 3, f"F/{card} rc={r['raw_rc']}")
                need(target["verdict"] == "FAIL_declared_expectation_mismatch",
                     f"F/{card} target verdict={target['verdict']}")
                need(target["raised"] == "ModelRegistryError",
                     f"F/{card} raised={target['raised']}")
                need(target["declared"] == "ValueError", f"F/{card} declared={target['declared']}")
                need(target["declared_expectation_mismatch"] is True, f"F/{card} mismatch not True")
                need(target["declared_expectation_not_met"] is False,
                     f"F/{card} not_met={target['declared_expectation_not_met']} (must be False: right type)")
                need(target["is_target_type"] is True, f"F/{card} is_target_type not True")
                need(out["negative_counts"]["declared_expectation_mismatch"] == 1, f"F/{card} count != 1")
                need(out["exit_code_semantics"]["verdict"] == "fail", f"F/{card} verdict != fail")
            if arm == "B":
                need(r["raw_rc"] == 0, f"B/{card} rc={r['raw_rc']}")
                need(out["exit_code_semantics"]["verdict"] == "pass", f"B/{card} verdict != pass")
                need(out["exit_code_semantics"].get("cases_json_declared_expectations_usable") is None,
                     f"B/{card} old runner somehow reports new field")
                need("declared" not in target, f"B/{card} old runner emitted 'declared'")
                need(out["negative_summary"]["passed"] == 11, f"B/{card} passed != 11")
                need("declared_expectations_enforced" not in out["negative_summary"],
                     f"B/{card} old runner reports enforcement")
            if arm == "G":
                need(r["raw_rc"] == 2, f"G/{card} rc={r['raw_rc']}")
                need(out["exit_code_semantics"]["verdict"] == "no_verdict", f"G/{card} verdict != no_verdict")
                need(target["verdict"] == "NOT_JUDGED_declaration_unusable",
                     f"G/{card} target verdict={target['verdict']}")
                need(target["judged"] is False, f"G/{card} target judged={target['judged']}")
                need(target["declared_expectation_mismatch"] is False,
                     f"G/{card} unusable case counted as mismatch")
                need(target["declared_expectation_ok"] is None, f"G/{card} declared_expectation_ok not None")
                need(out["negative_counts"]["declared_expectation_mismatch"] == 0, f"G/{card} mismatch != 0")
                need(out["negative_counts"]["declared_expectation_missing_in_cases_json"] == 1,
                     f"G/{card} missing count != 1")
                need(out["exit_code_semantics"]["declaration_unusable_case_ids"] == ["CONT-BREAK"],
                     f"G/{card} unusable ids wrong")
                need(str(out.get("no_verdict_reason", "")).startswith(
                    "cases_json_declared_expectation_missing:CONT-BREAK"),
                    f"G/{card} reason={out.get('no_verdict_reason')}")
                need(out["negative_summary"]["not_judged"] == ["CONT-BREAK"],
                     f"G/{card} not_judged={out['negative_summary']['not_judged']}")
                need(out["negative_summary"]["judged"] == 10, f"G/{card} judged != 10")

    # B and F must have run byte-identical cases.json
    for card in CARDS:
        need(idx[("B", card)]["cases_json_sha256"] == idx[("F", card)]["cases_json_sha256"],
             f"B/{card} cases.json != F/{card} cases.json")
        need(idx[("E", card)]["cases_json_sha256"] != idx[("F", card)]["cases_json_sha256"],
             f"E/{card} cases.json == F/{card} (mutation did not land)")

    print("=== per-arm/card measured (raw rc from process) ===")
    for arm in ("E", "F", "B", "G"):
        for card in CARDS:
            r = idx[(arm, card)]
            out = load(r["out_json"])
            t = {e["id"]: e for e in out["negatives"]}["CONT-BREAK"]
            print(f"{arm}/{card}: rc={r['raw_rc']} verdict={out['exit_code_semantics']['verdict']:>10} "
                  f"target_verdict={t['verdict']:<34} raised={t.get('raised')} "
                  f"declared={t.get('declared')!r} mismatch={t.get('declared_expectation_mismatch')} "
                  f"judged={t.get('judged')} "
                  f"counts={out.get('negative_counts')}")
    print()
    print("assertions_checked (need() invocations):", need.calls)
    print("problems:", len(problems))
    for p in problems:
        print("  PROBLEM:", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
