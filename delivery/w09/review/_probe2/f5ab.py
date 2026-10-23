import json, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
nc = json.loads((W / "delivery/w09/research/native-chain.json").read_text(encoding="utf-8"))
lines = []
lines.append("all_calls_clean: %s" % nc["all_calls_clean"])
lines.append("n_calls: %d" % len(nc["calls"]))
for c in nc["calls"]:
    lines.append("--- call ---")
    lines.append(json.dumps(c, ensure_ascii=False, indent=1)[:2600])
(OUTDIR / "f5a_calls.txt").write_text("\n".join(lines), encoding="utf-8")

lines2 = []
lines2.append("outputs: " + json.dumps(nc.get("outputs"), ensure_ascii=False, indent=1)[:3000])
sc = nc.get("sealed_comparison")
lines2.append("")
lines2.append("sealed_comparison: " + json.dumps(sc, ensure_ascii=False, indent=1)[:6000])
lines2.append("")
lines2.append("stress_minus_main: " + json.dumps(nc.get("stress_minus_main"), ensure_ascii=False, indent=1)[:1500])
(OUTDIR / "f5b_sealed.txt").write_text("\n".join(lines2), encoding="utf-8")
print("ok")
