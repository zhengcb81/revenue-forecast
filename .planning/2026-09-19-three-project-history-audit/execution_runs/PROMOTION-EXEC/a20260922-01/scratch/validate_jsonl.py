import json,sys
for i,l in enumerate(open(sys.argv[1],encoding="utf-8"),1):
    l=l.strip()
    if not l: continue
    o=json.loads(l)
    print(i, o["row"], "::", o["status"])
