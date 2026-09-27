"""Independent re-derivation of one frozen oracle value (review.md attack list #1).

Rule under test (oracle.md / review.md): p95 == sorted[int(n * 0.95)] (floor),
computed over the SUCCEEDED exact-bucket calls only.  This script never imports
the probe: it reads the probe's own report.json and recomputes with an
independently written one-liner executed in a separate interpreter process.

Usage: python recompute_p95.py <report.json> <out.json>
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
from pathlib import Path


def p95_floor(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]


def main() -> int:
    report_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    report = json.loads(report_path.read_text(encoding="utf-8"))

    per_call = report.get("per_call", [])
    # main() reports all_calls = exact_calls + latest_calls, so the first
    # `samples` entries are the exact bucket and the rest are latest.
    n_exact = report["slo_probe"]["samples"]
    exact_calls = per_call[:n_exact]
    latest_calls = per_call[n_exact:]
    exact_values = [c["elapsed_seconds"] for c in exact_calls if c["succeeded"]]
    latest_values = [c["elapsed_seconds"] for c in latest_calls if c["succeeded"]]
    reported_exact = report["slo_probe"]["exact"]["percentiles"]
    reported_latest = report["slo_probe"]["latest"]["percentiles"]

    code = (
        "import statistics,sys,json;v=json.loads(sys.argv[1]);o=sorted(v);"
        "print(json.dumps({'p50':statistics.median(o),"
        "'p95':o[min(len(o)-1,int(len(o)*0.95))],"
        "'p99':o[min(len(o)-1,int(len(o)*0.99))]}))"
    )
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", "-c", code, json.dumps(exact_values)],
        capture_output=True, text=True, encoding="utf-8",
    )

    out = {
        "report": str(report_path),
        "percentile_rule": "sorted[int(n*0.95)] floor",
        "exact_n": len(exact_values),
        "exact_values": exact_values,
        "exact_p95_recomputed_here": p95_floor(exact_values),
        "exact_p95_reported_by_probe": reported_exact["p95"],
        "exact_p50_recomputed_here": statistics.median(sorted(exact_values)),
        "exact_p50_reported_by_probe": reported_exact["p50"],
        "latest_n": len(latest_values),
        "latest_p95_recomputed_here": p95_floor(latest_values),
        "latest_p95_reported_by_probe": reported_latest["p95"],
        "independent_subprocess_rc": proc.returncode,
        "independent_subprocess_stdout": proc.stdout.strip(),
        "independent_subprocess_stderr": proc.stderr.strip(),
        "budgets_in_report": report.get("budgets"),
        "breaches_in_report": report.get("breaches"),
    }
    out["exact_p95_match"] = out["exact_p95_recomputed_here"] == out["exact_p95_reported_by_probe"]
    out["exact_p50_match"] = out["exact_p50_recomputed_here"] == out["exact_p50_reported_by_probe"]
    out["latest_p95_match"] = out["latest_p95_recomputed_here"] == out["latest_p95_reported_by_probe"]
    out["budgets_untouched"] = report.get("budgets") == {
        "exact_p95": 5.0, "latest_p95": 5.0, "bundle_p95": 5.0, "peak_rss_gb": 2.0}

    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if all([out["exact_p95_match"], out["exact_p50_match"],
                     out["latest_p95_match"], out["budgets_untouched"],
                     out["independent_subprocess_rc"] == 0]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
