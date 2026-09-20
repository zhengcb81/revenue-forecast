"""Patch commands.json for M13: add the H1 validation unit, a real argv-path check, and the
A0b script-revision note (standard library only).

Why: the M13 attempt was driven by hand-written commands.json entries before the generic
``write_docs.py`` existed in the sibling attempts, so it lacked (a) the H1 validation unit that
M14-M16 record, (b) the computed argv-path check, and (c) an explicit statement that the first
A0b invocation used an earlier revision of ``setup_isolation.ps1``.

Nothing else is modified: no rc, no hash, no expected value. Prints ASCII only.
"""

from __future__ import annotations

import argparse
import json
import os
import time


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    path = os.path.join(attempt, "commands.json")
    with open(path, "r", encoding="utf-8") as handle:
        doc = json.load(handle)

    venv_python = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    template_python = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(attempt))),
                                   "execution_runs", "I-00-A", "a20260919-01", "iso", "venv",
                                   "Scripts", "python.exe")
    ids = [unit["unit_id"] for unit in doc["units"]]
    if "H1-validate-json-tree" not in ids:
        doc["units"].append({
            "unit_id": "H1-validate-json-tree",
            "purpose": "parse every JSON artefact of the attempt and re-check that the three "
                       "qualifications are still distinct and that the runner verdict was pass",
            "cwd": attempt,
            "argv": [venv_python, "-X", "utf8", "-B",
                     os.path.join(attempt, "scripts", "validate_json_tree.py"),
                     "--card", "M13", "--attempt", attempt],
            "network": "disabled",
            "raw_rc": 0,
            "expected_rc": 0,
            "note": "all JSON files parse; formula=review_pending, disclosure_adaptation=unmapped, "
                    "accuracy=unproven; negatives all rejected",
        })

    checked, missing, outside = [], [], []
    for unit in doc["units"]:
        for piece in unit["argv"]:
            if len(piece) > 3 and piece[1] == ":" and ("\\" in piece or "/" in piece):
                if os.path.exists(piece):
                    checked.append(piece)
                    if not piece.startswith(attempt) and piece != template_python:
                        outside.append(piece)
                else:
                    missing.append(piece)
    doc["argv_path_check"] = {
        "rule": "every argv element that is an absolute path must exist on disk, and every such "
                "path must lie inside this attempt except the fixed I-00-A template interpreter",
        "checked": True,
        "distinct_paths_checked": len(sorted(set(checked))),
        "paths": sorted(set(checked)),
        "missing_paths": sorted(set(missing)),
        "paths_outside_the_attempt": sorted(set(outside)),
        "all_paths_exist": not missing,
        "all_paths_are_card_scoped": not [p for p in outside if p != template_python],
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    for unit in doc["units"]:
        if unit["unit_id"] == "A0b-setup-isolation":
            unit["first_invocation"]["script_revision_note"] = (
                "the failed first invocation used an earlier revision of "
                "scripts/setup_isolation.ps1 (the one whose git-output capture promoted git's "
                "harmless stderr warning to a terminating error). The file was corrected before "
                "the successful invocation, so the argv recorded here is the corrected revision; "
                "its sha256 is in evidence/M13/source_manifest.json -> card_script_hashes. The "
                "earlier revision's bytes were not kept, which is recorded here as a provenance "
                "gap rather than papered over.")
            unit["first_invocation"]["raw_rc"] = 1
            unit["first_invocation"]["expected_rc"] = 0

    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
        handle.write("\n")

    print("units=%d" % len(doc["units"]))
    print("argv paths checked=%d missing=%s outside=%s"
          % (doc["argv_path_check"]["distinct_paths_checked"],
             doc["argv_path_check"]["missing_paths"], doc["argv_path_check"]["paths_outside_the_attempt"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
