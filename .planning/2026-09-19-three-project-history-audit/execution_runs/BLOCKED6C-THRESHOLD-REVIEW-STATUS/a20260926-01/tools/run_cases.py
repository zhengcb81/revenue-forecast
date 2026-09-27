"""BLOCKED6C-THRESHOLD-REVIEW-STATUS case runner.

Read-only runner: it imports a target copy of validate_hypotheses.py by path and
reports, for (a) the frozen positive case, (b) the pre-registered counterexamples
CE-22..CE-25 of this card's oracle section 4, and (c) the target's own frozen
counterexample suite, whether each expected error code was observed.

Nothing here patches anything; it only calls validate() and reports rc-equivalent
verdicts. Exit code 0 means "run completed", the verdict lives in the JSON.

Usage:
  python -X utf8 -B tools/run_cases.py --validator <path to validate_hypotheses.py>
      --attempt <attempt root> --out <report.json> [--expect-red|--expect-green]
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import sys


def load_module(path):
    spec = importlib.util.spec_from_file_location("vh_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_ce22_25(hypotheses):
    """Pre-registered counterexamples, oracle.md section 4 (frozen, hand-written)."""
    base = next(h for h in hypotheses if h["hypothesis_id"] == "H-CN-ZIJIN-SEG-01")
    cases = []

    # CE-22: threshold_basis present, threshold_review_status outside the closed set
    h = copy.deepcopy(base)
    h["falsifier"]["threshold_review_status"] = "approved"
    cases.append(("CE-22", "E_THRESHOLD_REVIEW_STATUS_UNKNOWN",
                  "threshold_review_status outside the closed set "
                  "(threshold_basis still present)", [h]))

    # CE-23: threshold_review_status claims "reviewed" with no A-6.3 seal
    h = copy.deepcopy(base)
    h["falsifier"]["threshold_review_status"] = "reviewed"
    h["decision"] = {}
    cases.append(("CE-23", "E_THRESHOLD_REVIEW_STATUS_UNSEALED",
                  "threshold_review_status=reviewed without decision.decision_sha256 "
                  "and without a substantive reviewer seal", [h]))

    # CE-24: threshold_basis present, threshold_review_status MISSING, but the
    # proposition is consumed as approved (state=approved_frozen) -> the exact
    # counterexample named by the dispatch (step 3).
    h = copy.deepcopy(base)
    h["state"] = "approved_frozen"
    h["reviewer"] = "Independent Accounting Reviewer"
    h["decision"] = {"decision_sha256": "a" * 64}
    cases.append(("CE-24", "E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED",
                  "threshold_basis present, threshold_review_status MISSING, "
                  "yet state=approved_frozen (used as reviewed)", [h]))

    # CE-25: same, but threshold_review_status explicitly = not_reviewed
    h = copy.deepcopy(base)
    h["state"] = "approved_frozen"
    h["reviewer"] = "Independent Accounting Reviewer"
    h["decision"] = {"decision_sha256": "a" * 64}
    h["falsifier"]["threshold_review_status"] = "not_reviewed"
    cases.append(("CE-25", "E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED",
                  "threshold_basis present, threshold_review_status explicitly "
                  "not_reviewed, yet state=approved_frozen (used as reviewed)", [h]))

    return cases


def run(mod, hypotheses, source_map, attempt, doc_texts, cases, tag):
    out = []
    for item in cases:
        if tag == "own":
            code, note, patched = item
            cid = "OWN-%02d" % (len(out) + 1)
        else:
            cid, code, note, patched = item
        if code == "E_LISTED_VALUE_NOT_IN_EVIDENCE":
            sm = copy.deepcopy(source_map)
            sm["documents"].append({
                "doc_id": "CE-DOC", "doc_sha256": "f" * 64,
                "extraction_output_path": "evidence/I-11-A/hypotheses.json",
                "cited_values": [{"key": "ce", "raw": "999,999,999", "page": 1,
                                  "raw_label": "counterexample value"}],
                "narrative_facts": [],
            })
            errs = mod.validate(patched, sm, attempt, doc_texts)
        else:
            errs = mod.validate(patched, source_map, attempt, doc_texts)
        got = sorted({e["code"] for e in errs})
        out.append({
            "case_id": cid,
            "expected_code": code,
            "note": note,
            "observed_codes": got,
            "rejected": code in got,
            "errors": errs,
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validator", required=True)
    ap.add_argument("--attempt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--phase", default="run")
    args = ap.parse_args()

    mod = load_module(args.validator)
    ev = os.path.join(args.attempt, "evidence", "I-11-A")
    hypotheses = json.load(open(os.path.join(ev, "hypotheses.json"), encoding="utf-8"))
    source_map = json.load(open(os.path.join(ev, "source_map.json"), encoding="utf-8"))
    doc_texts = {}
    for d in source_map["documents"]:
        p = os.path.join(args.attempt, d["extraction_output_path"])
        doc_texts[d["doc_id"]] = open(p, encoding="utf-8").read()
        npath = d.get("narrative_text_path")
        if npath:
            doc_texts[d["doc_id"] + "::narrative"] = open(
                os.path.join(args.attempt, npath), encoding="utf-8").read()

    positive = mod.validate(hypotheses, source_map, args.attempt, doc_texts)

    ce_new = build_ce22_25(hypotheses)
    new_results = run(mod, hypotheses, source_map, args.attempt, doc_texts, ce_new, "ce")

    own_cases = mod.make_counterexamples(hypotheses)
    own_results = run(mod, hypotheses, source_map, args.attempt, doc_texts, own_cases, "own")
    for r, item in zip(own_results, own_cases):
        r["note"] = item[1]
        r["is_new_b6c_case"] = str(item[1]).startswith("[B6C]")
    original = [r for r in own_results if not r["is_new_b6c_case"]]
    added = [r for r in own_results if r["is_new_b6c_case"]]

    report = {
        "phase": args.phase,
        "validator": args.validator.replace("\\", "/"),
        "attempt": args.attempt.replace("\\", "/"),
        "positive_case": {
            "propositions_checked": len(hypotheses),
            "errors": positive,
            "verdict": "pass" if not positive else "fail",
        },
        "card_counterexamples_ce22_ce25": new_results,
        "ce_summary": {
            "cases": len(new_results),
            "rejected": sum(1 for r in new_results if r["rejected"]),
            "accepted": sum(1 for r in new_results if not r["rejected"]),
            "accepted_ids": [r["case_id"] for r in new_results if not r["rejected"]],
        },
        "target_suite": {
            "total": len(own_results),
            "original_21_total": len(original),
            "original_21_rejected": sum(1 for r in original if r["rejected"]),
            "original_21_accepted_ids": [r["case_id"] for r in original if not r["rejected"]],
            "original_21_notes": [r["note"] for r in original],
            "new_b6c_total": len(added),
            "new_b6c_rejected": sum(1 for r in added if r["rejected"]),
            "new_b6c_accepted_ids": [r["case_id"] for r in added if not r["rejected"]],
            "rejected_as_expected": sum(1 for r in own_results if r["rejected"]),
            "accepted_by_mistake": sum(1 for r in own_results if not r["rejected"]),
            "accepted_by_mistake_notes": [r["note"] for r in own_results if not r["rejected"]],
            "cases": len(own_results),
        },
        "all_cases": own_results,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print("phase=%s validator=%s" % (args.phase, report["validator"]))
    print("positive_case: %s (%d errors)" % (report["positive_case"]["verdict"], len(positive)))
    for r in new_results:
        print("  %-6s expect=%-42s rejected=%-5s observed=%s"
              % (r["case_id"], r["expected_code"], r["rejected"], ",".join(r["observed_codes"]) or "-"))
    print("  CE summary: %d/%d rejected (accepted=%s)"
          % (report["ce_summary"]["rejected"], report["ce_summary"]["cases"],
             report["ce_summary"]["accepted_ids"]))
    ts = report["target_suite"]
    print("  target suite: total=%d original_21_rejected=%d new_b6c_rejected=%d "
          "rejected_as_expected=%d accepted_by_mistake=%d"
          % (ts["total"], ts["original_21_rejected"], ts["new_b6c_rejected"],
             ts["rejected_as_expected"], ts["accepted_by_mistake"]))
    if ts["original_21_accepted_ids"]:
        print("  ORIGINAL-21 ACCEPTED (regression): %s" % ts["original_21_accepted_ids"])
    # rc semantics for this card: 0 = run completed and no counterexample was
    # accepted by the target validator; 1 = at least one counterexample leaked.
    leak = report["ce_summary"]["accepted"] + ts["accepted_by_mistake"]
    return 0 if leak == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
