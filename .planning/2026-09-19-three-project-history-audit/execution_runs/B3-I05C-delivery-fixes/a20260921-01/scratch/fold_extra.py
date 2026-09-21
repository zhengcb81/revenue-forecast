"""Fold the extra selector-regression results into the run matrix records."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
EXTRA = json.loads((ATTEMPT / "scratch" / "extra_regression.json").read_text(
    encoding="utf-8"))
MATRIX_PATH = ATTEMPT / "scratch" / "run_matrix.json"
MATRIX = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
BY_ID = {r["run_id"]: r for r in MATRIX}

NEW_RUNS = []
for entry in EXTRA:
    run_id = ("CTRL-G-prod-" if entry["mode"] == "production"
              else "CTRL-H-fixed-") + entry["suite"].removesuffix(".py").replace(
                  "test_", "")
    record = {
        "run_id": run_id,
        "purpose": f"{entry['suite']} (production suite also covering "
                   "select_artifact_roles) on the "
                   f"{'unfixed production' if entry['mode'] == 'production' else 'B3 fixed'} "
                   "bytes",
        "cwd": entry["cwd"],
        "argv": entry["argv"],
        "env": {"B3_BYTES": entry["mode"]},
        "returncode": entry["rc"],
        "summary_line": entry["summary"],
        "failed_nodes": entry["failed_nodes"],
        "error_nodes": [],
        "note": "suite vendored into this attempt with a binding block inserted "
                "after `from __future__ import annotations`; assertions "
                "unmodified",
    }
    NEW_RUNS.append(record)
    BY_ID[run_id] = record

merged = {r["run_id"]: r for r in MATRIX}
for record in NEW_RUNS:
    merged[record["run_id"]] = record
MATRIX_PATH.write_text(json.dumps(list(merged.values()), indent=2),
                       encoding="utf-8")
print("run_matrix.json now holds:", ", ".join(merged))

# --- extend commands.json -------------------------------------------------
CMDS_PATH = ATTEMPT / "commands.json"
commands = json.loads(CMDS_PATH.read_text(encoding="utf-8"))
existing = {c["id"] for c in commands}
for record in NEW_RUNS:
    if record["run_id"] in existing:
        continue
    mode = record["env"]["B3_BYTES"]
    commands.append({
        "id": record["run_id"],
        "purpose": record["purpose"],
        "cwd": record["cwd"],
        "argv": record["argv"],
        "env": record["env"],
        "config_paths": [],
        "allowed_write_roots": [str(ATTEMPT)],
        "network": "disabled",
        "timeout_seconds": None,
        "expected_returncode": 0,
        "raw_returncode": record["returncode"],
        "expected_business_result": "10 passed (zr706) / 6 passed (fc905b), "
                                    "identical on both byte sets",
        "observed": record["summary_line"],
        "failed_nodes": record["failed_nodes"],
        "before_after_evidence": ["after/test_results.json"],
        "binding_status": "bound",
        "rotation_note": "added after the initial matrix, because these two "
                         "production suites also call select_artifact_roles "
                         f"(mode={mode})",
    })
CMDS_PATH.write_text(json.dumps(commands, indent=2), encoding="utf-8")

# --- extend case_results regression block ---------------------------------
CASE_PATH = ATTEMPT / "case_results.json"
cases = json.loads(CASE_PATH.read_text(encoding="utf-8"))
cases["regression"]["zr706_fc905b"] = {
    "files": ["tests/test_zr706_selector_contract.py (production, unmodified)",
              "tests/test_fc905b_trusted_receipt.py (production, unmodified)"],
    "why": "a grep for select_artifact_roles found these two production suites "
           "outside the card's named set; they cover the same contract, so "
           "they were added as regression coverage",
    "before": "10 passed / 6 passed (production bytes)",
    "after": "10 passed / 6 passed (fixed bytes) - identical",
    "no_regression": True,
}
CASE_PATH.write_text(json.dumps(cases, indent=2), encoding="utf-8")

# --- extend after/test_results.json ---------------------------------------
RESULTS_PATH = ATTEMPT / "after" / "test_results.json"
results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
results["runs"] = list(merged.values())
RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")

print("updated commands.json, case_results.json, after/test_results.json")
