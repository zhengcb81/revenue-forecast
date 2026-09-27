"""R3 one-shot: compact per-arm summary of the four band JSONs (basis for deliverables)."""
import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]

BANDS = [
    ("red", "red/band-red.json"),
    ("green", "green/band-green.json"),
    ("mut1_M1", "mut1/band-mut-m1.json"),
    ("mut2_M2upper", "mut2/band-mut-m2upper.json"),
]

out = {}
for name, rel in BANDS:
    d = json.loads((ATTEMPT / rel).read_text(encoding="utf-8"))
    rows = []
    for r in d["results"]:
        ev = r.get("events", {})
        shapes = []
        for rep in r.get("reports", []):
            lr = str(rep.get("longrepr", ""))
            if "launcher_exception" in lr:
                shapes.append("launcher_exception")
            elif "assert 1 == 0" in lr or "assert completed.returncode == 0" in lr:
                shapes.append("rc_gate")
            elif "StopIteration" in lr:
                shapes.append("StopIteration")
        rows.append({
            "run": r["run"], "rc": r["returncode"], "verdict": r["verdict"],
            "wall_seconds": r["wall_seconds"],
            "assertion": r.get("assertion", "")[:120],
            "child_started_count": ev.get("child_started_count"),
            "hang_timeout_seconds": ev.get("hang_timeout_seconds"),
            "statuses": ev.get("statuses"),
            "tside_trace": r.get("tside_trace"),
            "failure_shapes": sorted(set(shapes)),
        })
    out[name] = {
        "band_file": rel,
        "suite_sha256": d.get("suite_sha256"),
        "condition": d.get("condition"), "burners": d.get("burners"),
        "runs": d.get("runs"), "tally": d.get("tally"),
        "driver_timeout_seconds": d.get("driver_timeout_seconds"),
        "started_utc": d.get("started_utc"), "finished_utc": d.get("finished_utc"),
        "ambient": d.get("ambient_sample"),
        "rows": rows,
    }

(ATTEMPT / "evidence" / "bands-summary.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
for name, d in out.items():
    print(name, d["tally"], "rcs:", [r["rc"] for r in d["rows"]],
          "shapes:", sorted({s for r in d["rows"] for s in r["failure_shapes"]}))
