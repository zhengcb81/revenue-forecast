"""Reviewer triangulation: recorded arm rc (evidence.json) vs raw per-card rc in scratch.

Reads the implementer's own arm_results.json files (raw process rc per card per arm) and
compares them with what evidence.json / aggregate_summary.json claim.
"""
import json
import os

ATTEMPT = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
           r"\2026-09-19-three-project-history-audit\execution_runs"
           r"\B5-plan-level-remediation\a20260921-01")
BATCHES = ["M05-M08", "M09-M12", "M13-M16", "M21-M24", "M25-M28", "M29-M31"]

for b in BATCHES:
    ev = json.load(open(os.path.join(ATTEMPT, b, "evidence.json"), encoding="utf-8"))
    rec = {}
    rows = ev.get("arm_summary_rows") or {}
    for arm in "EFBG":
        v = (ev.get("arms") or {}).get(arm, {}).get("rc")
        if v is None and isinstance(rows.get(arm), dict):
            r = rows[arm].get("rc")
            v = sorted(set(r.values())) if isinstance(r, dict) else r
        rec[arm] = v
    # raw scratch
    scratch_results = []
    for root, dirs, files in os.walk(ATTEMPT):
        if "_reviewer_verify" in root:
            continue
        for fn in files:
            if fn == "arm_results.json" and ("_scratch" in root):
                try:
                    d = json.load(open(os.path.join(root, fn), encoding="utf-8"))
                    scratch_results.append((os.path.relpath(os.path.join(root, fn), ATTEMPT), d))
                except Exception as e:
                    scratch_results.append((os.path.relpath(os.path.join(root, fn), ATTEMPT), str(e)))
    raw = {}
    for path, d in scratch_results:
        if not isinstance(d, dict):
            continue
        for e in d.get("arms", []):
            if isinstance(e, dict) and "card" in e:
                raw.setdefault(e.get("arm"), {})[e["card"]] = e.get("raw_rc")
    print("=" * 76)
    print("%s   evidence.json rc: %s" % (b, rec))
    print("   raw arm_results.json files found under _scratch: %d" % len(scratch_results))
    for path, _ in scratch_results:
        print("     %s" % path)
    if raw:
        for arm in sorted(raw):
            vals = sorted(set(v for v in raw[arm].values()))
            print("   RAW %-10s per-card rc=%s  uniform=%s" % (arm, raw[arm], len(vals) == 1))
