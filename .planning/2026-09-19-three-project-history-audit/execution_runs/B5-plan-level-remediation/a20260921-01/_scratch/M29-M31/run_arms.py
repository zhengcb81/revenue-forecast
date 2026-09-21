"""Run the REM-21 M29-M31 arms with REAL child processes and capture raw rc.

Arms:
  E  new runner, frozen cases.json            expect rc=0
  F  new runner, first negative's expected -> "ValueError"   expect rc=3
  B  OLD runner, same mutated cases.json as F expect rc=0 (fabricated green)
  G  new runner, first negative's expected key DELETED       expect rc=2
  H  OLD runner, ALL cases' expected -> "ImportError" (the reviewers' M29 P2 experiment)

The child is invoked exactly as the batch's own bound B-unit argv, with every path
redirected into this batch's scratch.  Raw rc is read from the process object.
Nothing is inferred.
"""
import json
import os
import subprocess
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        "\\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = os.path.join(ATTEMPT, "M29-M31")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M29-M31")
PY = os.path.join(PLAN, "execution_runs", "M29", "a20260919-01", "iso", "venv", "Scripts",
                  "python.exe")
CARDS = ["M29", "M30", "M31"]
ARMS = [("E", "run_card.py"), ("F", "run_card.py"), ("B", "run_card_before.py"),
        ("G", "run_card.py"), ("H_blanket", "run_card_before.py")]


def run_arm(arm, runner_name, card):
    armpath = os.path.join(SCRATCH, arm)
    runner = os.path.join(BATCH, runner_name)
    out = os.path.join(armpath, "out_%s.json" % card)
    run_result_out = os.path.join(armpath, "formula_result_%s.json" % card)
    negative_out = os.path.join(armpath, "negative_results_%s.json" % card)
    stdout_path = os.path.join(armpath, "stdout_%s.txt" % card)
    stderr_path = os.path.join(armpath, "stderr_%s.txt" % card)

    argv = [PY, "-X", "utf8", "-B", runner,
            "--card", card,
            "--attempt", armpath,
            "--code-root", os.path.join(armpath, "code_root"),
            "--out", out,
            "--run-result-out", run_result_out,
            "--negative-out", negative_out]
    proc = subprocess.run(argv, cwd=armpath, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    with open(stdout_path, "w", encoding="utf-8") as handle:
        handle.write(proc.stdout)
    with open(stderr_path, "w", encoding="utf-8") as handle:
        handle.write(proc.stderr)

    record = {"arm": arm, "card": card, "runner": runner_name, "argv": argv, "cwd": armpath,
              "raw_rc": proc.returncode, "stdout_path": stdout_path, "stderr_path": stderr_path,
              "out_path": out, "negative_out_path": negative_out,
              "result_readable": False}

    try:
        doc = json.load(open(out, encoding="utf-8"))
        neg = json.load(open(negative_out, encoding="utf-8"))
        summ = doc.get("negative_summary", {})
        counts = doc.get("negative_counts", {})
        target = None
        for entry in doc.get("negatives", []):
            if entry.get("id") == "NEG-CARD":
                target = entry
        record.update({
            "result_readable": True,
            "verdict": doc.get("verdict"),
            "exit_code_in_file": doc.get("exit_code"),
            "verdict_reasons": doc.get("verdict_reasons"),
            "declared_expectation_mismatch": counts.get("declared_expectation_mismatch"),
            "declared_expectation_not_met": counts.get("declared_expectation_not_met"),
            "declared_expectation_missing_in_cases_json":
                counts.get("declared_expectation_missing_in_cases_json"),
            "summary_passed": summ.get("passed"),
            "summary_total": summ.get("total"),
            "summary_not_judged": summ.get("not_judged"),
            "summary_failed": summ.get("failed"),
            "declared_expectations_in_cases_json":
                summ.get("declared_expectations_in_cases_json"),
            "declared_expectations_enforced": summ.get("declared_expectations_enforced"),
            "cases_json_declared_expectations_usable":
                doc.get("cases_json_declared_expectations_usable"),
            "declared_expectation_mismatch_case_ids":
                doc.get("exit_code_semantics", {}).get("declared_expectation_mismatch_case_ids"),
            "not_judged_case_ids": doc.get("exit_code_semantics", {}).get("not_judged_case_ids"),
            "model_registry_file": doc.get("model_registry_file"),
            "printed_values_match_evidence_file": doc.get("printed_values_match_evidence_file"),
            "negative_doc_summary": neg.get("summary"),
            "negative_doc_counts": neg.get("counts"),
            "negative_doc_frozen_expectation": neg.get("frozen_expectation"),
            "mutated_case_entry": target,
        })
    except Exception as exc:  # noqa: BLE001
        record["result_read_error"] = "%s: %s" % (type(exc).__name__, exc)

    record["stdout_tail"] = proc.stdout.strip().splitlines()[-4:]
    record["stderr_tail"] = proc.stderr.strip().splitlines()[-4:]
    return record


def main():
    results = []
    for arm, runner_name in ARMS:
        for card in CARDS:
            rec = run_arm(arm, runner_name, card)
            results.append(rec)
            print("%-9s %-4s raw_rc=%s verdict=%s mismatch=%s missing=%s"
                  % (arm, card, rec["raw_rc"], rec.get("verdict"),
                     rec.get("declared_expectation_mismatch"),
                     rec.get("declared_expectation_missing_in_cases_json")))
            sys.stdout.flush()

    with open(os.path.join(SCRATCH, "arm_results.json"), "w", encoding="utf-8") as handle:
        json.dump({"arms": results}, handle, ensure_ascii=False, indent=1)
    print("\nwritten arm_results.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
