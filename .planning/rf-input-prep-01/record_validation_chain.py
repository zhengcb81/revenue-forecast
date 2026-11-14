"""Record the three-step input validation chain with exact UTF-8 evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[1]
EVIDENCE = ROOT / "evidence"
INPUT = "inputs/mongodb-fy2025-input.json"

STEPS = [
    ("lint", ["scripts/lint_input.py", f".planning/rf-input-prep-01/{INPUT}"]),
    ("fix-hashes", ["scripts/fix_hashes.py", f".planning/rf-input-prep-01/{INPUT}"]),
    ("validate-only", ["scripts/revenue_forecast.py", f".planning/rf-input-prep-01/{INPUT}", "--validate-only"]),
]


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    input_path = WORKTREE / ".planning" / "rf-input-prep-01" / INPUT
    input_bytes = input_path.read_bytes()
    chain = {
        "schema_version": "rf-input-validation-chain/1",
        "input_document": f".planning/rf-input-prep-01/{INPUT}",
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "input_byte_size": len(input_bytes),
        "steps": [],
    }
    for label, step in STEPS:
        proc = subprocess.run(
            [sys.executable, "-B", *step], capture_output=True, cwd=str(WORKTREE)
        )
        (EVIDENCE / f"mdb-{label}.stdout.txt").write_bytes(proc.stdout)
        (EVIDENCE / f"mdb-{label}.stderr.txt").write_bytes(proc.stderr)
        chain["steps"].append(
            {
                "step": label,
                "argv": step,
                "exit_code": proc.returncode,
                "stdout": proc.stdout.decode("utf-8", "replace").strip(),
                "stderr": proc.stderr.decode("utf-8", "replace").strip(),
            }
        )
    chain["all_passed"] = all(step["exit_code"] == 0 for step in chain["steps"])
    (EVIDENCE / "mdb-validation-chain.json").write_text(
        json.dumps(chain, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "input_sha256": chain["input_sha256"],
                "all_passed": chain["all_passed"],
                "steps": [{"step": s["step"], "exit_code": s["exit_code"]} for s in chain["steps"]],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
