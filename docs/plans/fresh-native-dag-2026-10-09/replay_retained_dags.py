"""Offline retained DAG replay; inputs are read-only equivalent reconstructions.

Only explicit sensitivity-domain metadata is added in memory. These domains
express mathematical signed growth/delta semantics, not empirical calibration.
No provider, source acquisition or installed skill is invoked.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--audit-root", required=True, type=Path)
parser.add_argument("--runtime-root", required=True, type=Path)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
sys.path.insert(0, str(args.runtime_root / "scripts"))
from revenue_core import run_forecast, canonical_sha256, referenced_parameter_ids
from revenue_report import validate_published_forecast

cases = [
    ("retained-h2-reproducer", "fresh-20261009T065028-hk-00700/execution/input-unsupported-h2-sensitivity-reproducer.json",
     {"lower": -1.0, "upper": None, "basis": "Signed revenue growth; lower bound excludes revenue below zero"}),
    ("retained-signed-delta-equivalent", "fresh-20261009T065028-us-msft/execution/research/input-original-dag-equivalent-reconstruction.json",
     {"lower": None, "upper": None, "basis": "Signed additive growth change; downstream growth driver bounds still apply"}),
    ("retained-direct-with-derived-delta-equivalent", "fresh-20261009T065028-us-msft/execution/research/input-intermediate-direct-with-derived-delta.json", None),
]
rows = []
old_registry = os.environ.get("REVENUE_PUBLICATION_REGISTRY")
try:
    with tempfile.TemporaryDirectory(prefix="rf-retained-dag-") as td:
        os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(Path(td) / "registry")
        for label, relative, domain in cases:
            path = args.audit_root / relative
            source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            params = {p["parameter_id"]: p for p in data["parameters"]}
            direct = referenced_parameter_ids(data, "base")
            additions = {}
            for test in data.get("sensitivity_tests", []):
                pid = test["parameter_id"]
                if domain is not None and pid not in direct and params[pid]["dimension"] == "ratio":
                    params[pid]["sensitivity_domain"] = copy.deepcopy(domain)
                    additions[pid] = copy.deepcopy(domain)
            frozen = copy.deepcopy(data)
            row = {"case": label, "source_file": str(path), "source_sha256": source_hash,
                   "domain_metadata_additions": additions, "replay_input_sha256": canonical_sha256(data)}
            try:
                result = run_forecast(data)
                validate_published_forecast(result, data)
                assert data == frozen
                row.update(status="PASS", terminal=result["consolidated_forecast"]["base"]["terminal_revenue"],
                           sensitivity_count=len(result["sensitivities"]), shocks=[{
                           "parameter_id": s["parameter_id"], "requested_values": s["requested_values"],
                           "effective_values": s["effective_values"],
                           "down_terminal_revenue": s["down_terminal_revenue"],
                           "up_terminal_revenue": s["up_terminal_revenue"],
                           "affected_derived_parameter_ids": s.get("dependency_recalculation", {}).get("affected_derived_parameter_ids", [])
                           } for s in result["sensitivities"]])
            except Exception as exc:
                row.update(status="FAIL", error_type=type(exc).__name__, error=str(exc))
            row["source_bytes_unchanged"] = hashlib.sha256(path.read_bytes()).hexdigest() == source_hash
            rows.append(row)
finally:
    if old_registry is None:
        os.environ.pop("REVENUE_PUBLICATION_REGISTRY", None)
    else:
        os.environ["REVENUE_PUBLICATION_REGISTRY"] = old_registry
args.output.write_text(json.dumps({"runtime_root": str(args.runtime_root), "scope": "engineering replay only; equivalent inputs are not recovered first-failure bytes", "cases": rows}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
for row in rows:
    print(row["case"], row["status"], row.get("sensitivity_count", ""), row.get("error", ""))
raise SystemExit(0 if all(row["status"] == "PASS" and row["source_bytes_unchanged"] for row in rows) else 1)
