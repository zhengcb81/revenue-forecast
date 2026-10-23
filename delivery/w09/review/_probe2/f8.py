import json, hashlib, re
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
lines = []

# --- 1. Sandboxed re-run of verify_excerpts.py (redirect output into _probe2) ---
src = (W / "delivery/w09/tools/verify_excerpts.py").read_text(encoding="utf-8")
target_out = OUTDIR / "excerpts_rerun.json"
patched = src.replace(
    'OUT = Path(__file__).resolve().parents[1] / "research" / "excerpts.json"',
    'OUT = Path(r"%s")' % str(target_out).replace("\\", "\\\\")
)
assert patched != src, "OUT assignment not found"
runner = OUTDIR / "verify_excerpts_rerun.py"
runner.write_text(patched, encoding="utf-8")
lines.append("sandboxed copy written: verify_excerpts_rerun.py (OUT redirected)")

# --- 2. native-chain.json identical/keys ---
nc_text = (W / "delivery/w09/research/native-chain.json").read_text(encoding="utf-8")
keys = sorted(set(re.findall(r'"([a-z0-9_]*identical[a-z0-9_]*)"', nc_text)))
lines.append("identical-related keys in native-chain.json: %s" % json.dumps(keys))
nc = json.loads(nc_text)
# summarize per-scenario identical flags
for side in ("main", "stress"):
    for scen in ("low", "base", "high"):
        blk = nc["sealed_comparison"][side][scen]
        lines.append("sealed_comparison.%s.%s identical=%s" % (side, scen, blk["identical"]))

# --- 3. 18 price negative controls in stress input ---
si = json.loads((W / "delivery/w09/forecast/stress-input.json").read_text(encoding="utf-8"))
sclaims = {c["claim_id"]: c for c in si["evidence_claims"]}
cc = json.loads((W / "delivery/w09/research/claim-changes.json").read_text(encoding="utf-8"))
pnc_ids = cc["price_negative_control"]["claim_ids"]
bad = [cid for cid in pnc_ids if sclaims.get(cid, {}).get("evidence_role") != "conversion_assumption"]
lines.append("stress input: 18 pnc all conversion_assumption: %s (bad: %d)" % (len(bad) == 0, len(bad)))

# --- 4. reconcile_chain.py: does it write or only read? ---
rc = (W / "delivery/w09/tools/reconcile_chain.py").read_text(encoding="utf-8")
writes = [l.strip() for l in rc.splitlines() if "write_text" in l or "open(" in l and any(m in l for m in ("w", "a"))]
lines.append("reconcile_chain.py write operations: %s" % json.dumps(writes[:5]))
lines.append("reconcile_chain.py computes identical_old fields: %s" % json.dumps(sorted(set(re.findall(r'"(main_identical_old|stress_identical_old|[a-z_]*identical[a-z_]*)"', rc)))))

(OUTDIR / "f8_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
