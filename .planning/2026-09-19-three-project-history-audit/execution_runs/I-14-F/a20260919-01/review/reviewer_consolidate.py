"""Reviewer tool: consolidate the four reviewer-owned verification runs into one
audit record (reviewer_runs.json) by re-reading their own captures on disk.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
REVIEW = ATTEMPT / "review"
DEC = re.compile(r"CW-BASETEMP-DECISION (\{.*\})")
CLN = re.compile(r"CW-BASETEMP-CLEANUP (\{.*\})")
MUT = Path(os.environ["TEMP"]) / "i14f-rev-mut" / ("a" * 95)

RUNS = [
    ("R-red", "logon_wrapper_quoted", ATTEMPT / "review" / "deep" / "pad55" / "P0-logon_wrapper_quoted-1",
     "pristine git-archive HEAD tree (no conftest.py)"),
    ("G-green", "logon_wrapper_quoted", ATTEMPT / "review" / "deep" / "pad55" / "R1-logon_wrapper_quoted-1",
     "isolated tree with conftest.py"),
    ("M-mut", "logon_wrapper_quoted", MUT / "P0-logon_wrapper_quoted-1",
     "isolated tree, CW_SHORT_BASETEMP_DISABLE=1"),
    ("M-mut", "child_without_runtime", MUT / "P0-child_without_runtime-1",
     "isolated tree, CW_SHORT_BASETEMP_DISABLE=1"),
]


def classify(text: str, rc: int) -> str:
    if rc == 0:
        return "pass"
    for name, needles in [("WinError206", ("WinError 206",)),
                          ("FileNotFound-launcher-events", ("worker_launcher_events.jsonl",)),
                          ("timeout15s-band", ("TimeoutExpired", "timed out after"))]:
        if any(n in text for n in needles):
            return name
    return "other-failure"


def main() -> int:
    rows = []
    for phase, node, run_dir, note in RUNS:
        text = (run_dir / "stdout.txt").read_text(encoding="utf-8", errors="replace")
        rc = int((run_dir / "returncode.txt").read_text(encoding="utf-8").strip())
        basetemp = run_dir / "pytest"
        dm = DEC.search(text)
        cm = CLN.search(text)
        rows.append({
            "phase": phase,
            "node": node,
            "note": note,
            "cwd": str(run_dir),
            "cwd_len": len(str(run_dir)),
            "basetemp_len": len(str(basetemp)),
            "rc": rc,
            "signature": classify(text, rc),
            "decision": json.loads(dm.group(1)) if dm else None,
            "cleanup": json.loads(cm.group(1)) if cm else None,
            "capture": str(run_dir / "stdout.txt"),
            "capture_sha256": hashlib.sha256((run_dir / "stdout.txt").read_bytes()).hexdigest(),
        })
    out = {
        "reviewer": "independent reviewer of card I-14-F (not the implementer)",
        "driver": "review/reviewer_reverify.py (reviewer-written; does not reuse harness/run_placement.py)",
        "geometry_note": ("fallback dir stamps in decision lines are UTC; file mtimes are local "
                          "= UTC+1 on this box (TimeZone 'GMT Standard Time'), which matters when "
                          "comparing run times against artifact mtimes"),
        "rows": rows,
        "fallback_root": str(Path(os.environ["TEMP"]) / "cw-pytest-basetemp"),
        "fallback_root_leftovers": sorted(p.name for p in (Path(os.environ["TEMP"]) / "cw-pytest-basetemp").iterdir()),
    }
    (REVIEW / "reviewer_runs.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in rows:
        print(f"{r['phase']:7s} {r['node']:21s} cwd_len={r['cwd_len']} bt_len={r['basetemp_len']} "
              f"rc={r['rc']} {r['signature']} relocated="
              f"{None if not r['decision'] else r['decision'].get('relocated')} "
              f"cleanup_removed={None if not r['cleanup'] else r['cleanup'].get('removed')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
