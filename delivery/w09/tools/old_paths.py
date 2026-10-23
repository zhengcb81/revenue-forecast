"""Extract the old sealed forecast's consolidated and segment paths for comparison."""

from __future__ import annotations

import json
from pathlib import Path

RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
OLD = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-forecast.json"
OUT = Path(__file__).resolve().parents[1] / "research" / "scratch" / "old_paths.json"


def main() -> int:
    data = json.loads(OLD.read_text(encoding="utf-8"))
    rows = {"scenarios": {}, "segments": {}, "confidence": data.get("confidence"),
            "data_gaps": data.get("data_gaps"),
            "input_sha256": data.get("input_sha256"),
            "result_sha256": data.get("result_sha256")}
    for scenario, block in data["consolidated_forecast"].items():
        rows["scenarios"][scenario] = {
            "total_revenue": block.get("total_revenue"),
            "segment_subtotal": block.get("segment_subtotal"),
            "growth": block.get("growth"),
            "segments": {row["name"]: row["annual_revenue"] for row in block.get("segment_bridge", [])},
        }
    for seg in data["segments"]:
        rows["segments"][seg.get("name")] = {
            k: v for k, v in seg.items() if k not in {"recognition"}
        }
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({s: rows["scenarios"][s]["total_revenue"] for s in rows["scenarios"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
