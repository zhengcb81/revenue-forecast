import json, re, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
memo = (W / "delivery/w09/research/research-memo.md").read_text(encoding="utf-8")
lines = []

# FIX-2: no stale SHAs, references final ones
lines.append("FIX-2 stale sha '4454ce57' in memo: %s" % ("4454ce57" in memo))
lines.append("FIX-2 stale sha '852ba877' in memo: %s" % ("852ba877" in memo))
lines.append("FIX-2 memo has 770cd309: %s" % ("770cd309" in memo))
lines.append("FIX-2 memo has c0c45687: %s" % ("c0c45687" in memo))
# all sha-like strings in memo
shas = re.findall(r"\b[0-9a-f]{8}\b", memo)
lines.append("memo 8-hex tokens: " + json.dumps(sorted(set(shas))))
# all hex substrings >= 8 in whole memo
shas12 = re.findall(r"[0-9a-f]{8,64}", memo)
lines.append("memo long hex tokens: " + json.dumps(sorted(set(shas12))))

# grep entire delivery tree for stale shas
stale_hits = []
for p in (W / "delivery/w09").rglob("*"):
    if p.is_file() and "_probe" not in str(p) and "_probe2" not in str(p):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "4454ce57" in txt or "852ba877" in txt:
            stale_hits.append(str(p))
lines.append("files in delivery/w09 (excl probes) still containing stale SHAs: " + json.dumps(stale_hits, indent=0))

# native-chain request shas
nc = json.loads((W / "delivery/w09/research/native-chain.json").read_text(encoding="utf-8"))
lines.append("")
lines.append("native-chain top keys: " + ", ".join(nc.keys()))
lines.append(json.dumps({k: nc[k] for k in nc if not isinstance(nc[k], (list, dict))}, ensure_ascii=False, indent=1)[:2000])
(OUTDIR / "f2_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
