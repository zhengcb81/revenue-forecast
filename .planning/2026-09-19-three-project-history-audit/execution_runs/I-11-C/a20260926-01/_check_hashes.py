#!/usr/bin/env python3
"""_check_hashes.py — verify handoff.json input_hashes against recomputed SHA256/size."""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parents[1]                      # …/execution_runs
AUDIT = HERE.parents[2]                     # …/2026-09-19-three-project-history-audit

INPUTS = {
    "I-11-B/calibration_plan.json": RUNS / "I-11-B" / "a20260926-01" / "calibration_plan.json",
    "I-11-B/expert_assumptions.json": RUNS / "I-11-B" / "a20260926-01" / "expert_assumptions.json",
    "I-11-B/synthetic_mechanism_check.json": RUNS / "I-11-B" / "a20260926-01" / "synthetic_mechanism_check.json",
    "I-11-B/revert_or_stop.json": RUNS / "I-11-B" / "a20260926-01" / "revert_or_stop.json",
    "OPEN2-C2-REGISTRATION/hypotheses_v3.json": RUNS / "OPEN2-C2-REGISTRATION" / "a20260926-01" / "hypotheses_v3.json",
    "execution_v2/card_I-11-C.md": AUDIT / "execution_v2" / "card_I-11-C.md",
    "execution_v2/card_I-11-B.md": AUDIT / "execution_v2" / "card_I-11-B.md",
    "OWNER_DECISIONS.md": AUDIT / "OWNER_DECISIONS.md",
}

h = json.loads((HERE / "handoff.json").read_text(encoding="utf-8-sig"))["input_hashes"]
bad = 0
for key, path in INPUTS.items():
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    size = len(data)
    rec = h.get(key, "")
    m = re.match(r"([0-9a-f]{64}) \((\d+) B", (rec or "").replace("；", "; "))
    if not m:
        print(f"HASH_PARSE_FAIL {key}: recorded={rec!r}")
        bad += 1
        continue
    ok = (m.group(1) == sha) and (int(m.group(2)) == size)
    print(f"{'OK ' if ok else 'MISMATCH'} {key}: recorded={m.group(1)[:16]}…/{m.group(2)} actual={sha[:16]}…/{size}")
    if not ok:
        print(f"    CORRECT VALUE: {sha} ({size} B)")
        bad += 1
print(f"RESULT {'ALL_OK' if bad == 0 else f'{bad}_MISMATCH'}")
sys.exit(0 if bad == 0 else 1)
