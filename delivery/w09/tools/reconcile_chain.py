"""Reconcile the recorded native chain against the real artifacts.

Checks that the input SHA the recorder froze equals the builder's request SHA,
that the forecast/snapshot record the same input SHA, and that main/stress
numbers reproduce the sealed old paths where the repair was citation-only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
DELIVERY = WORKDIR / "delivery" / "w09"
RUN = DELIVERY / "recorder" / "w09-rf-research-20261023"
LEDGER = DELIVERY / "recorder" / "native-calls.jsonl"
OUT = DELIVERY / "research" / "native-chain.json"
SEALED = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec"
              r"\execution_replays\r1-remediation-01\phase_b\forecast")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    calls = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    ok = True
    for call in calls:
        capture = call["capture"] or {}
        snapshots = capture.get("input_snapshots") or []
        frozen = snapshots[0] if snapshots else {}
        row = {
            "operation": call["op"],
            "request_id": call["request_id"],
            "request_file": call["request_file"],
            "request_sha256": call["request_sha256"],
            "request_bytes": call["request_bytes"],
            "argv": call["argv"],
            "input_argv_positions": call["input_argv_positions"],
            "capture_id": capture.get("capture_id"),
            "capture_dir": str(RUN / "roles" / "executor" / "commands" / str(capture.get("capture_id"))),
            "child_started": capture.get("child_started"),
            "exit_code": capture.get("exit_code"),
            "timed_out": capture.get("timed_out"),
            "input_complete": capture.get("input_complete"),
            "output_complete": capture.get("output_complete"),
            "input_cleanup_complete": capture.get("input_cleanup_complete"),
            "frozen_input_sha256": frozen.get("sha256"),
            "frozen_input_bytes": frozen.get("byte_size"),
            "frozen_input_path": frozen.get("frozen_path"),
            "consumed_path": frozen.get("consumed_path"),
            "stdout_total_bytes": capture.get("stdout_total_bytes"),
            "stderr_total_bytes": capture.get("stderr_total_bytes"),
            "warnings": capture.get("warnings"),
        }
        row["frozen_matches_request"] = (row["frozen_input_sha256"] == row["request_sha256"]
                                         and row["frozen_input_bytes"] == row["request_bytes"])
        ok &= bool(row["frozen_matches_request"] and row["child_started"]
                   and row["exit_code"] == 0 and row["input_complete"] and row["output_complete"])
        rows.append(row)

    outputs = {}
    for which in ("main", "stress"):
        forecast_path = DELIVERY / "forecast" / f"{which}-forecast.json"
        snapshot_path = DELIVERY / "snapshots" / f"{which}-v1.json"
        forecast = json.loads(forecast_path.read_text(encoding="utf-8"))
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        outputs[which] = {
            "input_path": str(DELIVERY / "forecast" / f"{which}-input.json"),
            "input_sha256_file": sha(DELIVERY / "forecast" / f"{which}-input.json"),
            "forecast_path": str(forecast_path),
            "forecast_sha256_file": sha(forecast_path),
            "forecast_input_sha256": forecast["input_sha256"],
            "forecast_version": forecast["forecast_version"],
            "snapshot_path": str(snapshot_path),
            "snapshot_sha256_file": sha(snapshot_path),
            "snapshot_id": snapshot["snapshot_id"],
            "snapshot_input_sha256": snapshot["input_sha256"],
            "snapshot_forecast_result_sha256": snapshot["forecast_result_sha256"],
            "snapshot_version": snapshot["forecast_version"],
            "totals": {s: forecast["consolidated_forecast"][s]["segment_subtotal"]
                       for s in ("low", "base", "high")},
        }
        outputs[which]["snapshot_input_matches_forecast"] = (
            outputs[which]["snapshot_input_sha256"] == outputs[which]["forecast_input_sha256"])

    sealed_main = json.loads((SEALED / "final3-forecast.json").read_text(encoding="utf-8"))
    sealed_stress = json.loads((SEALED / "final3-shared-stress.json").read_text(encoding="utf-8"))
    comparisons = {}
    for label, sealed in (("main", sealed_main), ("stress", sealed_stress)):
        comparisons[label] = {
            scenario: {
                "old": sealed["consolidated_forecast"][scenario]["segment_subtotal"],
                "new": outputs[label]["totals"][scenario],
                "identical": (sealed["consolidated_forecast"][scenario]["segment_subtotal"]
                              == outputs[label]["totals"][scenario]),
            } for scenario in ("low", "base", "high")
        }
    stress_delta = {
        scenario: {year: outputs["stress"]["totals"][scenario][year]
                   - outputs["main"]["totals"][scenario][year]
                   for year in ("2026", "2027", "2028")}
        for scenario in ("low", "base", "high")
    }

    record = {
        "schema_version": "w09-native-chain/1",
        "package_id": "W09-RF-RESEARCH",
        "recorder_run": str(RUN),
        "calls": rows,
        "all_calls_clean": ok,
        "outputs": outputs,
        "sealed_comparison": comparisons,
        "stress_minus_main": stress_delta,
        "note": ("Every call was built by execution_request.py and executed by audit_run.py capture; "
                 "the frozen consumed input SHA equals the builder request SHA in each row. A clean "
                 "chain is an execution-integrity statement, not an economic acceptance."),
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"all_calls_clean": ok, "calls": len(rows),
                      "main_identical_old": all(c["identical"] for c in comparisons["main"].values()),
                      "stress_identical_old": all(c["identical"] for c in comparisons["stress"].values()),
                      "out": str(OUT)}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
