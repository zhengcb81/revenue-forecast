"""Exit-code mutation probe (G unit) for one M21-M24 attempt.

Purpose: prove that the shared runner's exit code CARRIES the verdict, i.e. that a
corrupted expectation or a corrupted negative assertion cannot hide behind rc=0.

The probe works on a scratch copy of evidence/<card>/, NEVER on the frozen evidence:

  G-A  corrupt oracle.json positive.expected_float  -> expect rc 3 (verdict negative)
  G-B  corrupt cases.json by adding a negative case that the product does NOT
       reject (a benign driver change)              -> expect rc 3 (verdict negative)
  G-C  delete the first required driver from input.json positive -> expect rc 2
       (harness cannot produce a verdict)
  G-D  restore the frozen scratch copy             -> expect rc 0

Run:
  <kard-venv-python> -X utf8 -B scripts/selfcheck_mutations.py --card M21 \
      --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run_runner(python: str, card: str, scratch: str, code_root: str, tag: str):
    out = os.path.join(scratch, "run_result_%s.json" % tag)
    stdout = os.path.join(scratch, "stdout_%s.txt" % tag)
    stderr = os.path.join(scratch, "stderr_%s.txt" % tag)
    argv = [python, "-X", "utf8", "-B",
            os.path.join(scratch, "scripts", "run_card.py"),
            "--card", card, "--attempt", scratch,
            "--code-root", code_root, "--out", out]
    with open(stdout, "wb") as so, open(stderr, "wb") as se:
        proc = subprocess.run(argv, stdout=so, stderr=se)
    return proc.returncode, stdout, stderr, out, argv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = args.attempt
    evidence = os.path.join(attempt, "evidence", card)
    scratch = os.path.join(attempt, "recovery", "selfcheck")
    code_root = os.path.join(attempt, "iso", "checkout_scripts")
    python = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    s_ev = os.path.join(scratch, "evidence", card)

    frozen = {
        "evidence/%s/input.json" % card: sha256(os.path.join(evidence, "input.json")),
        "evidence/%s/oracle.json" % card: sha256(os.path.join(evidence, "oracle.json")),
        "evidence/%s/cases.json" % card: sha256(os.path.join(evidence, "cases.json")),
    }

    report = {"card_id": card, "attempt": attempt, "scratch": scratch,
              "frozen_hashes_before": dict(frozen), "runs": []}

    # --- G-D baseline on the pristine scratch copy -------------------------
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "D_pristine")
    report["runs"].append({"tag": "D_pristine_uncorrupted", "argv": argv,
                           "raw_exit_code": rc, "expected_exit_code": 0,
                           "stdout": stdout, "stderr": stderr, "result": out})

    # --- G-A corrupt the positive expectation ------------------------------
    oracle_path = os.path.join(s_ev, "oracle.json")
    shutil.copyfile(os.path.join(evidence, "oracle.json"), oracle_path)
    with open(oracle_path, "r", encoding="utf-8") as fh:
        oracle = json.load(fh)
    oracle["positive"]["expected_float"] = [float(v) + 999.0
                                            for v in oracle["positive"]["expected_float"]]
    with open(oracle_path, "w", encoding="utf-8") as fh:
        json.dump(oracle, fh, ensure_ascii=False, indent=1)
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "A_corrupt_oracle")
    report["runs"].append({"tag": "A_corrupted_positive_expectation", "argv": argv,
                           "mutation": "oracle.json positive.expected_float += 999",
                           "raw_exit_code": rc, "expected_exit_code": 3,
                           "stdout": stdout, "stderr": stderr, "result": out})
    shutil.copyfile(os.path.join(evidence, "oracle.json"), oracle_path)

    # --- G-B corrupt a negative assertion ----------------------------------
    cases_path = os.path.join(s_ev, "cases.json")
    shutil.copyfile(os.path.join(evidence, "cases.json"), cases_path)
    with open(cases_path, "r", encoding="utf-8") as fh:
        cases = json.load(fh)
    base = cases["cases"][0].get("base_input", "positive")
    # A driver change that the product ACCEPTS: an optional, signed/other revenue
    # line, kept out of every stock-flow bridge and of every ratio domain.
    benign = {"M21": "other_revenue", "M22": "service_revenue",
              "M23": "other_revenue", "M24": "usage_revenue"}[card]
    bump = {"id": "G-B-BOGUS", "kind": "set_driver_element", "driver": benign,
            "index": 0, "value": 5, "base_input": base,
            "expected": "ModelRegistryError",
            "why": "MUTATION PROBE: a driver change the product ACCEPTS, frozen here "
                   "as if it had to be rejected"}
    cases["cases"] = list(cases["cases"]) + [bump]
    with open(cases_path, "w", encoding="utf-8") as fh:
        json.dump(cases, fh, ensure_ascii=False, indent=1)
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "B_corrupt_cases")
    report["runs"].append({"tag": "B_corrupted_negative_assertion", "argv": argv,
                           "mutation": "cases.json += a negative case whose input the "
                                       "product does NOT reject",
                           "raw_exit_code": rc, "expected_exit_code": 3,
                           "stdout": stdout, "stderr": stderr, "result": out})
    shutil.copyfile(os.path.join(evidence, "cases.json"), cases_path)

    # --- G-C remove a required driver from the positive input --------------
    input_path = os.path.join(s_ev, "input.json")
    shutil.copyfile(os.path.join(evidence, "input.json"), input_path)
    with open(input_path, "r", encoding="utf-8") as fh:
        input_doc = json.load(fh)
    with open(cases_path, "r", encoding="utf-8") as fh:
        first = json.load(fh)["first_required_driver"]
    del input_doc["positive"]["drivers"][first]
    with open(input_path, "w", encoding="utf-8") as fh:
        json.dump(input_doc, fh, ensure_ascii=False, indent=1)
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "C_corrupt_input")
    report["runs"].append({"tag": "C_corrupted_positive_input", "argv": argv,
                           "mutation": "input.json positive.drivers[%s] deleted" % first,
                           "raw_exit_code": rc, "expected_exit_code": 2,
                           "stdout": stdout, "stderr": stderr, "result": out})

    # --- restore and re-verify ---------------------------------------------
    for name in ("input.json", "oracle.json", "cases.json"):
        shutil.copyfile(os.path.join(evidence, name), os.path.join(s_ev, name))
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "D_restored")
    report["runs"].append({"tag": "D_restored_uncorrupted", "argv": argv,
                           "raw_exit_code": rc, "expected_exit_code": 0,
                           "stdout": stdout, "stderr": stderr, "result": out})

    frozen_after = {
        "evidence/%s/input.json" % card: sha256(os.path.join(evidence, "input.json")),
        "evidence/%s/oracle.json" % card: sha256(os.path.join(evidence, "oracle.json")),
        "evidence/%s/cases.json" % card: sha256(os.path.join(evidence, "cases.json")),
    }
    report["frozen_hashes_after"] = frozen_after
    report["frozen_hashes_unchanged"] = frozen_after == frozen
    report["all_exit_codes_match_expectation"] = all(
        r["raw_exit_code"] == r["expected_exit_code"] for r in report["runs"])
    report["why_this_settles_the_mutation_requirement"] = (
        "G-A shows a corrupted positive expectation yields rc=3 instead of rc=0; "
        "G-B shows a negative assertion that the product does not satisfy yields rc=3; "
        "G-C shows a harness that cannot produce a verdict yields rc=2; "
        "G-D shows the same runner returns rc=0 on the uncorrupted scratch copy and "
        "the frozen evidence hashes are byte-identical before and after every probe.")
    target = os.path.join(scratch, "selfcheck_result.json")
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    for r in report["runs"]:
        print(r["tag"], "rc=", r["raw_exit_code"], "expected=", r["expected_exit_code"],
              "OK" if r["raw_exit_code"] == r["expected_exit_code"] else "MISMATCH")
        with open(r["stdout"], "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("verdict:") or line.startswith("negative summary:"):
                    print("   ", line.rstrip())
    print("frozen hashes unchanged:", report["frozen_hashes_unchanged"])
    return 0 if (report["all_exit_codes_match_expectation"]
                 and report["frozen_hashes_unchanged"]) else 1


if __name__ == "__main__":
    sys.exit(main())
