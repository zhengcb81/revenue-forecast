"""INDEPENDENT reviewer re-run of the M05-M08 four arms.

Written by the reviewer, not the implementer.  Uses the implementer's *runner copies*
(the thing under review) plus the *historical* frozen evidence files, and redirects
every path into _reviewer_verify/.  Raw rc is read from the child process object.
Only read-only access to historical / implementer artifacts.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = "M05-M08"
CARDS = ["M05", "M06", "M07", "M08"]
RV = os.path.join(ATTEMPT, "_reviewer_verify", BATCH)
PY = os.path.join(PLAN, "execution_runs", "M05", "a20260919-01", "iso", "venv",
                  "Scripts", "python.exe")
CODE_ROOT_SRC = os.path.join(PLAN, "execution_runs", "M05", "a20260919-01", "iso",
                             "checkout_scripts")


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build_arm(arm, card, variant):
    root = os.path.join(RV, arm)
    ev = os.path.join(root, "evidence", card)
    os.makedirs(ev, exist_ok=True)
    src = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card)
    for name in ("input.json", "oracle.json"):
        shutil.copyfile(os.path.join(src, name), os.path.join(ev, name))

    doc = json.load(open(os.path.join(src, "cases.json"), encoding="utf-8"))
    frozen_sha = sha(os.path.join(src, "cases.json"))
    target = None
    for case in doc["cases"]:
        if isinstance(case.get("expected"), str) and case["expected"].strip():
            target = case["id"]
            break
    if variant == "mutated_value":
        for case in doc["cases"]:
            if case["id"] == target:
                case["expected"] = "ValueError"
    elif variant == "deleted_key":
        for case in doc["cases"]:
            if case["id"] == target:
                del case["expected"]
    dest = os.path.join(ev, "cases.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    # code_root copy
    cr = os.path.join(root, "code_root")
    os.makedirs(cr, exist_ok=True)
    for name in os.listdir(CODE_ROOT_SRC):
        src_path = os.path.join(CODE_ROOT_SRC, name)
        if os.path.isfile(src_path):
            shutil.copyfile(src_path, os.path.join(cr, name))
    return root, dest, frozen_sha, target, sha(dest)


def run_one(arm, card, runner_name, variant):
    root, cases_path, frozen_sha, target, cases_sha = build_arm(arm, card, variant)
    runner = os.path.join(ATTEMPT, BATCH, runner_name)
    out = os.path.join(root, "out_%s.json" % card)
    rr = os.path.join(root, "run_result_%s.json" % card)
    argv = [PY, "-X", "utf8", "-B", runner,
            "--card", card,
            "--attempt", root,
            "--code-root", os.path.join(root, "code_root"),
            "--out", out,
            "--run-result-out", rr]
    proc = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    rec = {"arm": arm, "card": card, "runner": runner_name,
           "runner_sha256": sha(runner), "cases_variant": variant,
           "target_case_by_contract_rule": target,
           "cases_json_sha256": cases_sha, "frozen_cases_json_sha256": frozen_sha,
           "raw_rc": proc.returncode,
           "stderr_head": proc.stderr.strip().splitlines()[:3]}
    try:
        doc = json.load(open(out, encoding="utf-8"))
        counts = doc.get("negative_counts", {})
        summ = doc.get("negative_summary", {})
        entry = None
        for e in doc.get("negatives", []):
            if e.get("id") == target:
                entry = e
        rec.update({
            "out_json_written": True,
            "verdict": doc.get("verdict"),
            "exit_code_in_file": doc.get("exit_code"),
            "no_verdict_reason": doc.get("no_verdict_reason"),
            "declared_expectation_mismatch": counts.get("declared_expectation_mismatch"),
            "declared_expectation_missing_in_cases_json":
                counts.get("declared_expectation_missing_in_cases_json"),
            "negative_summary": {k: summ.get(k) for k in
                                 ("passed", "total", "judged", "not_judged", "failed",
                                  "declared_expectations_in_cases_json",
                                  "declared_expectations_enforced")},
            "target_entry": entry,
        })
    except Exception as exc:  # noqa: BLE001
        rec["out_json_written"] = False
        rec["read_error"] = "%s: %s" % (type(exc).__name__, exc)
    return rec


def main():
    results = []
    plan = [("E", "run_card.py", "frozen"),
            ("F", "run_card.py", "mutated_value"),
            ("B", "run_card_before.py", "mutated_value"),
            ("G", "run_card.py", "deleted_key")]
    for arm, runner, variant in plan:
        for card in CARDS:
            rec = run_one(arm, card, runner, variant)
            results.append(rec)
            print("%-2s %-4s rc=%-2s verdict=%-12s mismatch=%-5s target=%s" % (
                arm, card, rec["raw_rc"], rec.get("verdict"),
                rec.get("declared_expectation_mismatch"),
                rec["target_case_by_contract_rule"]))
            sys.stdout.flush()
    with open(os.path.join(RV, "reviewer_arm_results.json"), "w", encoding="utf-8") as fh:
        json.dump({"batch": BATCH, "arms": results}, fh, ensure_ascii=False, indent=1)
    print("\nwritten reviewer_arm_results.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
