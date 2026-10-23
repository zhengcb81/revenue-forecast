import json
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
ex = json.loads((W / "delivery/w09/research/excerpts.json").read_text(encoding="utf-8"))
cc = json.loads((W / "delivery/w09/research/claim-changes.json").read_text(encoding="utf-8"))
lines = []
for eid in ("chemistry_dm_operating", "chemistry_r_operating", "chemistry_non_tides_operating"):
    r = ex["excerpts"][eid]
    lines.append("%s full contig sha: %s" % (eid, r["contiguous_range_sha256"]))
rpo = cc["out_of_union_requirement_repairs"]["rows"][0]
lines.append("RPO row full contig sha: %s" % rpo["contiguous_range_sha256"])
lines.append("RPO row excerpt_id: %s span=%s" % (rpo["excerpt_id"], rpo["contiguous_span"]))
# sample union row full hash
s = cc["rows"][0]
lines.append("sample union row (%s) full contig sha: %s" % (s["claim_id"], s["contiguous_range_sha256"]))
(W / "delivery/w09/review/_probe2/f11_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
