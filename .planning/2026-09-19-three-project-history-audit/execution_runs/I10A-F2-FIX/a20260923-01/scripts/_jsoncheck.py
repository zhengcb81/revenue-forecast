import json, sys
from pathlib import Path
att = Path(sys.argv[1])
bad = []
for p in sorted((att/"evidence").rglob("*.json")):
    try:
        json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        bad.append((str(p.relative_to(att)), repr(e)))
for name in ("handoff.json", "frozen_regression_rerun.json"):
    p = att/name
    if p.exists():
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            bad.append((name, repr(e)))
print(json.dumps({"failures": bad, "count": len(bad)}, indent=1))
