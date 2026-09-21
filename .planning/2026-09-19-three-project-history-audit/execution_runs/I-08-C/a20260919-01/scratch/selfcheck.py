"""I-08-C r3 self-check: JSON validity + every hash quoted in handoff.json re-verified
against the files on disk. Read-only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent
errors: list[str] = []
checked = 0


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# 1. every JSON in the attempt must parse (utf-8-sig tolerant)
for p in sorted(D.rglob("*.json")):
    if any(part in {".pytest_cache", "runner"} for part in p.parts):
        continue
    try:
        json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"JSON parse failed: {p.relative_to(D)}: {exc}")

# 2. handoff.json deliverable hashes must match disk
h = json.loads((D / "handoff.json").read_text(encoding="utf-8-sig"))
for name, expected in h["deliverables"].items():
    if expected.startswith("self"):
        continue
    f = D / name
    if not f.exists():
        errors.append(f"handoff.deliverables lists a missing file: {name}")
        continue
    actual = sha(f)
    checked += 1
    if actual != expected:
        errors.append(f"hash mismatch {name}: handoff={expected} disk={actual}")

# 3. oracle byte count + hash quoted in handoff must match disk
o = D / "oracle.md"
if o.stat().st_size != h["append_only_proof"]["oracle_bytes"]:
    errors.append("oracle byte count mismatch")
if sha(o) != h["append_only_proof"]["oracle_sha256"]:
    errors.append("oracle sha256 mismatch")

# 4. frozen body must still hash to the r2 digest and be a prefix of oracle.md
body = o.read_bytes()[: h["append_only_proof"]["frozen_body_bytes"]]
if sha(D / "oracle.md.r2_frozen_copy.txt") != h["append_only_proof"]["frozen_body_sha256_recorded_r2"]:
    errors.append("frozen copy hash mismatch")
if hashlib.sha256(body).hexdigest() != h["append_only_proof"]["frozen_body_sha256_on_disk_now"]:
    errors.append("frozen body prefix hash mismatch")
if not o.read_bytes().startswith(body):
    errors.append("oracle.md no longer starts with the frozen body")

# 5. the frozen test file must still be the executed one (byte + hash)
t = D / "test_i08c_consumer_rejection.py"
if t.stat().st_size != 10902 or sha(t) != h["deliverables"]["test_i08c_consumer_rejection.py"]:
    errors.append("test file changed after the frozen run")

# 6. pinned product gaps must still be pinned as rc=3 in the case table
rc = {c["case"]: c["business_rc"] for c in h["case_results"]}
for case in ("E11", "E13"):
    if rc.get(case) != 3:
        errors.append(f"{case} is not classified rc=3 (pinned gap)")
if len(h["case_results"]) != 13:
    errors.append("case_results is not the frozen 13-case matrix")

# 7. status must NOT be accepted
if h["status"] != "changes_required" or h["reviewer_verdict"] != "changes_required":
    errors.append("handoff status/verdict is not changes_required")
if h["implementer_self_acceptance"] is not False:
    errors.append("implementer_self_acceptance must be false")

# 8. required_by_reviewer must carry the reviewer's four closing items
nums = sorted(x["n"] for x in h["required_by_reviewer"])
if nums != [1, 2, 3, 4]:
    errors.append(f"required_by_reviewer items are {nums}, expected [1,2,3,4]")

out = {
    "json_files_parsed_ok": True,
    "handoff_deliverable_hashes_checked": checked,
    "oracle_bytes": o.stat().st_size,
    "oracle_sha256": sha(o),
    "errors": errors,
    "self_check": "PASS" if not errors else "FAIL",
}
print(json.dumps(out, indent=2))
raise SystemExit(1 if errors else 0)
