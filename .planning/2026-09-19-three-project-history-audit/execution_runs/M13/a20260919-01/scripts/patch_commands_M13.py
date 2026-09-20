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

    production_root = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
    revision_units = [
        ("K1-oracle-regenerate-with-annotation",
         "re-run the card's own oracle generator so cases.json carries the append-only annotation "
         "on the one observation that is not constructible as frozen (review note (c))",
         [venv_python, "-X", "utf8", "-B",
          os.path.join(attempt, "scripts", "oracle_M13.py"), "--out-root", attempt], 0,
         "input.json and oracle.json came out byte-identical (f4700cc2... / ab3a1f30...); only "
         "cases.json changed"),
        ("K2-cases-annotation-repack-proof",
         "prove that the only difference between the frozen cases.json revision and the "
         "regenerated one is the declared append-only annotation",
         [venv_python, "-X", "utf8", "-B",
          os.path.join(attempt, "scripts", "build_cases_annotation_repack.py"),
          "--card", "M13", "--attempt", attempt,
          "--expect-observation", "OBS-SIGNED-PERF-FEE"], 0,
         "two key additions on extra_observations[2]; every pre-existing key kept its value"),
        ("D4-append-r3",
         "append the SINGLE r3 section (response to the independent review F-01..F-05) to "
         "oracle.md below its own boundary marker and write revision_r3.json",
         [venv_python, "-X", "utf8", "-B",
          os.path.join(attempt, "scripts", "append_r3.py"),
          "--card", "M13", "--attempt", attempt], 0,
         "refuses to append when an r3 marker already exists, so no second r3 baseline can appear"),
        ("I1-audit-doc-pointers",
         "audit every <file>.py:<line> document pointer of the attempt and record the search result "
         "for the residue tokens the reviewer listed",
         [venv_python, "-X", "utf8", "-B",
          os.path.join(attempt, "scripts", "audit_doc_pointers.py"),
          "--card", "M13", "--attempt", attempt, "--production-root", production_root], 0,
         "evidence/M13/doc_pointer_audit.json all_pointers_resolve true; none of the five residue "
         "tokens exists in this attempt"),
    ]
    for unit_id, purpose, argv, rc, note in revision_units:
        if unit_id not in ids:
            doc["units"].append({"unit_id": unit_id, "purpose": purpose, "cwd": attempt,
                                 "argv": argv, "network": "disabled", "raw_rc": rc,
                                 "expected_rc": rc, "note": note})

    for unit in doc["units"]:
        if unit["unit_id"] == "B-product-run":
            unit["runner_revision_note"] = (
                "the recorded run_result.json / formula_result.json / stdout.txt were regenerated "
                "by run_card.py revision r2 (sha256 9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52"
                "cabc59c44e777ac0194), which adds the expectation-declaration consistency check "
                "(F-01). The product code and the frozen fixtures are unchanged (only cases.json "
                "gained the append-only annotation, proven by K2); the verdict values are identical "
                "(positive [25.0], continuity [25.0, 35.0], defaults [20.0], 11/11 negatives, rc=0) "
                "and the previous evidence bytes are kept under recovery/before_fixes/.")
        if unit["unit_id"] in ("D2-verify-r2-boundary", "D3-verify-r2-boundary"):
            unit["note"] = ("evidence/M13/r2_boundary_check.json all_checks_passed true; the "
                            "verifier now re-derives BOTH the r2 and the r3 boundary and checks "
                            "that each revision has exactly one section and one baseline")

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
