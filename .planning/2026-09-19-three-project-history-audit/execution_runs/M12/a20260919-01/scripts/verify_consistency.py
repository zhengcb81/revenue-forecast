"""Printed-value vs evidence-file consistency verifier.

This exists because a previous batch printed a value that did not match its evidence file.
Every number the runner prints must be re-readable from the evidence JSON, and the exit
code printed must equal the exit code recorded in run_result.json, formula_result.json,
negative_results.json, the shell exit-code ledger and qualification.json.

Run:
  python -X utf8 -B scripts/verify_consistency.py --card M09 --attempt <attempt>
"""

from __future__ import annotations

import argparse
import json
import os
import re

CHECKS = []


def add(check_id, ok, printed, observed, note=""):
    CHECKS.append({"check": check_id, "ok": bool(ok), "printed": printed,
                   "observed": observed, "note": note})


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_stdout(text):
    fields = {}
    for line in text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields.setdefault(key.strip(), value.strip())
        if line.startswith("negative:") or line.startswith("observation:"):
            fields.setdefault("__negative_lines__", []).append(line)
    negative_lines = [line for line in text.splitlines() if line.startswith("negative:")]
    observation_lines = [line for line in text.splitlines() if line.startswith("observation:")]
    fields["__negative_lines__"] = negative_lines
    fields["__observation_lines__"] = observation_lines
    return fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    card = args.card
    evidence = os.path.join(attempt, "evidence", card)

    stdout_text = open(os.path.join(evidence, "stdout.txt"), "r", encoding="utf-8").read()
    printed = parse_stdout(stdout_text)
    run_result = load_json(os.path.join(evidence, "run_result.json"))
    formula_result = load_json(os.path.join(evidence, "formula_result.json"))
    negative_results = load_json(os.path.join(evidence, "negative_results.json"))
    oracle = load_json(os.path.join(evidence, "oracle.json"))
    source_manifest = load_json(os.path.join(evidence, "source_manifest.json"))
    qualification = load_json(os.path.join(evidence, "qualification.json"))
    ledger = {}
    ledger_path = os.path.join(attempt, "after", "rc_ledger.txt")
    if os.path.exists(ledger_path):
        for line in open(ledger_path, "r", encoding="ascii", errors="replace"):
            line = line.strip()
            if line and not line.startswith("#"):
                unit, _, rc = line.partition("\t")
                ledger[unit.strip()] = int(rc.strip())

    rc = run_result["exit_code_semantics"]["exit_code"]

    # 1. printed positive values == evidence files
    add("positive_actual_printed_equals_formula_result",
        printed.get("positive actual") == str(formula_result["positive"].get("actual")),
        printed.get("positive actual"), formula_result["positive"].get("actual"))
    add("positive_actual_printed_equals_run_result",
        printed.get("positive actual") == str(run_result["positive"].get("actual")),
        printed.get("positive actual"), run_result["positive"].get("actual"))
    add("positive_expected_printed_equals_oracle",
        printed.get("positive expected") == str(oracle["positive"]["expected_float"]),
        printed.get("positive expected"), oracle["positive"]["expected_float"])
    add("positive_expected_printed_equals_formula_result_per_value",
        printed.get("positive expected")
        == str([c["expected"] for c in formula_result.get("per_value_checks", [])]),
        printed.get("positive expected"),
        [c["expected"] for c in formula_result.get("per_value_checks", [])])

    add("continuity_actual_printed_equals_file",
        printed.get("continuity_positive actual") == str(formula_result["continuity_positive"]["actual"]),
        printed.get("continuity_positive actual"), formula_result["continuity_positive"]["actual"])
    add("continuity_expected_printed_equals_oracle",
        printed.get("continuity_positive expected") == str(oracle["continuity_positive"]["expected_float"]),
        printed.get("continuity_positive expected"), oracle["continuity_positive"]["expected_float"])
    add("continuity_ok_printed_equals_file",
        printed.get("continuity_positive ok") == str(formula_result["continuity_positive"]["ok"]),
        printed.get("continuity_positive ok"), formula_result["continuity_positive"]["ok"])

    add("defaults_actual_printed_equals_file",
        printed.get("defaults actual") == str(formula_result["defaults"]["actual"]),
        printed.get("defaults actual"), formula_result["defaults"]["actual"])
    add("defaults_expected_printed_equals_oracle",
        printed.get("defaults expected") == str(oracle["defaults_expected_float"]),
        printed.get("defaults expected"), oracle["defaults_expected_float"])
    add("defaults_ok_printed_equals_file",
        printed.get("defaults ok") == str(formula_result["defaults"]["ok"]),
        printed.get("defaults ok"), formula_result["defaults"]["ok"])

    # 2. printed registry facts == the manifest's observed registry metadata
    observed_reg = source_manifest["registry_metadata_observed_from_the_isolated_copy"]
    add("registry_formula_printed_equals_manifest",
        printed.get("registry formula") == str(observed_reg["formula"]),
        printed.get("registry formula"), observed_reg["formula"])
    add("registry_required_printed_equals_manifest",
        printed.get("registry required") == str(observed_reg["required"]),
        printed.get("registry required"), observed_reg["required"])
    add("registry_optional_printed_equals_manifest",
        printed.get("registry optional") == str(observed_reg["optional"]),
        printed.get("registry optional"), observed_reg["optional"])

    # 3. printed negative lines == negative_results.json entries
    by_id = {e["id"]: e for e in negative_results["negatives"]}
    mismatches = []
    for line in printed["__negative_lines__"]:
        match = re.match(r"negative: (\S+) verdict=(\S+) raised=(\S+) expected=(\S+) - (.*)$", line)
        if not match:
            mismatches.append({"line": line, "error": "unparseable"})
            continue
        case_id, verdict, raised, expected, message = match.groups()
        entry = by_id.get(case_id)
        if entry is None:
            mismatches.append({"line": line, "error": "no such case in negative_results.json"})
            continue
        if (verdict != entry["verdict"] or raised != str(entry.get("raised"))
                or expected != entry["expected"] or message != (entry.get("message") or "")):
            mismatches.append({"line": line, "entry": {k: entry.get(k) for k in
                                                      ("verdict", "raised", "expected", "message")}})
    add("every_printed_negative_line_matches_negative_results",
        not mismatches and len(printed["__negative_lines__"]) == len(negative_results["negatives"]),
        "%d printed lines" % len(printed["__negative_lines__"]),
        "%d json entries" % len(negative_results["negatives"]),
        note=json.dumps(mismatches[:5], ensure_ascii=True))

    # 4. printed summaries
    add("negative_summary_printed_equals_file",
        printed.get("negative_summary") == json.dumps(negative_results["negative_summary"],
                                                     ensure_ascii=True),
        printed.get("negative_summary"),
        json.dumps(negative_results["negative_summary"], ensure_ascii=True))
    add("negative_summary_printed_equals_run_result",
        printed.get("negative_summary") == json.dumps(run_result["negative_summary"], ensure_ascii=True),
        printed.get("negative_summary"), json.dumps(run_result["negative_summary"], ensure_ascii=True))

    # 5. verdict / exit code agreement across every file and the shell ledger
    verdict_line = printed.get("verdict")
    add("verdict_line_matches_files",
        verdict_line == "%s exit_code: %s" % (run_result["exit_code_semantics"]["verdict"], rc),
        verdict_line,
        "%s exit_code: %s" % (run_result["exit_code_semantics"]["verdict"], rc))
    add("exit_code_run_result_equals_formula_result",
        rc == formula_result["exit_code_semantics"]["exit_code"], rc,
        formula_result["exit_code_semantics"]["exit_code"])
    add("exit_code_run_result_equals_negative_results",
        rc == negative_results["exit_code_semantics"]["exit_code"], rc,
        negative_results["exit_code_semantics"]["exit_code"])
    add("exit_code_equals_shell_ledger",
        rc == ledger.get("B-%s-product-run" % card), rc, ledger.get("B-%s-product-run" % card))
    add("qualification_runner_exit_code_equals_rc",
        qualification["formula"]["a_to_c_conditions"]["runner_exit_code"] == rc, rc,
        qualification["formula"]["a_to_c_conditions"]["runner_exit_code"])
    add("qualification_negatives_rejected_equals_summary",
        qualification["formula"]["a_to_c_conditions"]["negatives_rejected"]
        == "%d/%d" % (run_result["negative_summary"]["passed"], run_result["negative_summary"]["total"]),
        qualification["formula"]["a_to_c_conditions"]["negatives_rejected"],
        "%d/%d" % (run_result["negative_summary"]["passed"], run_result["negative_summary"]["total"]))

    # 6. observations printed == observations in negative_results.json
    obs_by_id = {o["id"]: o for o in negative_results["observations"]}
    obs_mismatch = []

    def parse_observation_line(line):
        """Positional parse: the expectation field is JSON and may contain spaces."""
        markers = ["observation: ", " gating=", " raised=", " actual=", " expectation=",
                   " matches_expected=", " matches_compared=", " expect_equal=",
                   " matches_expected_relation="]
        positions = []
        cursor = 0
        for marker in markers:
            index = line.find(marker, cursor)
            if index < 0:
                return None
            positions.append(index)
            cursor = index + len(marker)
        values = []
        for i, marker in enumerate(markers):
            start = positions[i] + len(marker)
            end = positions[i + 1] if i + 1 < len(positions) else cursor
            values.append(line[start:end])
        relation, _, message = line[cursor:].partition(" ")
        values.append(relation)
        return {"id": values[0], "gating": values[1], "raised": values[2], "actual": values[3],
                "expectation": values[4], "matches_expected": values[5],
                "matches_compared": values[6], "expect_equal": values[7],
                "matches_expected_relation": values[8], "message": message}

    for line in printed["__observation_lines__"]:
        parsed = parse_observation_line(line)
        if parsed is None:
            obs_mismatch.append({"line": line, "error": "unparseable"})
            continue
        entry = obs_by_id.get(parsed["id"])
        if entry is None:
            obs_mismatch.append({"line": line, "error": "no such observation"})
            continue
        if (parsed["gating"] != str(entry["gating"])
                or parsed["raised"] != str(entry.get("raised"))
                or parsed["actual"] != str(entry.get("actual"))
                or parsed["matches_expected"] != str(entry.get("matches_expected"))):
            obs_mismatch.append({"line": line,
                                 "entry": {k: entry.get(k) for k in
                                           ("gating", "raised", "actual", "matches_expected")}})
    add("every_printed_observation_line_matches_file",
        not obs_mismatch and len(printed["__observation_lines__"]) == len(negative_results["observations"]),
        "%d printed lines" % len(printed["__observation_lines__"]),
        "%d json entries" % len(negative_results["observations"]),
        note=json.dumps(obs_mismatch[:5], ensure_ascii=True))

    # 7. the printed tolerance must equal the frozen oracle tolerance
    add("positive_tolerance_printed_equals_oracle",
        printed.get("positive tolerance") == str(oracle["positive"]["tolerances"]),
        printed.get("positive tolerance"), oracle["positive"]["tolerances"])

    # 8. no non-ASCII-only artefacts in the frozen expectation direction
    add("frozen_input_hashes_recorded",
        bool(run_result.get("frozen_input_hashes")), bool(run_result.get("frozen_input_hashes")), True)

    ok = all(c["ok"] for c in CHECKS)
    doc = {
        "card_id": card,
        "attempt_id": os.path.basename(attempt),
        "purpose": "every value the runner printed must be re-readable from the evidence files; "
                   "this is the explicit guard against a printed/recorded mismatch",
        "checks": CHECKS,
        "checks_total": len(CHECKS),
        "checks_failed": [c["check"] for c in CHECKS if not c["ok"]],
        "all_consistent": ok,
    }
    with open(os.path.join(evidence, "consistency_check.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
        handle.write("\n")

    print("card", card)
    for c in CHECKS:
        print("check %-52s ok=%s printed=%s observed=%s %s"
              % (c["check"], c["ok"], c["printed"], c["observed"], c["note"]))
    print("checks_total", len(CHECKS), "checks_failed", doc["checks_failed"])
    print("all_consistent", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
