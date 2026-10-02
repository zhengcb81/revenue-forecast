"""Coverage before/after for the three B-group files (branch coverage)."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
OUT = Path(__file__).resolve().parent
FLOORS = {"producer_events.py": 95, "identity_cli.py": 82,
          "artifact_read_model.py": None}
REQUIRED = {"producer_events.py": True, "identity_cli.py": False,
            "artifact_read_model.py": None}


def load(p):
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    r = {}
    for k, v in d["files"].items():
        s = v["summary"]
        tot = s.get("num_statements", 0) + s.get("num_branches", 0)
        cov = s.get("covered_lines", 0) + s.get("covered_branches", 0)
        name = k.replace("\\", "/").split("source_catalog/")[-1]
        r[name] = {
            "stmts": s.get("num_statements"), "cov_lines": s.get("covered_lines"),
            "branches": s.get("num_branches"), "cov_branches": s.get("covered_branches"),
            "pct": round(100.0 * cov / tot, 1) if tot else None,
        }
    return r


before = load(OUT / "cov_before.json")
after = load(OUT / "cov_after.json")
print(f"{'module':26s} {'before':>34s} {'after':>34s}  floor  verdict")
for name in sorted(set(before) | set(after)):
    b, a = before.get(name), after.get(name)
    floor = FLOORS.get(name)
    pct = a["pct"] if a else None
    if floor is None:
        verdict = "n/a (no floor)"
    else:
        verdict = "OK" if pct >= floor - 0.5 else "REGRESS"
    print(f"{name:26s} {str(b):>34s} {str(a):>34s}  {str(floor):>5s}  {verdict}")
    if floor is not None:
        print(f"{'':26s} pct {b['pct']} -> {a['pct']} "
              f"(floor {floor}{' (required)' if REQUIRED[name] else ''})")
