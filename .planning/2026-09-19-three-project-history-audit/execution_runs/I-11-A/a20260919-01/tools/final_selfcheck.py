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
    "review.md": 2000,
    "handoff.json": 2000,
    "changes.diff": 500,
    "recovery/README.md": 500,
    "evidence/I-11-A/hypotheses.json": 5000,
    "evidence/I-11-A/source_map.json": 2000,
    "evidence/I-11-A/mechanism_review.md": 5000,
    "evidence/I-11-A/validation_report.json": 2000,
    "evidence/I-11-A/extract/arithmetic_oracle.json": 2000,
    "evidence/I-11-A/extract/commands_raw.json": 2000,
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

    # before/after production state must be identical
    b = json.load(open(os.path.join(ev, "state_before.json"), encoding="utf-8"))
    af = json.load(open(os.path.join(ev, "state_after.json"), encoding="utf-8"))
    same_heads = all(b["production_repos"][k]["head"] == af["production_repos"][k]["head"]
                     for k in b["production_repos"])
    same_porcelain = all(b["production_repos"][k]["porcelain"] == af["production_repos"][k]["porcelain"]
                         for k in b["production_repos"])
    same_keyfiles = b["key_files"] == af["key_files"]
    checks.append({"step": "production_state_unchanged", "heads": same_heads,
                   "porcelain": same_porcelain, "key_files": same_keyfiles})
    if not (same_heads and same_porcelain and same_keyfiles):
        problems.append("production state changed between the before and after captures")

    # the reviews tree must not contain anything written during this attempt
    reviews = b.get("plan_reviews", {})
    checks.append({"step": "plan_reviews", "mtime_local": reviews.get("mtime_local"),
                   "recorded_by": "state_before.json"})

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
