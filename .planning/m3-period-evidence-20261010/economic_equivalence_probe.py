"""Economic equivalence control: legacy-schema 3.7 outputs must be identical
between the base commit runtime and the post-change runtime, excluding the
intentionally bumped version/receipt metadata fields.

Prints one JSON line: {"variant": ..., "economic_sha256": ..., "engine": ...}.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "scripts"))
sys.path.insert(0, str(WORKTREE / "tests"))

from revenue_core import ENGINE_VERSION, canonical_sha256, run_forecast  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

ECONOMIC_KEYS = (
    "consolidated_forecast",
    "segments",
    "sensitivities",
    "growth_driver_analysis",
    "theme_analysis",
    "revenue_constraints",
    "research_coverage",
    "management_target_coverage",
    "disconfirming_indicators",
    "parameter_trace",
    "historical_accuracy_records",
)


def main() -> int:
    variants = {}
    for variant, mutate in (("legacy_37", None), ("legacy_38", "operating_units")):
        data = forecast_document()
        if mutate == "operating_units":
            data["schema_version"] = "3.8"
            data["operating_units"] = []
        result = run_forecast(data)
        economic = {k: result[k] for k in ECONOMIC_KEYS if k in result}
        economic["confidence_score"] = result["confidence"]["score"]
        economic["confidence_components"] = result["confidence"]["components"]
        economic["data_gaps"] = result["data_gaps"]
        variants[variant] = {
            "economic_sha256": canonical_sha256(economic),
            "engine": result["engine_version"],
            "schema": result["schema_version"],
        }
    print(json.dumps({"variant": "probe", **variants}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
