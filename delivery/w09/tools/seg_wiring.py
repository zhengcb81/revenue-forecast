"""Compare one segment's scenario wiring between the sealed base and stress inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
BASE = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json"
STRESS = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-shared-stress-input.json"
OUT = Path(__file__).resolve().parents[1] / "research" / "scratch" / "seg_wiring.txt"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--segment", type=int, default=0)
    args = ap.parse_args()
    base = json.loads(BASE.read_text(encoding="utf-8"))
    stress = json.loads(STRESS.read_text(encoding="utf-8"))
    lines = []
    for label, data in (("BASE", base), ("STRESS", stress)):
        seg = data["segments"][args.segment]
        lines.append(f"===== {label} segment[{args.segment}] {seg['name']}")
        lines.append(f"base_revenue_parameter_id={seg['base_revenue_parameter_id']}")
        lines.append("recognition=" + json.dumps(seg["recognition"], ensure_ascii=False, indent=1))
        for scenario, block in seg["scenarios"].items():
            lines.append(f"-- {scenario}: " + json.dumps(block, ensure_ascii=False, indent=1))
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
