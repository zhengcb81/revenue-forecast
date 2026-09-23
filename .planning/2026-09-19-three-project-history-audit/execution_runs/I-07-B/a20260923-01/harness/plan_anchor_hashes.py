"""Emit evidence/plan_anchor_hashes.json — corrected capture of the six PLAN
inputs that harness/snapshot.py resolved one level too deep (see decision.md J8).
Read-only hashing; taken after the runs, inputs are read-only plan files."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[4]
FILES = {
    "PLAN/execution_v2/card_I-07-B.md": AUDIT / "execution_v2" / "card_I-07-B.md",
    "PLAN/execution_v2/scenario_matrix.md": AUDIT / "execution_v2" / "scenario_matrix.md",
    "PLAN/execution_v2/sample_manifest.json": AUDIT / "execution_v2" / "sample_manifest.json",
    "PLAN/execution_v2/START_HERE.md": AUDIT / "execution_v2" / "START_HERE.md",
    "PLAN/execution_runs/I-00-B/a20260919-01/binding.json":
        AUDIT / "execution_runs" / "I-00-B" / "a20260919-01" / "binding.json",
    "PLAN/execution_runs/I-00-B/a20260919-01/commands.json":
        AUDIT / "execution_runs" / "I-00-B" / "a20260919-01" / "commands.json",
    "PLAN/execution_runs/I-00-B/a20260919-01/oracle.md":
        AUDIT / "execution_runs" / "I-00-B" / "a20260919-01" / "oracle.md",
    "PLAN/execution_runs/I-07-A/a20260919-01/after/state_matrix.json":
        AUDIT / "execution_runs" / "I-07-A" / "a20260919-01" / "after" / "state_matrix.json",
}


def main() -> int:
    out = {"captured_at": datetime.now(timezone.utc).isoformat(),
           "why": "snapshot.py path-resolution bug (decision.md J8); inputs are read-only "
                  "plan files, hashed independently here",
           "files": {}}
    for key, p in FILES.items():
        if p.is_file():
            out["files"][key] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                                 "bytes": p.stat().st_size}
        else:
            out["files"][key] = {"missing": True, "path": str(p)}
    dest = Path(__file__).resolve().parents[1] / "evidence" / "plan_anchor_hashes.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"written": str(dest),
                      "scenario_matrix_ok":
                          out["files"]["PLAN/execution_v2/scenario_matrix.md"].get("sha256")
                          == "0dec23cd10f00efd6ad82cf923552bd46c1763bcf9f740422f51f4973292299f"},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
