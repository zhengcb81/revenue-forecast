#!/usr/bin/env python3
"""I-13-A 只读校验器（oracle §7 冻结）。

exit code legend (frozen):
  0 = ALL_INVARIANTS_OK
  1 = harness failure (missing file / unparsable JSON)
  2 = never produced by this verifier
  3 = invariant violation (named J1..J5)

usage: python _verify_i13a.py --root <attempt_dir> --plan <plan_root>
"""
import argparse
import hashlib
import io
import json
import os
import sys

HARNESS = 1
VIOLATION = 3

FORBIDDEN_TOKENS = ["consumed_for_forecast"]
REDLINE_NUMBERS = [124248.63]
REDLINE_STRINGS = ["124,248.63", "124248.63"]
REDLINE_CONTEXT = r"registered_not_consumed|只登记|禁消费|登记|存档|不含|未消费"
# Lines that merely *describe* the ban/mutation (rule text) are not consumption claims.
BAN_RULE_CONTEXT = r"不得出现|模拟|内塞|FORBIDDEN|forbidden|无\s*consumed|token|禁止"
ALLOWED_CLASSIFICATION = {
    "blocked",
    "research_draft_needs_review",
    "buy_side_review_ready",
}
ALLOWED_DISPOSITION = {"established", "not_established"}
REQUIRED_FILES = [
    os.path.join("evidence", "I-13-A", "buy_side_scorecard.json"),
    os.path.join("evidence", "I-13-A", "blocking_issues.json"),
    os.path.join("evidence", "I-13-A", "artifact_references.json"),
    "verification.json",
    "handoff.json",
]


def load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_strings(node, path=""):
    if isinstance(node, dict):
        for key, val in node.items():
            for item in walk_strings(val, path + "/" + str(key)):
                yield item
    elif isinstance(node, list):
        for idx, val in enumerate(node):
            for item in walk_strings(val, path + "[%d]" % idx):
                yield item
    elif isinstance(node, str):
        yield path, node
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        yield path, node


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--plan", required=True)
    args = ap.parse_args()

    import re

    violations = []
    loaded = {}

    # ---------- harness ----------
    for rel in REQUIRED_FILES:
        full = os.path.join(args.root, rel)
        if not os.path.isfile(full):
            print("HARNESS: missing %s" % full)
            return HARNESS
        try:
            loaded[rel] = load(full)
        except Exception as exc:  # noqa: BLE001
            print("HARNESS: unparsable %s (%s)" % (rel, exc))
            return HARNESS

    handoff = loaded["handoff.json"]
    verification = loaded["verification.json"]
    scorecard = loaded[os.path.join("evidence", "I-13-A", "buy_side_scorecard.json")]
    blocking = loaded[os.path.join("evidence", "I-13-A", "blocking_issues.json")]
    references = loaded[os.path.join("evidence", "I-13-A", "artifact_references.json")]

    # ---------- J1 release / authority lock ----------
    j1 = []
    if handoff.get("params_released") is not False:
        j1.append("handoff.params_released != false")
    if handoff.get("implementer_signed") is not False:
        j1.append("handoff.implementer_signed != false")
    if handoff.get("releases_nothing") is not True:
        j1.append("handoff.releases_nothing != true")
    if handoff.get("status") != "review_pending":
        j1.append("handoff.status != review_pending")
    if handoff.get("gate0_passed") is not True:
        j1.append("handoff.gate0_passed != true")
    if handoff.get("git_diff_non_planning") != 0:
        j1.append("handoff.git_diff_non_planning != 0")
    if handoff.get("open2_ban_observed") is not True:
        j1.append("handoff.open2_ban_observed != true")
    if handoff.get("role") != "implementer_i13a":
        j1.append("handoff.role != implementer_i13a")
    if not isinstance(handoff.get("authorized_by"), dict) or not handoff.get("authorized_by"):
        j1.append("handoff.authorized_by missing/empty")
    if not handoff.get("gate0_raw_output"):
        j1.append("handoff.gate0_raw_output missing")
    if not handoff.get("written_files"):
        j1.append("handoff.written_files missing")
    boundary = handoff.get("boundary_self_declaration", {})
    for flag in ("no_auto_actions", "no_falsifier_triggered", "five_plan_files_untouched"):
        if boundary.get(flag) is not True:
            j1.append("boundary.%s != true" % flag)
    if boundary.get("writes_outside_planning") != 0:
        j1.append("boundary.writes_outside_planning != 0")
    if boundary.get("git_writes") != 0:
        j1.append("boundary.git_writes != 0")
    if boundary.get("git_status_run") is not False:
        j1.append("boundary.git_status_run != false")
    if boundary.get("network_used") is not False:
        j1.append("boundary.network_used != false")
    for item in j1:
        print("VIOLATION J1: %s" % item)

    # ---------- J2 scorecard rule ----------
    j2 = []
    dims = scorecard.get("dimensions") or []
    if len(dims) != 8:
        j2.append("dimensions count = %d (expected 8)" % len(dims))
    scores = []
    for dim in dims:
        sid = dim.get("id", "?")
        sc = dim.get("score")
        if sc not in (0, 1, 2):
            j2.append("%s.score=%r not in {0,1,2}" % (sid, sc))
        else:
            scores.append(sc)
        ev = dim.get("evidence") or []
        if not ev:
            j2.append("%s has no evidence refs" % sid)
        elif not any(isinstance(e, str) and re.search(r"( L\d+|:\d+)", e) for e in ev):
            j2.append("%s evidence lacks path:line reference" % sid)
    total = scorecard.get("total")
    if scores and total != sum(scores):
        j2.append("total=%r != sum(scores)=%d" % (total, sum(scores)))
    if scorecard.get("total_max") != 16:
        j2.append("total_max != 16")
    zeros = sum(1 for s in scores if s == 0)
    if scorecard.get("zeros_present") != zeros:
        j2.append("zeros_present=%r != %d" % (scorecard.get("zeros_present"), zeros))
    if scorecard.get("total_is_display_only") is not True:
        j2.append("total_is_display_only != true (total must not be an auto-release threshold)")

    hb = blocking.get("hard_blocks") or []
    if len(hb) != 7:
        j2.append("hard_blocks count = %d (expected 7)" % len(hb))
    dispositions = []
    for issue in hb:
        iid = issue.get("id", "?")
        disp = issue.get("disposition")
        if disp not in ALLOWED_DISPOSITION:
            j2.append("%s.disposition=%r invalid" % (iid, disp))
        else:
            dispositions.append(disp)
        if disp == "established":
            for key in ("reproducible_sample", "impact", "required_fix"):
                if not issue.get(key):
                    j2.append("%s established but missing %s" % (iid, key))
        else:
            for key in ("basis", "counter_evidence"):
                if not issue.get(key):
                    j2.append("%s not_established but missing %s" % (iid, key))

    if dispositions:
        if "established" in dispositions:
            expected_class = "blocked"
        elif zeros > 0:
            expected_class = "blocked"
        elif any(s == 1 for s in scores):
            expected_class = "research_draft_needs_review"
        else:
            expected_class = "buy_side_review_ready"
        observed_class = scorecard.get("classification")
        if observed_class != expected_class:
            j2.append(
                "classification=%r but rule-derived=%r (zeros=%d, established=%d)"
                % (observed_class, expected_class, zeros, dispositions.count("established"))
            )
        if observed_class not in ALLOWED_CLASSIFICATION:
            j2.append("classification=%r not allowed" % observed_class)
        listed = sorted(blocking.get("established_hard_blocks") or [])
        actual = sorted(i.get("id") for i in hb if i.get("disposition") == "established")
        if listed != actual:
            j2.append("established_hard_blocks %r != actual %r" % (listed, actual))
        if observed_class == "buy_side_review_ready" and "established" in dispositions:
            j2.append("buy_side_review_ready granted despite hard block")
        if observed_class == "buy_side_review_ready" and zeros > 0:
            j2.append("buy_side_review_ready granted despite zero score")
    for item in j2:
        print("VIOLATION J2: %s" % item)

    # ---------- J3 OPEN-2 ban ----------
    j3 = []
    ctx_re = re.compile(REDLINE_CONTEXT)
    for rel in REQUIRED_FILES:
        text = io.open(os.path.join(args.root, rel), encoding="utf-8").read()
        for token in FORBIDDEN_TOKENS:
            if token in text:
                rule_re = re.compile(BAN_RULE_CONTEXT)
                offenders = [
                    ln for ln in text.splitlines()
                    if token in ln and not rule_re.search(ln)
                ]
                if offenders:
                    j3.append(
                        "%s contains consumption claim token %r on line: %s"
                        % (rel, token, offenders[0].strip()[:120])
                    )
        for path, val in walk_strings(load(os.path.join(args.root, rel))):
            if isinstance(val, float) and any(abs(val - n) < 1e-9 for n in REDLINE_NUMBERS):
                j3.append("%s%s is numeric red-line value %r (must be registration text only)" % (rel, path, val))
            if isinstance(val, str):
                for needle in REDLINE_STRINGS:
                    if needle in val and not ctx_re.search(val):
                        j3.append("%s%s cites red-line value without registration context" % (rel, path))
    if scorecard.get("classification") == "buy_side_review_ready":
        j3.append("ready label while OPEN-2 red line still in force")
    for item in j3:
        print("VIOLATION J3: %s" % item)

    # ---------- J4 upstream sha ----------
    j4 = []
    for entry in verification.get("upstream_inputs") or []:
        rel = entry.get("path")
        full = os.path.join(args.plan, rel)
        if not os.path.isfile(full):
            j4.append("upstream missing: %s" % rel)
            continue
        actual = sha256(full)
        if actual != entry.get("sha256"):
            j4.append(
                "sha mismatch %s recorded=%s actual=%s"
                % (rel, entry.get("sha256"), actual)
            )
        if os.path.getsize(full) != entry.get("bytes"):
            j4.append("bytes mismatch %s recorded=%r actual=%d" % (rel, entry.get("bytes"), os.path.getsize(full)))
    for item in j4:
        print("VIOLATION J4: %s" % item)

    # ---------- J5 evidence completeness ----------
    j5 = []
    if not references.get("upstream_artifacts"):
        j5.append("artifact_references.upstream_artifacts empty")
    if references.get("not_referenced_by_design") is None:
        j5.append("artifact_references.read-scope declaration missing")
    for company in references.get("companies") or []:
        if not company.get("refs"):
            j5.append("%s has no refs" % company.get("company", "?"))
        if not company.get("fields"):
            j5.append("%s has no field table" % company.get("company", "?"))
    stop = scorecard.get("stop_conditions") or {}
    if not stop.get("hard_block_stop"):
        j5.append("scorecard.stop_conditions.hard_block_stop missing")
    if "HB3" not in str(stop.get("accuracy_unproven_stop", "")):
        j5.append("scorecard must state blocked is NOT based on accuracy=unproven (card L20)")
    if scorecard.get("rubric_source", {}).get("buy_side_dimensions") is None:
        j5.append("scorecard.rubric_source missing")
    for item in j5:
        print("VIOLATION J5: %s" % item)

    if violations or j1 or j2 or j3 or j4 or j5:
        print("RESULT: FAIL (%d violations)" % (len(j1) + len(j2) + len(j3) + len(j4) + len(j5)))
        return VIOLATION
    print("CHECK J1-J5 all OK")
    print("RESULT ALL_INVARIANTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
