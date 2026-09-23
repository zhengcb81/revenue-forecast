"""GUARD-MERGE battery (v) — P5-b disposal-gate mutation.

Removes the disposal gate from the merged ``prompt_injection.py`` face
installed in the I-06-B harness arm, runs case J (its frozen expectations:
every unauthorised ``detected_and_ignored`` write must be refused with a
``disposal authorization unavailable:`` literal), restores the merged face,
and re-runs J to confirm GREEN.

Usage: python run_mutation_disposal.py <attempt_dir>
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

A = pathlib.Path(sys.argv[1])
ARM_PI = A / "iso" / "fixed" / "fixed_pi" / "prompt_injection.py"
BASE_PI = A / "iso" / "prompt_injection.py"
RUNNER = A / "scripts" / "run_cases.py"
EVID = A / "evidence" / "raw"

base = BASE_PI.read_bytes()
assert hashlib.sha256(base).hexdigest() == \
    "88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33"
text = base.decode("utf-8")
anchor = '    if status == "detected_and_ignored":\n        disposal_fields = _disposal_gate('
mutant_anchor = '    if False and status == "detected_and_ignored":\n        disposal_fields = _disposal_gate('
assert text.count(anchor) == 1, text.count(anchor)


def run_j(tag: str) -> dict:
    out = EVID / f"battery_v_disposal_{tag}"
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(RUNNER), "--iso", "fixed",
         "--case", "J", "--out", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(A),
    )
    (EVID / f"battery_v_disposal_{tag}.log").write_text(
        (proc.stdout or "") + (proc.stderr or ""), encoding="utf-8")
    return json.loads((out / "J.json").read_text(encoding="utf-8"))


# 1. mutant: gate never runs
mutant = text.replace(anchor, mutant_anchor, 1)
ARM_PI.write_text(mutant, encoding="utf-8", newline="\n")
mutant_sha = hashlib.sha256(ARM_PI.read_bytes()).hexdigest()
res_mut = run_j("mutant")

# 2. restore the merged face and confirm green
ARM_PI.write_bytes(base)
restored_sha = hashlib.sha256(ARM_PI.read_bytes()).hexdigest()
res_ok = run_j("restored")

summary = {
    "mutation": "prompt_injection.py: `if status == \"detected_and_ignored\":` "
                "-> `if False and ...` (P5-b disposal gate never runs)",
    "mutant_pi_sha256": mutant_sha,
    "mutant_verdict": res_mut["verdict"],
    "mutant_failed_checks": [c["name"] for c in res_mut["checks"] if not c["ok"]],
    "mutant_sample_detail": [c["detail"][:300] for c in res_mut["checks"] if not c["ok"]][:3],
    "expect_mutant_red": True,
    "mutant_is_red": res_mut["verdict"] != "PASS",
    "restored_pi_sha256": restored_sha,
    "merged_pi_sha256": "88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33",
    "restored_byte_identical": restored_sha == "88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33",
    "restored_verdict": res_ok["verdict"],
}
(EVID / "battery_v_disposal_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
sys.exit(0 if (summary["mutant_is_red"] and summary["restored_verdict"] == "PASS"
               and summary["restored_byte_identical"]) else 1)
