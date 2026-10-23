import json, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
reg = (W / "delivery/w09/registry/publications.jsonl").read_text(encoding="utf-8").strip().splitlines()
recs = [json.loads(l) for l in reg]
lines = []
lines.append("n=%d" % len(recs))

# 1) chain: prev_line_sha256 == previous line_sha256
chain_ok = all(recs[i]["prev_line_sha256"] == recs[i-1]["line_sha256"] for i in range(1, len(recs)))
lines.append("prev chain links OK: %s" % chain_ok)
lines.append("first prev_line_sha256: %r (genesis)" % recs[0]["prev_line_sha256"])

# 2) reproduce line_sha256 conventions
def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

for i, r in enumerate(recs):
    conv = {}
    # a: compact json of record minus line_sha256 and prev_line_sha256
    d = {k: v for k, v in r.items() if k not in ("line_sha256",)}
    conv["minus_line_sha256"] = sha(json.dumps(d, sort_keys=True, separators=(",", ":"))) == r["line_sha256"]
    # b: compact json sort_keys with prev set to previous
    d2 = {k: v for k, v in r.items() if k != "line_sha256"}
    conv["minus_line_sha256_unsorted"] = sha(json.dumps(d2, sort_keys=False, separators=(",", ":"))) == r["line_sha256"]
    d3 = {k: v for k, v in r.items() if k not in ("line_sha256", "prev_line_sha256")}
    conv["minus_both"] = sha(json.dumps(d3, sort_keys=True, separators=(",", ":"))) == r["line_sha256"]
    d4 = dict(r)
    d4["line_sha256"] = ""
    conv["line_empty_sorted"] = sha(json.dumps(d4, sort_keys=True, separators=(",", ":"))) == r["line_sha256"]
    lines.append("rec[%d] line_sha256=%s reproducible_conventions: %s" % (i, r["line_sha256"][:12], json.dumps(conv)))

# 3) registry content vs native-chain: input shas and snapshot ids
lines.append("rec input_sha256s: %s" % json.dumps(sorted({r["input_sha256"] for r in recs})))
lines.append("rec artifact_ids: %s" % json.dumps([r.get("artifact_id") for r in recs]))
lines.append("rec types: %s" % json.dumps([r["artifact_type"] for r in recs]))
lines.append("rec registered_at: %s" % json.dumps([r["registered_at"] for r in recs]))

# native-chain snapshot ids for comparison
nc = json.loads((W / "delivery/w09/research/native-chain.json").read_text(encoding="utf-8"))
lines.append("native-chain snapshot ids: main=%s stress=%s" % (
    nc["outputs"]["main"]["snapshot_id"], nc["outputs"]["stress"]["snapshot_id"]))
lines.append("native-chain forecast result shas: main=%s stress=%s" % (
    nc["outputs"]["main"]["snapshot_forecast_result_sha256"][:16], nc["outputs"]["stress"]["snapshot_forecast_result_sha256"][:16]))
# registry result sha for snapshots
for r in recs:
    if r["artifact_type"] == "snapshot":
        lines.append("registry snapshot %s result_sha256=%s" % (r["artifact_id"][:12], r["result_sha256"][:16]))

(OUTDIR / "f6d_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
