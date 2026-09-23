"""I-07-B: aggregate per-case results -> after/case_results.json (+ compact stdout)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
CASES = ATT / "evidence" / "cases"

CASE_ORDER = ["S-CN-1", "S-HK-1", "S-US-1", "S-CN-2", "S-HK-2", "S-US-2",
              "S-CN-3", "S-HK-3", "S-US-3", "REGFAIL-HK", "REGFAIL-US"]


def load(p: Path):
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def main() -> int:
    out = {"generated_at": datetime.now(timezone.utc).isoformat(),
           "exit_code_legend_ref": "commands.json.exit_code_legend (harness rc)",
           "cases": {}}
    for cid in CASE_ORDER:
        cdir = CASES / cid
        entry: dict = {"initial_state": load(cdir / "initial_state.json") is not None,
                       "runs": {}, "scans": {}, "lock": load(cdir / "lock" / "hold.json")}
        initial = load(cdir / "initial_state.json") or {}
        entry["state"] = initial.get("state")
        entry["sample"] = initial.get("sample")
        entry["precondition"] = {
            "state1_documents_rows": (initial.get("rows") or {}).get("inserted", {}).get("documents"),
            "pi_review_present": (initial.get("rows") or {}).get(
                "metadata_prompt_injection_review_present"),
            "raw_absent": (initial.get("asset") or {}).get("raw_absent_exists"),
        }
        for sub, key in (("run", "runs"), ("scan", "scans")):
            for d in sorted(cdir.glob(f"{sub}*")):
                ev = load(d / "evidence.json")
                if ev is None:
                    continue
                slim = {k: ev.get(k) for k in (
                    "product_returncode", "counter_delta", "catalog_count_delta",
                    "catalog_counts_before", "catalog_counts_after",
                    "raw_unchanged", "allow_download", "simulated_provider_fixture",
                    "elapsed_seconds", "stage", "run")}
                slim["stages"] = ev.get("stages")
                ref = ev.get("refusal") or {}
                slim["refusal"] = {
                    "structured_actionable_present": ref.get("structured_actionable_present"),
                    "actionable_fields": sorted((ref.get("actionable_recovery_fields") or {}).keys()),
                    "generic_error_fields": ref.get("generic_error_fields"),
                    "explicit_missing_info": ref.get("explicit_missing_info"),
                }
                slim["deep_verification"] = ev.get("deep_verification")
                entry[key][d.name] = slim
        out["cases"][cid] = entry
    # second-run deltas (重复请求 clause C3) per case
    for cid, entry in out["cases"].items():
        r1, r2 = entry["runs"].get("run1"), entry["runs"].get("run2")
        if r1 and r2:
            entry["repeat_clause_C3"] = {
                "provider_delta_run1": (r1.get("counter_delta") or {}).get("provider", 0),
                "provider_delta_run2": (r2.get("counter_delta") or {}).get("provider", 0),
                "producer_delta_run1": (r1.get("counter_delta") or {}).get("producer", 0),
                "producer_delta_run2": (r2.get("counter_delta") or {}).get("producer", 0),
                "registration_rows_unchanged_run1_to_run2":
                    (r2.get("catalog_counts_before") or {}) == (r1.get("catalog_counts_after") or {})
                    if "catalog_counts_before" in (r2 or {}) else None,
                "catalog_count_delta_run2": r2.get("catalog_count_delta"),
                "raw_unchanged_both": bool(r1.get("raw_unchanged") and r2.get("raw_unchanged")),
            }
    dest = ATT / "after" / "case_results.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str),
                    encoding="utf-8")
    compact = {}
    for cid, e in out["cases"].items():
        compact[cid] = {
            "state": e["state"],
            "run_rcs": {k: v.get("product_returncode") for k, v in e["runs"].items()},
            "run_counters": {k: v.get("counter_delta") for k, v in e["runs"].items()},
            "scan_rcs": {k: v.get("product_returncode") for k, v in e["scans"].items()},
            "scan_counters": {k: v.get("counter_delta") for k, v in e["scans"].items()},
            "C3": e.get("repeat_clause_C3"),
        }
    print(json.dumps({"written": str(dest), "cases": compact}, ensure_ascii=False,
                     default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
