"""I-14-B frozen-case runner.

Runs the subject under test (SUT) as a REAL subprocess (argv + raw rc), then
compares its per-case verdicts against harness/frozen_expectations.json, which
was hand-derived from oracle.md before any run.

The runner is the anti-cheat gate: its own rc is 0 only when every frozen case
matches.  accepted_ineligible counts the cases where the SUT accepted a claim
that the frozen oracle says must be refused -- that is the headline number.

Usage:
  <iso-python> -X utf8 -B harness/run_cases.py --sut <path> --out-dir <dir>
      --label <label> [--tolerance-seconds N] [--capture-tolerance-seconds N]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent

# frozen output-shape contract: the card requires the time fields to be recorded
# SEPARATELY, so a verdict that collapses them cannot satisfy the oracle.
REQUIRED_KEYS = {
    "window_accounting": [
        "scheduled_at", "started_at", "first_sampled_at", "last_sampled_at",
        "observation_finished_at", "observation_span_seconds", "sample_count",
        "samples_outside_window", "quick_check_seconds", "command_total_seconds",
        "schedule_lag_seconds", "union_seconds", "sum_seconds", "overlap_seconds",
        "sum_used_for_natural_duration",
    ],
    "calendar": [
        "daily_count", "weekly_count", "monthly_count", "alert_count",
        "window_status", "clock_source",
    ],
    "login_anchor": [
        "anchor_event_id", "shared_anchor_event_id", "label_offsets_seconds",
        "label_offset_max_error_seconds", "capture_latency_max_seconds",
        "label_count",
    ],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse(ts: str):
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sut", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--cases", default=str(HERE / "cases.json"))
    ap.add_argument("--expectations", default=str(HERE / "frozen_expectations.json"))
    ap.add_argument("--tolerance-seconds", type=float, default=None)
    ap.add_argument("--capture-tolerance-seconds", type=float, default=None)
    args = ap.parse_args()

    sut = Path(args.sut).resolve()
    cases_path = Path(args.cases).resolve()
    exp_path = Path(args.expectations).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cases_doc = json.loads(cases_path.read_text(encoding="utf-8"))
    exp_doc = json.loads(exp_path.read_text(encoding="utf-8"))
    frozen_now = cases_doc["frozen_now_utc"]

    tol = args.tolerance_seconds
    if tol is None:
        tol = exp_doc["default_inputs"]["label_offset_tolerance_seconds"]
    cap_tol = args.capture_tolerance_seconds
    if cap_tol is None:
        cap_tol = exp_doc["default_inputs"]["capture_latency_tolerance_seconds"]

    sut_report = out_dir / "sut_report.json"
    if sut_report.exists():
        sut_report.unlink()

    argv = [
        sys.executable, "-X", "utf8", "-B", str(sut),
        "--cases", str(cases_path),
        "--report", str(sut_report),
        "--tolerance-seconds", repr(float(tol)),
        "--capture-tolerance-seconds", repr(float(cap_tol)),
        "--frozen-now", frozen_now,
    ]
    proc = subprocess.run(argv, capture_output=True)
    (out_dir / "sut_cli.stdout.txt").write_bytes(proc.stdout)
    (out_dir / "sut_cli.stderr.txt").write_bytes(proc.stderr)
    (out_dir / "sut_cli.argv.json").write_text(
        json.dumps({"argv": argv, "raw_returncode": proc.returncode,
                    "expected_returncode": 0}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    gate = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "label": args.label,
        "sut_path": str(sut),
        "sut_sha256": sha256_file(sut),
        "cases_path": str(cases_path),
        "cases_sha256": sha256_file(cases_path),
        "expectations_path": str(exp_path),
        "expectations_sha256": sha256_file(exp_path),
        "runner_path": str(Path(__file__).resolve()),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "frozen_now_utc": frozen_now,
        "tolerance_seconds_input": tol,
        "capture_tolerance_seconds_input": cap_tol,
        "sut_raw_returncode": proc.returncode,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if proc.returncode != 0:
        gate.update({"ok": False, "error": "sut_cli_nonzero",
                     "mismatches": [], "accepted_ineligible": [],
                     "case_count": len(cases_doc["cases"])})
        (out_dir / "cases_report.json").write_text(
            json.dumps(gate, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"ok": False, "label": args.label,
                          "sut_raw_returncode": proc.returncode}, indent=2))
        return 1

    report = json.loads(sut_report.read_text(encoding="utf-8"))
    by_id = {v["case_id"]: v for v in report["verdicts"]}

    mismatches = []
    accepted_ineligible = []
    for case in cases_doc["cases"]:
        cid = case["case_id"]
        exp = exp_doc["expected"][cid]
        got = by_id.get(cid)
        if got is None:
            mismatches.append({"case_id": cid, "field": "verdict", "expected": "present",
                               "got": "missing"})
            continue
        if got["verdict"] != exp["verdict"]:
            mismatches.append({"case_id": cid, "field": "verdict",
                               "expected": exp["verdict"], "got": got["verdict"]})
        if sorted(got.get("refusals") or []) != sorted(exp["refusals"]):
            mismatches.append({"case_id": cid, "field": "refusals",
                               "expected": sorted(exp["refusals"]),
                               "got": sorted(got.get("refusals") or [])})
        for key, want in exp["computed"].items():
            have = (got.get("computed") or {}).get(key, "<absent>")
            if isinstance(want, float) and isinstance(have, (int, float)):
                same = abs(float(want) - float(have)) < 1e-9
            else:
                same = want == have
            if not same:
                mismatches.append({"case_id": cid, "field": f"computed.{key}",
                                   "expected": want, "got": have})
        if got["verdict"] == "accept_claim" and exp["verdict"] == "reject_claim":
            accepted_ineligible.append(cid)
        computed = got.get("computed") or {}
        for key in REQUIRED_KEYS.get(case["class"], []):
            if key not in computed:
                mismatches.append({"case_id": cid, "field": f"shape.{key}",
                                   "expected": "present", "got": "<absent>"})

    gate.update({
        "ok": len(mismatches) == 0,
        "case_count": len(cases_doc["cases"]),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "accepted_ineligible": accepted_ineligible,
        "accepted_ineligible_count": len(accepted_ineligible),
        "sut_accepted_claim_count": report.get("accepted_claim_count"),
        "sut_refusal_code_count": report.get("refusal_code_count"),
        "sut_version": report.get("sut_version"),
    })
    (out_dir / "cases_report.json").write_text(
        json.dumps(gate, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": gate["ok"],
        "label": args.label,
        "case_count": gate["case_count"],
        "mismatch_count": gate["mismatch_count"],
        "accepted_ineligible_count": gate["accepted_ineligible_count"],
        "sut_raw_returncode": gate["sut_raw_returncode"],
        "sut_sha256": gate["sut_sha256"],
    }, indent=2))
    return 0 if gate["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
