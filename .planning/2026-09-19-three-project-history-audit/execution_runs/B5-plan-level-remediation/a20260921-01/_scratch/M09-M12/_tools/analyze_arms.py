"""REM-21 / batch M09-M12 -- read the measured arm outputs and print a compact summary.

Nothing here is inferred: every value comes from a file written by a real child process whose raw
rc was recorded in ``raw_rc.json``.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = os.path.join(ATTEMPT, "M09-M12")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M09-M12")
CARDS = ["M09", "M10", "M11", "M12"]
ARMS = ["E", "F", "B", "G", "F2", "Gpre"]


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def summarize(arm: str, card: str) -> dict:
    out_dir = os.path.join(SCRATCH, arm, card)
    res = load(os.path.join(out_dir, "run_result.json"))
    neg = load(os.path.join(out_dir, "negative_results.json"))
    info = {"arm": arm, "card": card,
            "run_result_written": res is not None,
            "negative_results_written": neg is not None}
    if res is None:
        return info
    sem = res.get("exit_code_semantics") or {}
    info["result_verdict"] = res.get("verdict", sem.get("verdict"))
    info["result_exit_code"] = res.get("exit_code", sem.get("exit_code"))
    info["semantics_verdict"] = sem.get("verdict")
    info["semantics_exit_code"] = sem.get("exit_code")
    info["verdict_reasons"] = res.get("verdict_reasons")
    info["semantics_reason"] = sem.get("reason")
    info["reason_namespace"] = sem.get("reason_namespace")
    info["declared_usable"] = sem.get("cases_json_declared_expectations_usable")
    info["unusable_ids"] = sem.get("cases_json_unusable_declared_expectations")
    info["mismatch_case_ids"] = sem.get("declared_expectation_mismatch_case_ids")
    info["not_judged_case_ids"] = sem.get("not_judged_case_ids")
    ns = res.get("negative_summary") or {}
    nc = res.get("negative_counts") or {}
    info["negative_summary"] = ns
    info["negative_counts"] = nc or None
    negs = res.get("negatives") or []
    info["per_case"] = [
        {"id": e.get("id"), "raised": e.get("raised"), "expected": e.get("expected"),
         "declared": e.get("declared"), "verdict": e.get("verdict"),
         "judged": e.get("judged"),
         "raised_matches_expected_name": e.get("raised_matches_expected_name"),
         "declared_expectation_ok": e.get("declared_expectation_ok"),
         "declared_expectation_mismatch": e.get("declared_expectation_mismatch"),
         "declared_expectation_not_met": e.get("declared_expectation_not_met"),
         "declared_expectation_comparison": e.get("declared_expectation_comparison")}
        for e in negs]
    info["measured_mismatch_count"] = sum(
        1 for e in negs if e.get("declared_expectation_mismatch") is True)
    info["measured_not_judged_count"] = sum(
        1 for e in negs if e.get("verdict") == "NOT_JUDGED_declaration_unusable")
    info["measured_passed_count"] = sum(
        1 for e in negs if e.get("verdict") == "PASS_rejected")
    # arm-input identity
    cases_path = os.path.join(SCRATCH, arm, "evidence", card, "cases.json")
    info["arm_cases_sha256"] = sha256_file(cases_path) if os.path.exists(cases_path) else None
    info["arm_cases_bytes"] = os.path.getsize(cases_path) if os.path.exists(cases_path) else None
    info["out_json_sha256"] = sha256_file(os.path.join(out_dir, "run_result.json"))
    info["negative_json_sha256"] = (sha256_file(os.path.join(out_dir, "negative_results.json"))
                                    if os.path.exists(os.path.join(out_dir, "negative_results.json"))
                                    else None)
    return info


def main() -> int:
    raw = load(os.path.join(SCRATCH, "_tools", "raw_rc.json"))
    rc_map = {(r["arm"], r["card"]): r for r in raw["runs"]}
    summary = {}
    for arm in ARMS:
        summary[arm] = {}
        for card in CARDS:
            info = summarize(arm, card)
            run = rc_map.get((arm, card))
            info["raw_rc"] = None if run is None else run["rc"]
            info["runner_sha256"] = None if run is None else run["runner_sha256"]
            info["runner_is_old"] = bool(run and run["runner"].endswith("run_card_before.py"))
            info["elapsed_ms"] = None if run is None else run["elapsed_ms"]
            info["out_json_bytes"] = None if run is None else run["out_json_bytes"]
            summary[arm][card] = info

    doc = {
        "batch": "M09-M12",
        "runner_after": {"path": "M09-M12/run_card.py", "sha256": sha256_file(os.path.join(BATCH, "run_card.py")),
                         "bytes": os.path.getsize(os.path.join(BATCH, "run_card.py"))},
        "runner_before_copy": {"path": "M09-M12/run_card_before.py",
                               "sha256": sha256_file(os.path.join(BATCH, "run_card_before.py")),
                               "bytes": os.path.getsize(os.path.join(BATCH, "run_card_before.py"))},
        "raw_rc_doc": raw,
        "summary": summary,
    }
    dest = os.path.join(SCRATCH, "_tools", "arm_analysis.json")
    with open(dest, "w", encoding="utf-8", newline="") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)

    for arm in ARMS:
        for card in CARDS:
            i = summary[arm][card]
            print("%-4s %s rc=%-3s verdict=%-20s mismatch=%-4s not_judged=%-3s passed=%-3s out=%s"
                  % (arm, card, i["raw_rc"], i.get("result_verdict"), i["measured_mismatch_count"],
                     i["measured_not_judged_count"], i["measured_passed_count"],
                     i["out_json_bytes"]))
            if i.get("verdict_reasons") is not None:
                print("        verdict_reasons=%s" % json.dumps(i["verdict_reasons"]))
            if i.get("declared_usable") is not None:
                print("        declared_expectations_usable=%s unusable_ids=%s mismatch_ids=%s "
                      "not_judged_ids=%s"
                      % (i["declared_usable"], i["unusable_ids"], i["mismatch_case_ids"],
                         i["not_judged_case_ids"]))
            if i["per_case"]:
                for e in i["per_case"]:
                    if e["verdict"] != "PASS_rejected" or e["id"] in ("NEG-CARD",):
                        print("        %-11s verdict=%-34s raised=%-18s declared=%r judged=%s "
                              "ok=%s mismatch=%s not_met=%s"
                              % (e["id"], e["verdict"], e["raised"], e["declared"],
                                 e["judged"], e["declared_expectation_ok"],
                                 e["declared_expectation_mismatch"],
                                 e["declared_expectation_not_met"]))
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
