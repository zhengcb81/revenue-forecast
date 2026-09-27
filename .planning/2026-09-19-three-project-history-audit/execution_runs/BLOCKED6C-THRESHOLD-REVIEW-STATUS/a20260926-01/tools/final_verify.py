"""BLOCKED6C final verification (oracle.md exit criteria 6-7).

Re-reads every JSON deliverable with json.load, re-hashes the sealed inputs and
this attempt's deliverables, checks UTF-8/BOM/line endings, re-measures the git
read-only counters, and writes final_verification.json (UTF-8, no BOM, LF).

Usage:
  python -X utf8 -B tools/final_verify.py --out final_verification.json
      --git-name-only <file produced by git diff HEAD --name-only>
      --git-untracked <file produced by git ls-files --others --exclude-standard>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANNING = os.path.abspath(os.path.join(RUN, os.pardir, os.pardir, os.pardir))

JSON_FILES = [
    "red/baseline_validation_report.json",
    "red/baseline_recheck_report.json",
    "red/ce22_ce25_report.json",
    "green/cases_report.json",
    "green/validation_report.json",
    "l271/l271_report.json",
    "handoff.json",
] + ["mut/M%d/cases_report.json" % i for i in range(1, 6)]

TEXT_FILES = [
    "oracle.md", "changes.diff", "handoff.json",
    "tools/run_cases.py", "tools/make_mutants.py", "tools/l271_monitor.py",
    "tools/make_diff.py", "tools/build_handoff.py", "tools/final_verify.py",
    "iso_patched/tools/validate_hypotheses.py",
    "green/cases_report.json", "green/validation_report.json",
    "l271/l271_report.json", "red/ce22_ce25_report.json",
]


def sha_bytes(path):
    raw = open(path, "rb").read()
    return hashlib.sha256(raw).hexdigest(), len(raw)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--git-name-only", required=True)
    ap.add_argument("--git-untracked", required=True)
    args = ap.parse_args()

    reparse = {}
    for rel in JSON_FILES:
        p = os.path.join(RUN, rel)
        raw = open(p, "rb").read()
        try:
            json.loads(raw.decode("utf-8"))
            ok, err = True, None
        except Exception as exc:  # noqa: BLE001 - reported verbatim
            ok, err = False, repr(exc)
        reparse[rel] = {"ok": ok, "error": err, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()}

    enc = {}
    for rel in TEXT_FILES:
        p = os.path.join(RUN, rel)
        raw = open(p, "rb").read()
        bom = raw[:3] == b"\xef\xbb\xbf"
        try:
            raw.decode("utf-8")
            utf8 = True
        except UnicodeDecodeError:
            utf8 = False
        crlf = sum(1 for i in range(1, len(raw))
                   if raw[i] == 10 and raw[i - 1] == 13)
        lf = raw.count(b"\n")
        enc[rel] = {"utf8": utf8, "bom": bom, "crlf": crlf, "lf": lf,
                    "crlf_free": crlf == 0}

    sealed = json.load(open(os.path.join(RUN, "handoff.json"),
                            encoding="utf-8"))["sealed_inputs_reverified"]
    sealed_now = []
    for s in sealed:
        sha, ln = sha_bytes(os.path.join(PLANNING, s["path"]))
        sealed_now.append({"path": s["path"], "sha256": sha,
                           "sha256_expected": s["sha256_expected"],
                           "bytes": ln, "bytes_expected": s["bytes_expected"],
                           "match": sha == s["sha256_expected"]
                                    and ln == s["bytes_expected"]})

    pre_sha, pre_len = sha_bytes(os.path.join(RUN, "iso", "tools",
                                              "validate_hypotheses.py"))
    post_sha, post_len = sha_bytes(os.path.join(RUN, "iso_patched", "tools",
                                                "validate_hypotheses.py"))
    diff_sha, diff_len = sha_bytes(os.path.join(RUN, "changes.diff"))
    oracle_sha, oracle_len = sha_bytes(os.path.join(RUN, "oracle.md"))
    handoff_sha, handoff_len = sha_bytes(os.path.join(RUN, "handoff.json"))

    def read_lines(path):
        """PowerShell 5.1 `>` writes UTF-16LE with a BOM; accept any of the three."""
        raw = open(path, "rb").read()
        if raw[:2] == b"\xff\xfe":
            text, enc = raw.decode("utf-16"), "utf-16 (LE BOM, stripped)"
        elif raw[:2] == b"\xfe\xff":
            text, enc = raw.decode("utf-16"), "utf-16 (BE BOM, stripped)"
        elif raw[:3] == b"\xef\xbb\xbf":
            text, enc = raw.decode("utf-8-sig"), "utf-8-sig"
        else:
            text, enc = raw.decode("utf-8", errors="replace"), "utf-8"
        return [l.lstrip("\ufeff") for l in text.splitlines() if l.strip()], enc

    def count_non_planning(path):
        lines, enc = read_lines(path)
        non = [l for l in lines if not l.startswith(".planning")]
        return len(lines), non, enc

    diff_total, diff_non, diff_enc = count_non_planning(args.git_name_only)
    untr_total, untr_non, untr_enc = count_non_planning(args.git_untracked)

    green = json.load(open(os.path.join(RUN, "green", "cases_report.json"),
                           encoding="utf-8"))
    handoff = json.load(open(os.path.join(RUN, "handoff.json"), encoding="utf-8"))

    checks = {
        "json_all_reparsed": all(v["ok"] for v in reparse.values()),
        "green_positive_pass": green["positive_case"]["verdict"] == "pass"
                               and not green["positive_case"]["errors"],
        "green_ce_4_of_4": green["ce_summary"] == {
            "cases": 4, "rejected": 4, "accepted": 0, "accepted_ids": []},
        "green_original_21_rejected": green["target_suite"]
                                       ["original_21_rejected"] == 21,
        "green_new_4_rejected": green["target_suite"]["new_b6c_rejected"] == 4,
        "green_suite_25_of_25": green["target_suite"]["cases"] == 25
                                and green["target_suite"]
                                ["rejected_as_expected"] == 25
                                and green["target_suite"]
                                ["accepted_by_mistake"] == 0,
        "pre_image_equals_sealed":
            pre_sha == "cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac"
            and pre_len == 28549,
        "sealed_inputs_all_match": all(s["match"] for s in sealed_now),
        "utf8_no_bom": all(not v["bom"] and v["utf8"] for k, v in enc.items()),
        "deliverables_lf": all(v["crlf_free"] for k, v in enc.items()),
        "git_diff_non_planning_zero": len(diff_non) == 0,
        "handoff_status_review_pending": handoff["status"] == "review_pending",
        "handoff_implementer_signed_false":
            handoff["implementer_signed"] is False,
        "mutations_all_match_oracle_S5": all(
            v["matches_oracle_S5_expectation"]
            for v in handoff["red_green_mutations"]["mutations"].values()),
        "l271_hand_calculation_matches_measurement":
            handoff["L271"]["matches_oracle_frozen_hand_calculation"],
        "l271_not_fired_under_primary": handoff["L271"]["trigger_fired"] is False,
        "l271_literal_counterfactual_disclosed":
            handoff["L271"]["trigger_fired_literal_A61_reading"] is True,
        "fail_closed_blocked_is_false": handoff["fail_closed"]["blocked"] is False,
        "changes_diff_sha_matches_disk":
            handoff["changes_diff"]["sha256"] == diff_sha
            and handoff["changes_diff"]["bytes"] == diff_len,
        "changes_diff_single_file_no_deletions":
            handoff["changes_diff"]["touched_files"] == 1
            and handoff["changes_diff"]["deletions"] == 0,
        "regression_21_passed": handoff["counterexample_regression_21"]["passed"],
    }

    doc = {
        "verification": "BLOCKED6C final verification (oracle.md exit criteria 6-7)",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "json_reparse": reparse,
        "encoding": enc,
        "sealed_inputs_reverified": sealed_now,
        "sha256": {
            "oracle.md": {"sha256": oracle_sha, "bytes": oracle_len},
            "iso (pre-image)": {"sha256": pre_sha, "bytes": pre_len},
            "iso_patched (post-image)": {"sha256": post_sha, "bytes": post_len},
            "changes.diff": {"sha256": diff_sha, "bytes": diff_len},
            "handoff.json": {"sha256": handoff_sha, "bytes": handoff_len},
        },
        "git": {
            "input_encoding_name_only": diff_enc,
            "input_encoding_untracked": untr_enc,
            "diff_HEAD_name_only_total": diff_total,
            "diff_HEAD_name_only_non_planning": len(diff_non),
            "diff_HEAD_name_only_non_planning_paths": diff_non,
            "ls_files_others_total": untr_total,
            "ls_files_others_non_planning": len(untr_non),
            "ls_files_others_non_planning_paths": untr_non,
            "git_status_used": False,
            "git_write_used": False,
        },
        "note": "this file is written after handoff.json, so handoff.json cannot "
                "contain this file's sha256; it is the last artifact of the card",
    }
    out = os.path.abspath(args.out)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    raw = open(out, "rb").read()
    json.loads(raw.decode("utf-8"))
    print("all_checks_pass=%s" % doc["all_checks_pass"])
    for k, v in checks.items():
        if not v:
            print("  FAIL: %s" % k)
    print("git diff non-planning=%d  untracked non-planning=%d"
          % (len(diff_non), len(untr_non)))
    print("final_verification.json bytes=%d sha256=%s"
          % (len(raw), hashlib.sha256(raw).hexdigest()))
    return 0 if doc["all_checks_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
