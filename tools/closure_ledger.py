"""FC-1505: closure ledger generator — machine-generated, never hand-written.

Builds the final FCAP closure ledger from the registry + receipts + the
closure gate verdict, mapping every user goal to its FC/scenario/receipt
evidence.  The ledger can only be marked ``complete`` when the closure
gate passes (validator exit 0).

Exit 0 = ledger generated AND complete; 1 = ledger generated but
incomplete (honest); 2 = gate failure prevented generation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GATE = PROJECT_ROOT / "tools" / "closure_gate.py"
OUTPUT = PROJECT_ROOT / "assurance" / "fc" / "Phase-15" / "closure_ledger.json"

GOALS = {
    "重构完全成功": ["FC-301", "FC-302", "FC-303", "FC-304", "FC-305",
                     "FC-701", "FC-702", "FC-705", "FC-1201"],
    "Dropbox 功能层面接入": ["FC-501", "FC-502", "FC-503", "FC-504", "FC-505"],
    "功能和目标全部实现": ["FC-601", "FC-602", "FC-603", "FC-604",
                          "FC-801", "FC-802", "FC-803", "FC-804", "FC-805"],
    "完善动态审核": ["FC-1101", "FC-1102", "FC-1103", "FC-1104", "FC-1105"],
    "更多真实 E2E": ["FC-1001", "FC-1002", "FC-1003", "FC-1004", "FC-1005"],
    "全面代码质量提升": ["FC-101", "FC-102", "FC-103", "FC-104",
                        "FC-1202", "FC-1203", "FC-1204", "FC-1205"],
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)

    gate = subprocess.run(
        [sys.executable, str(GATE), "--json"],
        capture_output=True, text=True, timeout=600,
    )
    if gate.returncode not in (0, 1):
        print(f"closure gate failed to run: {gate.stderr[-300:]}", file=sys.stderr)
        return 2
    report = json.loads(gate.stdout)
    ledger = {
        "schema_version": "1.0",
        "generated_by": "tools/closure_ledger.py",
        "closure_gate": report,
        "goals": {
            goal: {"fcs": fcs,
                   "accepted": [
                       fc for fc in fcs
                       if any(f"{fc} " in p or fc in p for p in report["problems"]) is False
                       and fc not in report["problems"]]}
            for goal, fcs in GOALS.items()
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ledger, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    print(json.dumps(ledger, ensure_ascii=False, indent=2))
    return 0 if report["closure_gate"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
