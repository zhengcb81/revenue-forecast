"""Diagnose which conversion inputs lack a disclosed conversion observation."""

from __future__ import annotations

import json
from pathlib import Path

FORECAST = Path(__file__).resolve().parents[1] / "forecast" / "main-forecast.json"
OUT = Path(__file__).resolve().parents[1] / "research" / "scratch" / "conv_diag.txt"


def main() -> int:
    data = json.loads(FORECAST.read_text(encoding="utf-8"))
    adequacy = data["confidence"]["research_adequacy"]
    observations = adequacy["evidence_roles"]
    conversion = [o for o in observations if o["role"] == "conversion_assumption"]
    covered = {pid for o in conversion for pid in o["parameter_ids"]}
    lines = [f"conversion observations: {len(conversion)}", f"covered parameters: {len(covered)}"]
    for row in conversion[:12]:
        lines.append(f"  {row['claim_id']} {row['parameter_ids']} {row['scope']} "
                     f"{row['period']} {row['binding_status']}")
    for calibration in adequacy["calibrations"]:
        missing = []
        for scenario, inputs in calibration["scenario_input_parameter_ids"].items():
            for pid in inputs[1:]:
                if pid not in covered:
                    missing.append(f"{scenario}:{pid}")
        lines.append(f"{calibration['calibration_id']} {calibration['adequacy_status']} "
                     f"missing={missing}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
