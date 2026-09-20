"""Validate that every JSON artefact of one attempt parses and that key invariants hold.

Standard library only. Prints ASCII only. Exit 0 when every JSON file under the attempt
(excluding iso/venv) parses, every required evidence file exists, and the three qualifications
are consistent with the frozen card contract.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B <attempt>/scripts/validate_json_tree.py ^
      --card <CARD> --attempt <attempt>
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REQUIRED = (
    "input.json", "oracle.json", "cases.json", "source_manifest.json", "command_manifest.json",
    "stdout.txt", "stderr.txt", "formula_result.json", "negative_results.json",
    "qualification.json", "oq_rulings.json", "oq_enumeration.json", "integrity.json",
    "oracle_selfcheck.json", "revision_r2.json", "negative_results_derivation.json",
    "r2_boundary_check.json",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    card = args.card
    evidence = os.path.join(attempt, "evidence", card)
    skip = os.path.join(attempt, "iso", "venv")

    bad = []
    count = 0
    for root, dirs, files in os.walk(attempt):
        if root.startswith(skip):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not os.path.join(root, d).startswith(skip)]
        for name in sorted(files):
            if not name.endswith(".json"):
                continue
            path = os.path.join(root, name)
            count += 1
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    json.load(handle)
            except Exception as exc:  # noqa: BLE001
                bad.append((os.path.relpath(path, attempt), "%s: %s" % (type(exc).__name__, exc)))

    missing = [name for name in REQUIRED if not os.path.isfile(os.path.join(evidence, name))]
    qualification = json.load(open(os.path.join(evidence, "qualification.json"), "r",
                                   encoding="utf-8"))
    run = json.load(open(os.path.join(evidence, "run_result.json"), "r", encoding="utf-8"))
    checks = {
        "all_json_files_parse": not bad,
        "required_evidence_present": not missing,
        "qualification_formula_state_is_review_pending":
            qualification["formula"]["state"] == "review_pending",
        "qualification_disclosure_adaptation_is_unmapped":
            qualification["disclosure_adaptation"]["state"] == "unmapped",
        "qualification_accuracy_is_unproven": qualification["accuracy"]["state"] == "unproven",
        "runner_verdict_is_pass": run["verdict"]["verdict"] == "pass" and run["exit_code"] == 0,
        "negatives_all_rejected":
            run["negative_summary"]["passed"] == run["negative_summary"]["total"],
    }
    report = {
        "card_id": card,
        "json_files_checked": count,
        "unparsable": bad,
        "missing_required_evidence": missing,
        "checks": checks,
        "all_checks_passed": all(checks.values()),
    }
    print("json files checked: %d" % count)
    print("unparsable: %s" % bad)
    print("missing required evidence: %s" % missing)
    for name, ok in checks.items():
        print("check %-62s ok=%s" % (name, ok))
    print("all_checks_passed: %s" % report["all_checks_passed"])
    return 0 if report["all_checks_passed"] else 12


if __name__ == "__main__":
    raise SystemExit(main())
