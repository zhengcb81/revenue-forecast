"""Append fidelity of the r4 carriers + carrier hash pins."""
import hashlib
import json
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")


def sha(b):
    return hashlib.sha256(b).hexdigest()


carrier = json.loads((ATT / "handoff_r4.json").read_text(encoding="utf-8"))

print("=== carrier-registered generation_carriers ===")
for name, meta in carrier["generation_carriers"].items():
    b = (ATT / name).read_bytes()
    print(f"{name}:")
    print(f"   now bytes={len(b)} sha256={sha(b)}")
    print(f"   registered after_bytes={meta['after_bytes']} after_sha256={meta['after_sha256']}")
    print(f"   after matches: {len(b) == meta['after_bytes'] and sha(b) == meta['after_sha256']}")
    pre = b[:meta["before_bytes"]]
    print(f"   prefix[:{meta['before_bytes']}] sha256={sha(pre)}")
    print(f"   registered before_sha256={meta['before_sha256']}")
    print(f"   before matches (pure prefix): {sha(pre) == meta['before_sha256']}")
    print()

print("=== carrier's own hash / the report says it does not register it ===")
b = (ATT / "handoff_r4.json").read_bytes()
print(f"handoff_r4.json: bytes={len(b)} sha256={sha(b)}")

print()
print("=== r4 harnesses + product copy: carrier pins ===")
for rel, meta in (("harness/run_i14d_oracle_r4.py", carrier["harness_generation"]["r4_oracle_harness"]),
                  ("harness/run_rule_table_i14d_r4.py", carrier["harness_generation"]["r4_rule_table_harness"])):
    b = (ATT / rel).read_bytes()
    print(f"{rel}: bytes={len(b)} (reg {meta['bytes']}) sha256={sha(b)} (reg {meta['sha256']}) match={len(b)==meta['bytes'] and sha(b)==meta['sha256']}")
pc = carrier["product_copy"]
b = (ATT / pc["path"]).read_bytes()
print(f"{pc['path']}: bytes={len(b)} (reg {pc['bytes']}) sha256={sha(b)} match={len(b)==pc['bytes'] and sha(b)==pc['sha256']}")

print()
print("=== r3 harnesses: still at the r3-carrier pins? ===")
for rel, want in (("harness/run_i14d_oracle.py", "f7c94c60ce8dffda8d58786d6b20787ff11e4c5c22f06ec1ba1e0307d96a4fe2"),
                  ("harness/run_rule_table_i14d.py", "01a3187e9d5062db316fa89e3fc0feb40f862c782a7ce782aa458c6a0f4f7ed6")):
    b = (ATT / rel).read_bytes()
    print(f"{rel}: sha256={sha(b)} match_pin={sha(b)==want}")

print()
print("=== recorded r3 runs still at the r3-carrier pins? ===")
for rel, want in (("scratch/oracle_r3.json", "c436d62159c5a19b7fa8d2afe6f0aac9c265af98a52c6a669b0a327b69217cf1"),):
    p = ATT / rel
    if p.exists():
        b = p.read_bytes()
        print(f"{rel}: bytes={len(b)} sha256={sha(b)} match_pin={sha(b)==want}")
    else:
        print(f"{rel}: MISSING")

print()
print("=== production anchor ===")
pa = carrier["boundaries"]["production_anchor"]
print("registered:", pa)
