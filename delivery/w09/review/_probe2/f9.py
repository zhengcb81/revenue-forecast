import json, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
lines = []

# sandboxed rerun output vs on-disk excerpts.json
rerun = (OUTDIR / "excerpts_rerun.json").read_text(encoding="utf-8")
disk = (W / "delivery/w09/research/excerpts.json").read_text(encoding="utf-8")
lines.append("rerun sha=%s" % hashlib.sha256(rerun.encode("utf-8")).hexdigest()[:16])
lines.append("disk  sha=%s" % hashlib.sha256(disk.encode("utf-8")).hexdigest()[:16])
lines.append("byte-identical: %s" % (rerun == disk))

# native-chain.json: where are main_identical_old / stress_identical_old stored?
nc = json.loads((W / "delivery/w09/research/native-chain.json").read_text(encoding="utf-8"))


def hunt(obj, needles, path=""):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in needles:
                hits.append((path + "/" + k, v))
            else:
                hits.extend(hunt(v, needles, path + "/" + k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(hunt(v, needles, path + "/%d" % i))
    return hits


hits = hunt(nc, {"main_identical_old", "stress_identical_old"})
lines.append("main_identical_old / stress_identical_old locations:")
for p, v in hits:
    lines.append("  %s = %s" % (p, v))

# outputs side identical flags
om = hunt(nc["outputs"]["main"], {"snapshot_input_matches_forecast"})
lines.append("outputs.main snapshot_input_matches_forecast: %s" % json.dumps(om))
osn = hunt(nc["outputs"]["stress"], {"snapshot_input_matches_forecast"})
lines.append("outputs.stress snapshot_input_matches_forecast: %s" % json.dumps(osn))

(OUTDIR / "f9_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
