"""C-1 route A: derive the identity-scope threshold from measured cadence.

Writes evidence/threshold_derivation.json.  Two independent cadence sources:
  1. the D1 reviewer's measured spacing (64.0-75.2 ms, 6 E1c calls)
  2. this attempt's own E1c re-measurement: spacing = window / (count - 1)
threshold = 2 * max(both maxima), consistent with D1 ruling 5.1(a)2
("alive >= ~2x effective cadence (~150 ms)").
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
EXEC_RUNS = ATTEMPT.parents[1]
REVIEW_EVIDENCE = EXEC_RUNS / "I14A-D1-OPS-REVIEW" / "a20260924-01" / "evidence" / "e1c_samples_inside_life.json"
OWN_REPORT = ATTEMPT / "evidence" / "green" / "sweep" / "E1c-F3-alive-allocate" / "report.json"
OUT = ATTEMPT / "evidence" / "threshold_derivation.json"

NOMINAL = 0.05
HARDCODED = 0.1504

rev = json.loads(REVIEW_EVIDENCE.read_text(encoding="utf-8"))
rev_rows = rev["rows"]
rev_min = float(rev["spacing_ms_min"])
rev_max = float(rev["spacing_ms_max"])

report = json.loads(OWN_REPORT.read_text(encoding="utf-8"))
own_rows = []
for call in report["per_call"]:
    rss = call.get("rss") or {}
    count = int(rss.get("rss_sample_count") or 0)
    window = float(rss.get("rss_sample_window_seconds") or 0.0)
    spacing = (window / (count - 1)) if count > 1 else None
    own_rows.append({
        "child_pid": call.get("child_pid"),
        "fixture_pid_from_stdout": None,   # filled in below from the stdout envelope
        "elapsed_seconds": call.get("elapsed_seconds"),
        "rss_sample_count": count,
        "rss_sample_window_seconds": window,
        "spacing_ms": round(spacing * 1000, 2) if spacing is not None else None,
    })

# fixture pid from the stdout envelope (identity source used by the checker)
for row, call in zip(own_rows, report["per_call"]):
    head = (call.get("stdout_head") or "").splitlines()
    pid = None
    if head:
        try:
            env = json.loads(head[0])
            if isinstance(env, dict) and isinstance(env.get("pid"), int):
                pid = env["pid"]
        except ValueError:
            pid = None
    row["fixture_pid_from_stdout"] = pid

spacings = [r["spacing_ms"] for r in own_rows if r["spacing_ms"] is not None]
own_min = min(spacings)
own_max = max(spacings)

cadence_max = max(own_max, rev_max)
threshold = round(2 * cadence_max / 1000, 4)

payload = {
    "purpose": (
        "C-1 route A: derivation of the identity-scope threshold "
        "(2x effective sampling cadence); frozen in this attempt's oracle.md section 4"
    ),
    "nominal_interval_seconds": NOMINAL,
    "nominal_interval_source": "sealed iso/slo_probe_patched.py:76 RSS_SAMPLE_INTERVAL_SECONDS = 0.05",
    "reviewer_cadence_ms": {
        "min": rev_min,
        "max": rev_max,
        "calls": len(rev_rows),
        "source": "execution_runs/I14A-D1-OPS-REVIEW/a20260924-01/evidence/e1c_samples_inside_life.json",
        "sha256": hashlib.sha256(REVIEW_EVIDENCE.read_bytes()).hexdigest(),
        "rows": [{"call": r["call"], "elapsed": r["elapsed"], "window": r["window"],
                  "count": r["count"], "spacing_ms": r["spacing_ms"]} for r in rev_rows],
    },
    "own_cadence_ms": {
        "min": own_min,
        "max": own_max,
        "calls": len(own_rows),
        "method": "spacing = rss_sample_window_seconds / (rss_sample_count - 1) per E1c call",
        "source": "evidence/green/sweep/E1c-F3-alive-allocate/report.json",
        "sha256": hashlib.sha256(OWN_REPORT.read_bytes()).hexdigest(),
        "rows": own_rows,
    },
    "cadence_max_ms": cadence_max,
    "cadence_max_source": "own measurement" if own_max >= rev_max else "D1 reviewer measurement",
    "threshold_2x_ms": round(cadence_max * 2, 2),
    "threshold_seconds": threshold,
    "threshold_seconds_from_reviewer": round(2 * rev_max / 1000, 4),
    "threshold_seconds_from_own": round(2 * own_max / 1000, 4),
    "hardcoded_in_harness": HARDCODED,
    "hardcoded_consistent": abs(threshold - HARDCODED) < 0.00005,
    "rationale": (
        "a child alive >= 2x the effective cadence is guaranteed >=1 periodic sample "
        "while alive; a shorter child is covered only by the spawn-time race sample, "
        "where fixture identity is not guaranteed on this platform "
        "(D1 ruling 4.3 / 5.1(a)2)"
    ),
    "lifetime_proxy": (
        "per-call elapsed_seconds (child wall time) >= fixture pid true lifetime, "
        "so the scope can only over-include (stricter) and can never weaken the assertion"
    ),
}

OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
parsed = json.loads(OUT.read_text(encoding="utf-8"))
print(json.dumps({
    "own_min_ms": own_min,
    "own_max_ms": own_max,
    "rev_min_ms": rev_min,
    "rev_max_ms": rev_max,
    "cadence_max_ms": cadence_max,
    "threshold_seconds": parsed["threshold_seconds"],
    "hardcoded": parsed["hardcoded_in_harness"],
    "consistent": parsed["hardcoded_consistent"],
}, indent=2))
