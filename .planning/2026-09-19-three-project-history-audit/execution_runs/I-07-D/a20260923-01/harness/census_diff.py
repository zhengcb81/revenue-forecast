import json, sys
b = json.load(open(sys.argv[1], encoding="utf-8"))
a = json.load(open(sys.argv[2], encoding="utf-8"))
if isinstance(b, dict): b = [b]
if isinstance(a, dict): a = [a]
bids = {int(p["ProcessId"]) for p in b}
aids = {int(p["ProcessId"]) for p in a}
gone = [p for p in b if int(p["ProcessId"]) not in aids]
real = [p for p in gone if p.get("CommandLine") and "source_catalog" in p["CommandLine"]
        and not any(m in p["CommandLine"] for m in ("I-07-D", "i07d", "run_d_matrix",
                    "writer.py", "hold_file", "lock_catalog"))]
out = {"before": len(bids), "after": len(aids), "gone_count": len(gone),
       "gone": [{"pid": p["ProcessId"], "name": p["Name"],
                 "cmd": (p.get("CommandLine") or "")[:200]} for p in gone],
       "real_source_catalog_gone": len(real),
       "note": "all killed PIDs must appear in this card's pid manifests"}
json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"before": len(bids), "after": len(aids), "gone": len(gone),
                  "real_gone": len(real)}))
for p in real: print("REAL GONE:", p["ProcessId"], (p.get("CommandLine") or "")[:150])
