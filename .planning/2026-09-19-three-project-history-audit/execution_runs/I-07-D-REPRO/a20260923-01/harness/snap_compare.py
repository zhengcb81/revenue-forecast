import json, sys, hashlib
def load(p): return json.load(open(p, encoding="utf-8"))
b = load(sys.argv[1]); a = load(sys.argv[2])
same_anchors = all(b["anchors"][k] == a["anchors"][k] for k in b["anchors"])
same_samples = b["production_samples"] == a["production_samples"]
cat_same = b["production_catalog"] == a["production_catalog"]
out = {"anchors_identical": same_anchors, "anchor_count": len(b["anchors"]),
       "samples_identical": same_samples, "production_catalog_stat_identical": cat_same,
       "raw_all_match_before": b.get("production_samples", {}),
       "changed_anchors": [k for k in b["anchors"] if b["anchors"][k] != a["anchors"].get(k)]}
json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:600])
