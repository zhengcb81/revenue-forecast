"""I-11-A: final completeness self-check of this attempt (not a verdict).

Re-runs the two content validators and compares the captured production state, so
the delivered package cannot claim completeness while an artifact is stale.

Usage: python -X utf8 -B tools/final_selfcheck.py <attempt_root>
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

MIN_BYTES = {
    "binding.json": 2000,
    "oracle.md": 5000,
    "decision.md": 8000,
    "commands.json": 3000,
    "review.md": 10000,
    "handoff.json": 2000,
    "changes.diff": 1500,
    "recovery/README.md": 500,
    "before/README.md": 500,
    "after/README.md": 500,
    "evidence/I-11-A/hypotheses.json": 5000,
    "evidence/I-11-A/source_map.json": 2000,
    "evidence/I-11-A/mechanism_review.md": 5000,
    "evidence/I-11-A/validation_report.json": 2000,
    "evidence/I-11-A/extract/arithmetic_oracle.json": 2000,
    "evidence/I-11-A/extract/commands_raw.json": 2000,
    "evidence/I-11-A/extract/P1_xiaomi_content_probe.json": 500,
    "evidence/I-11-A/attempt_hashes.json": 2000,
    "evidence/I-11-A/state_before.json": 1000,
    "evidence/I-11-A/state_after.json": 1000,
}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    attempt = sys.argv[1]
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    ev = os.path.join(attempt, "evidence", "I-11-A")
    problems = []
    checks = []

    for rel, min_bytes in MIN_BYTES.items():
        p = os.path.join(attempt, rel)
        if not os.path.exists(p):
            problems.append("missing artifact: %s" % rel)
            continue
        size = os.path.getsize(p)
        ok = size >= min_bytes
        checks.append({"artifact": rel, "byte_size": size, "min_bytes": min_bytes, "ok": ok,
                       "sha256": sha256(p)})
        if not ok:
            problems.append("artifact below minimum size (possible placeholder): %s (%d < %d)"
                            % (rel, size, min_bytes))

    # re-run the content validators
    v = subprocess.run([py, "-X", "utf8", "-B", os.path.join(attempt, "tools", "validate_hypotheses.py"),
                        attempt, os.path.join(ev, "validation_report.json"),
                        os.path.join(ev, "validation_report.ascii.txt")], capture_output=True)
    checks.append({"step": "validate_hypotheses", "returncode": v.returncode})
    if v.returncode != 0:
        problems.append("validate_hypotheses.py returned %d" % v.returncode)
    a = subprocess.run([py, "-X", "utf8", "-B", os.path.join(attempt, "tools", "verify_arithmetic.py"),
                        os.path.join(ev, "extract", "arithmetic_oracle.json")], capture_output=True)
    checks.append({"step": "verify_arithmetic", "returncode": a.returncode})
    if a.returncode != 0:
        problems.append("verify_arithmetic.py returned %d" % a.returncode)

    # the two state captures: they must be DISTINCT captures; HEAD and key-file
    # hashes must match; porcelain is expected to move because the owner/parent
    # commit concurrently. Identical-surface-porcelain is therefore NOT required,
    # and the identical result is reported as time-bracketed rather than as a
    # pre-work/post-work proof (finding P1-1).
    b = json.load(open(os.path.join(ev, "state_before.json"), encoding="utf-8"))
    af = json.load(open(os.path.join(ev, "state_after.json"), encoding="utf-8"))
    distinct = (b.get("captured_at_utc") != af.get("captured_at_utc")
                or b.get("sequence") != af.get("sequence"))
    same_heads = all(b["production_repos"][k]["head"] == af["production_repos"][k]["head"]
                     for k in b["production_repos"])
    same_keyfiles = b["key_files"] == af["key_files"]
    cmp_block = (af.get("capture_comparison") or b.get("capture_comparison") or {})
    audit_changes = cmp_block.get("porcelain_changes_inside_this_audits_execution_runs", [])
    production_changes = cmp_block.get("porcelain_changes_outside_the_audit_tree_PROBLEM_IF_ANY", [])
    checks.append({
        "step": "state_captures",
        "captures_are_distinct": distinct,
        "capture_1_utc": b.get("captured_at_utc"),
        "capture_2_utc": af.get("captured_at_utc"),
        "heads_identical_between_captures": same_heads,
        "key_files_identical_between_captures": same_keyfiles,
        "porcelain_changes_inside_the_audit_tree": len(audit_changes),
        "porcelain_changes_outside_the_audit_tree": production_changes,
        "porcelain_diff": cmp_block.get("porcelain_diff"),
        "claim_boundary": ("the two captures were both taken during this attempt and porcelain is expected "
                           "to move while other actors commit; this is NOT a pre-work baseline comparison "
                           "and does not by itself prove that production was untouched by this card "
                           "(finding P1-1). What it does show is that no porcelain entry OUTSIDE this "
                           "audit's execution_runs tree changed, and that HEAD/key-file hashes are stable."),
    })
    if not distinct:
        problems.append("the two state captures share one timestamp: they are not distinct captures")
    if not same_heads:
        problems.append("HEAD moved between the two state captures (see porcelain_diff for who moved it)")
    if not same_keyfiles:
        problems.append("a key production file's sha256 changed between the two state captures")
    if production_changes:
        problems.append("a porcelain entry OUTSIDE this audit tree changed between captures "
                        "(a production-repo write happened): %s" % production_changes)

    # the reviews tree: report who is the newest file and how many were listed
    reviews = b.get("plan_reviews", {})
    checks.append({"step": "plan_reviews", "mtime_local": reviews.get("mtime_local"),
                   "file_count": reviews.get("file_count"),
                   "newest_file": reviews.get("newest_file"),
                   "recorded_by": "state_before.json / state_after.json"})
    if not reviews.get("file_count"):
        problems.append("plan_reviews listing is missing or empty")

    # production repos are not tracked as modified by THIS attempt: only report, do
    # not assert, because other actors commit to these repositories concurrently.
    checks.append({
        "step": "production_write_attribution",
        "attempt_own_writes_to_production": [],
        "note": ("this attempt's tools only read production paths; the only write root bound in "
                 "binding.json is this attempt directory. Concurrent commits by the owner/parent "
                 "(e.g. ddc81ab at 2026-09-20 04:09 local) change HEAD and porcelain afterwards and "
                 "must not be read as this card's writes."),
    })

    report = {
        "attempt_id": "a20260919-01",
        "card_id": "I-11-A",
        "generated_by": "tools/final_selfcheck.py",
        "checks": checks,
        "problems": problems,
        "verdict": "complete_for_review" if not problems else "incomplete",
        "note": ("This is an implementer self-check. It is NOT an acceptance verdict and grants no "
                 "qualification; independent review is required."),
    }
    out = os.path.join(ev, "final_selfcheck.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    for p in problems:
        print("PROBLEM:", p.encode("ascii", "replace").decode("ascii"))
    print("verdict:", report["verdict"], "problems:", len(problems))
    print("wrote", out)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
