"""Assemble the rf-job/1 submit body with the built forecast_input embedded."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "inputs" / "mongodb-fy2025-input.json"
OUT = ROOT / "requests" / "mongodb-submit.json"

document = json.loads(INPUT.read_text(encoding="utf-8"))

body = {
    "schema_version": "rf-job/1",
    "workflow": "full_research",
    "company_query": "MongoDB",
    "information_as_of": document["as_of_date"],
    "horizon_end_year": max(document["forecast_years"]),
    "scenario_set": ["low", "base", "high"],
    "source_snapshot_ids": [document["sources"][0]["capture"]["snapshot_sha256"]],
    "idempotency_key": "rf-input-prep-01-mongodb-fy2025-v2",
    "limits_ref": "owner-approved-1usd",
    "forecast_input": document,
}

OUT.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"body": str(OUT), "bytes": OUT.stat().st_size,
                  "information_as_of": body["information_as_of"],
                  "horizon_end_year": body["horizon_end_year"]}))
