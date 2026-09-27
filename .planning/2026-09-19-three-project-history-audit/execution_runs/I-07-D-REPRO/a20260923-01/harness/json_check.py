import json, sys, pathlib
D = pathlib.Path(sys.argv[1])
ok, bad = [], []
for p in list(D.glob("*.json")) + list((D/"evidence").rglob("*.json")):
    try:
        json.loads(p.read_text(encoding="utf-8"))
        ok.append(str(p.relative_to(D)))
    except Exception as e:
        bad.append(f"{p.relative_to(D)}: {e}")
print(f"json_ok={len(ok)} json_bad={len(bad)}")
for b in bad: print("BAD:", b)
