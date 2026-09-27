#!/usr/bin/env python
"""I10A-F2-FIX I-6 golden VALUE-identity check (oracle §3 I-6 / §5 disposition G1).

Runs the five golden families through the tree given as argv[1] (either the
read-only RF production tree or the fixed iso/rf tree) and dumps ONLY the
revenue series (recognized / effective / modeled / carry-in / tail, plus the
consolidated and probability-weighted forecasts and the historical series).
Driver metadata (`driver_parameter_ids`, parameter ids, hashes, receipts) is
deliberately excluded: G1 adds EXPLICIT zero-valued optional parameters, which
changes metadata bytes (=> deliberate golden hash refresh) while every revenue
series value must stay byte-identical.

Usage: python golden_value_identity.py <tree_root> <out.json>
Exit 0 on success; the JSON carries one sha256 per family over the canonical
revenue-series serialization so the two trees can be compared mechanically.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SCENARIO_FIELDS = (
    "formula",
    "modeled_activity",
    "recognized_revenue",
    "carry_in_revenue",
    "unrecognized_tail_activity",
    "effective_revenue",
)


def revenue_series(result: dict) -> dict:
    return {
        "base_revenue": result.get("base_revenue"),
        "base_year": result.get("base_year"),
        "forecast_years": result.get("forecast_years"),
        "historical_revenue": result.get("historical_revenue"),
        "consolidated_forecast": result.get("consolidated_forecast"),
        "probability_weighted_forecast": result.get("probability_weighted_forecast"),
        "segments": [
            {
                "name": segment["name"],
                "base_revenue": segment.get("base_revenue"),
                "scenarios": {
                    name: {field: payload.get(field) for field in SCENARIO_FIELDS}
                    for name, payload in segment["scenarios"].items()
                },
            }
            for segment in result["segments"]
        ],
    }


def main() -> int:
    root = Path(sys.argv[1])
    out = Path(sys.argv[2])
    sys.path.insert(0, str(root / "scripts"))
    sys.path.insert(0, str(root / "tests"))
    import test_golden_behavior_lock as golden  # noqa: PLC0415

    families = {}
    for family in golden.MODEL_SPECS:
        series = revenue_series(golden.run_family(family))
        blob = json.dumps(series, sort_keys=True, ensure_ascii=False).encode("utf-8")
        families[family] = {
            "revenue_series_sha256": hashlib.sha256(blob).hexdigest(),
            "revenue_series_bytes": len(blob),
            "revenue_series": series,
        }
    out.write_text(
        json.dumps(
            {
                "artifact": "golden_value_identity",
                "tree": str(root),
                "families": families,
            },
            indent=1,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({k: v["revenue_series_sha256"] for k, v in families.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
