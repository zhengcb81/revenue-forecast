"""I-11-A: freeze the semantics of the two state captures (post-review correction).

WHY THIS FILE CHANGED AFTER REVIEW
----------------------------------
The independent reviewer found (finding P1-1) that `state_before.json` and
`state_after.json` carried the SAME `captured_at_utc` value, i.e. they were not two
captures but one capture echoed into two files by the first version of this script.
That made the "production unchanged" comparison trivially true and let the
documentation imply a pre-work baseline that never existed (the capture timestamp was
also later than this attempt directory's creation time).

Corrected semantics applied here:
  * both files declare their role explicitly (`state_capture_1` / `state_capture_2`);
    the on-disk names are kept because other artifacts reference them;
  * the pair is declared to be two snapshots taken DURING this attempt, not a
    pre-work/post-work pair;
  * the load-bearing claim - this card did not write to the three production
    repositories - is NOT carried by this pair. It rests on the independent review
    (review.md section 5) and on the fact that this card changes no product file.
    That boundary is written into both files.

Usage: python -X utf8 -B tools/finalize_state.py <attempt_root>
"""

from __future__ import annotations

import json
import os
import sys

CLAIM = ("This pair of captures does NOT by itself establish 'production unchanged': both were taken "
         "during this attempt (see capture_timeline.attempt_dir_created_local), so they bracket the "
         "close-out, not the work. The card writes nothing to the production repositories; the "
         "zero-write claim is supported by the independent review (review.md section 5) and by the "
         "absence of any write path to those repositories in this attempt's tools. See review finding "
         "P1-1 and decision.md DEC-13.")


def main() -> int:
    attempt = sys.argv[1]
    ev = os.path.join(attempt, "evidence", "I-11-A")
    b_path = os.path.join(ev, "state_before.json")
    a_path = os.path.join(ev, "state_after.json")
    b = json.load(open(b_path, encoding="utf-8"))
    a = json.load(open(a_path, encoding="utf-8"))

    b["capture_role"] = "state_capture_1 (file name kept for compatibility; NOT a pre-work baseline)"
    a["capture_role"] = "state_capture_2 (file name kept for compatibility; NOT a post-work baseline)"
    b["attempt_inventory_removed"] = {
        "removed_count": len(b.pop("attempt_inventory", [])),
        "reason": ("the first capture was taken after this attempt's tools/ already existed, so its "
                   "directory listing is not a pre-work baseline; the attempt's own inventory is kept "
                   "only in state_after.json as a close-out listing"),
    }
    b.pop("attempt_file_count", None)
    a["attempt_inventory_scope"] = ("close-out inventory of this attempt's own files (iso/venv excluded); "
                                    "informational, not part of any before/after comparison")

    same_ts = (b.get("captured_at_utc") == a.get("captured_at_utc")
               and b.get("sequence") == a.get("sequence"))
    heads = {k: (b["production_repos"][k]["head"], a["production_repos"][k]["head"])
             for k in b["production_repos"]}
    heads_identical = all(x == y for x, y in heads.values())
    key_files_identical = b["key_files"] == a["key_files"]
    reviews_identical = b.get("plan_reviews") == a.get("plan_reviews")

    # Porcelain is NOT expected to be stable: other actors (the owner, the parent
    # session, other cards) commit to these repositories concurrently. What matters
    # is (a) whether HEAD moved, (b) WHICH entries changed, so that any write by
    # this attempt would be visible. The attempt's own writes must be none.
    porcelain_diff = {}
    for name in b["production_repos"]:
        pb = set(b["production_repos"][name]["porcelain"])
        pa = set(a["production_repos"][name]["porcelain"])
        porcelain_diff[name] = {
            "count_capture_1": len(pb),
            "count_capture_2": len(pa),
            "appeared_between_captures": sorted(pa - pb)[:20],
            "disappeared_between_captures": sorted(pb - pa)[:20],
            "identical": pb == pa,
        }
    # Any changed porcelain entry whose path lies INSIDE this audit's execution_runs
    # tree is this card's own artifact surface (the attempt directory is tracked in
    # git since commit ddc81ab). Entries OUTSIDE that tree are production files and
    # must never be touched by this card.
    ATTEMPT_SCOPE = ".planning/2026-09-19-three-project-history-audit/execution_runs/"
    attempt_path_changes = []
    production_path_changes = []
    for name, d in porcelain_diff.items():
        for entry in d["appeared_between_captures"] + d["disappeared_between_captures"]:
            path = entry[3:].strip() if len(entry) > 3 else entry
            (attempt_path_changes if path.startswith(ATTEMPT_SCOPE) else
             production_path_changes).append({name: entry})

    comparison = {
        "captures_are_distinct": not same_ts,
        "capture_1_utc": b.get("captured_at_utc"),
        "capture_2_utc": a.get("captured_at_utc"),
        "heads_identical": heads_identical,
        "heads": heads,
        "key_files_identical": key_files_identical,
        "plan_reviews_identical": reviews_identical,
        "porcelain_diff": porcelain_diff,
        "porcelain_changes_inside_this_audits_execution_runs": attempt_path_changes,
        "porcelain_changes_outside_the_audit_tree_PROBLEM_IF_ANY": production_path_changes,
        "production_repos_interesting_identity": ("head + key_files (porcelain is expected to move: the "
                                                  "owner/parent commit concurrently - see the review "
                                                  "finding P1-1 and decision.md DEC-13)"),
        "claim_boundary": CLAIM,
    }
    for rec in (b, a):
        rec["capture_comparison"] = comparison

    with open(b_path, "w", encoding="utf-8") as fh:
        json.dump(b, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with open(a_path, "w", encoding="utf-8") as fh:
        json.dump(a, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    print("captures distinct:", comparison["captures_are_distinct"],
          "| capture_1:", comparison["capture_1_utc"], "| capture_2:", comparison["capture_2_utc"])
    print("heads identical:", comparison["heads_identical"],
          "| key files:", comparison["key_files_identical"],
          "| reviews listing:", comparison["plan_reviews_identical"])
    for name, d in porcelain_diff.items():
        print("  %-18s porcelain %d -> %d (appeared %d, disappeared %d)"
              % (name, d["count_capture_1"], d["count_capture_2"],
                 len(d["appeared_between_captures"]), len(d["disappeared_between_captures"])))
    print("porcelain entries inside the audit's execution_runs:",
          len(comparison["porcelain_changes_inside_this_audits_execution_runs"]))
    print("porcelain entries OUTSIDE the audit tree (must be none):",
          comparison["porcelain_changes_outside_the_audit_tree_PROBLEM_IF_ANY"])
    print("wrote", b_path, "and", a_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
