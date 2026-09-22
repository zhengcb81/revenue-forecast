"""Compare the pre-break sweeps across trees; compute regression sets."""
import json
from pathlib import Path

S = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_review_i14d_r4_20260922")

trees = ["product_narrow_r4", "product_narrow_r3", "product_narrow", "product_base"]
data = {}
for t in trees:
    data[t] = json.loads((S / f"prebreak_{t}.json").read_text(encoding="utf-8"))

for t in trees:
    print(f"{t:20s} leaks={len(data[t]['leaks'])}/{len(data[t]['rows'])}")

r4 = set(data["product_narrow_r4"]["leaks"])
r3 = set(data["product_narrow_r3"]["leaks"])
r2 = set(data["product_narrow"]["leaks"])
base = set(data["product_base"]["leaks"])

print()
print("r4 leaks but base does NOT (base-regression):", len(r4 - base))
print(sorted(r4 - base))
print()
print("r3 leaks but base does NOT:", len(r3 - base))
print("r2 leaks but base does NOT:", len(r2 - base))
print()
print("base leaks:", sorted(base))
print()
print("r4 minus r3 (closed by r4):", sorted(r3 - r4))
print("r3 minus r4 (new in r4):", sorted(r4 - r3))
print()

# the marker variants specifically
print("=== marker variants, all trees ===")
for t in trees:
    for r in data[t]["rows"]:
        if r["id"].startswith("pre-mark"):
            print(f"  {t:20s} {r['id']:20s} leaks={r['leaks']!s:5s} out={r['out']!r}")
