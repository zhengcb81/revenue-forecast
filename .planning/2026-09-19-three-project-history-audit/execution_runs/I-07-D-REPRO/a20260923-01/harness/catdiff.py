import json, sys
b = json.load(open(sys.argv[1], encoding="utf-8"))["production_catalog"]
a = json.load(open(sys.argv[2], encoding="utf-8"))["production_catalog"]
keys = sorted(set(b) | set(a))
for k in keys:
    if b.get(k) != a.get(k):
        print(f"DIFF {k}: before={b.get(k)} after={a.get(k)}")
    else:
        print(f"SAME {k}: {b.get(k)}")
