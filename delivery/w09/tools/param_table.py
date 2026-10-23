"""Print a compact parameter/formula table for one segment of the sealed input."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
INPUT = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json"
OUT = Path(__file__).resolve().parents[1] / "research" / "scratch" / "param_table.txt"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--needle", default="non_tides")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    lines = []
    for i, p in enumerate(data["parameters"]):
        pid = p["parameter_id"]
        if args.needle not in pid:
            continue
        lines.append(
            f"[{i:3d}] {pid} | kind={p.get('kind')} | scen={p.get('scenario')} | "
            f"period={p.get('period')} | unit={p.get('unit')} | value={p.get('value')}"
        )
        if p.get("formula"):
            lines.append(f"      formula={p['formula']} inputs={p.get('input_parameter_ids')}")
        if p.get("rationale"):
            lines.append(f"      rationale={p['rationale']}")
        if p.get("claim_ids"):
            lines.append(f"      claims={p['claim_ids']}")
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out} lines={len(lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
