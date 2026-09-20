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

    # --- restore the input before the cases.json probes ---------------------
    # Probe C mutates input.json; F/G/H mutate only cases.json, so the input must be
    # restored first or those probes would fail for the wrong reason (rc=2 instead of 3).
    shutil.copyfile(os.path.join(evidence, "input.json"), input_path)

    # --- G-F corrupt the frozen `expected` TYPE of a negative case ----------
    # Review item P2-1: the first revision of the runner only copied cases.json
    # `expected` into the result and never compared it, so editing it to "ValueError"
    # still produced rc=0/verdict=pass. Probe F must now go red.
    with open(cases_path, "r", encoding="utf-8") as fh:
        cases = json.load(fh)
    original_expected = cases["cases"][0]["expected"]
    cases["cases"][0]["expected"] = "ValueError"
    with open(cases_path, "w", encoding="utf-8") as fh:
        json.dump(cases, fh, ensure_ascii=False, indent=1)
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "F_corrupt_expected")
    report["runs"].append({"tag": "F_corrupted_expected_type", "argv": argv,
                           "mutation": "cases.json cases[0].expected %r -> 'ValueError'" % original_expected,
                           "raw_exit_code": rc, "expected_exit_code": 3,
                           "stdout": stdout, "stderr": stderr, "result": out})
    with open(os.path.join(evidence, "cases.json"), "rb") as fh:
        frozen_cases_bytes = fh.read()
    with open(cases_path, "wb") as fh:
        fh.write(frozen_cases_bytes)

    # --- G-G corrupt a frozen MESSAGE requirement --------------------------
    # The message requirement exists so that a length/lookup guard cannot stand in
    # for the value-domain or bridge guard the case is meant to exercise. Editing the
    # requirement to an impossible string must go red.
    with open(cases_path, "r", encoding="utf-8") as fh:
        cases = json.load(fh)
    target_case = cases["cases"][0]
    original_requirement = target_case.get("expect_message_contains")
    target_case["expect_message_contains"] = "THIS_SUBSTRING_CANNOT_APPEAR"
    with open(cases_path, "w", encoding="utf-8") as fh:
        json.dump(cases, fh, ensure_ascii=False, indent=1)
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "G_corrupt_message")
    report["runs"].append({"tag": "G_corrupted_message_requirement", "argv": argv,
                           "mutation": "cases.json cases[0].expect_message_contains %r -> "
                                       "'THIS_SUBSTRING_CANNOT_APPEAR'" % original_requirement,
                           "raw_exit_code": rc, "expected_exit_code": 3,
                           "stdout": stdout, "stderr": stderr, "result": out})
    with open(cases_path, "wb") as fh:
        fh.write(frozen_cases_bytes)

    # --- G-H point the message requirement at the length-guard message ------
    # Shows the control is discriminating rather than merely non-empty: demanding the
    # LENGTH-guard wording from a case that must fail in the VALUE-domain guard has to
    # go red as well.
    with open(cases_path, "r", encoding="utf-8") as fh:
        cases = json.load(fh)
    target_case = cases["cases"][0]
    target_case["expect_message_contains"] = "must contain one value per forecast year"
    with open(cases_path, "w", encoding="utf-8") as fh:
        json.dump(cases, fh, ensure_ascii=False, indent=1)
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "H_message_from_other_guard")
    report["runs"].append({"tag": "H_message_requirement_points_at_another_guard", "argv": argv,
                           "mutation": "cases.json cases[0].expect_message_contains -> the "
                                       "LENGTH-guard wording 'must contain one value per "
                                       "forecast year'",
                           "raw_exit_code": rc, "expected_exit_code": 3,
                           "stdout": stdout, "stderr": stderr, "result": out})
    with open(cases_path, "wb") as fh:
        fh.write(frozen_cases_bytes)

    # --- G-R4 remove the frozen `required_message_ids` gate ------------------
    # Review round 2, item 3: freezing the individual message requirements was not enough,
    # because DELETING one silently disabled the check. The gate field closes that hole, so
    # removing it must now go red.
    with open(cases_path, "r", encoding="utf-8") as fh:
        cases = json.load(fh)
    removed_gate = cases.pop("required_message_ids", None)
    with open(cases_path, "w", encoding="utf-8") as fh:
        json.dump(cases, fh, ensure_ascii=False, indent=1)
    rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root, "R4_no_gate")
    report["runs"].append({"tag": "R4_required_message_ids_gate_removed", "argv": argv,
                           "mutation": "cases.json `required_message_ids` %r deleted"
                                       % (removed_gate,),
                           "raw_exit_code": rc, "expected_exit_code": 3,
                           "stdout": stdout, "stderr": stderr, "result": out})
    with open(cases_path, "wb") as fh:
        fh.write(frozen_cases_bytes)

    # --- G-R5 empty one required message requirement -------------------------
    # The other half of the same hole: keeping the id in the gate list but blanking its
    # `expect_message_contains` must also go red.
    gate_ids = json.loads(frozen_cases_bytes.decode("utf-8")).get("required_message_ids") or []
    if gate_ids:
        with open(cases_path, "r", encoding="utf-8") as fh:
            cases = json.load(fh)
        victim = gate_ids[0]
        for case in cases["cases"]:
            if case["id"] == victim:
                case["expect_message_contains"] = ""
        with open(cases_path, "w", encoding="utf-8") as fh:
            json.dump(cases, fh, ensure_ascii=False, indent=1)
        rc, stdout, stderr, out, argv = run_runner(python, card, scratch, code_root,
                                                   "R5_empty_requirement")
        report["runs"].append({"tag": "R5_required_message_requirement_emptied", "argv": argv,
                               "mutation": "cases.json %s.expect_message_contains -> ''" % victim,
                               "raw_exit_code": rc, "expected_exit_code": 3,
                               "stdout": stdout, "stderr": stderr, "result": out})
        with open(cases_path, "wb") as fh:
            fh.write(frozen_cases_bytes)

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
        "G-F shows that editing a case's frozen `expected` TYPE now yields rc=3 "
        "(FAIL_expected_type_mismatch) instead of silently passing; "
        "G-G shows that an impossible frozen MESSAGE requirement yields rc=3; "
        "G-H shows the message control is discriminating: demanding the LENGTH-guard wording "
        "from a case that must fail in the VALUE-domain guard also yields rc=3; "
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
