import hashlib
import json
import sys
from pathlib import Path

attempt = Path(sys.argv[1])

# 1) normalize any BOM (pwsh Set-Content -Encoding UTF8 emitted BOMs) -> strict UTF-8
bom_seen = []
for rel in [
    "evidence/hashes.json",
    "evidence/product_tests_before.txt",
    "evidence/product_tests_after.txt",
    "evidence/product_tests_mutant_m1.txt",
]:
    p = attempt / rel
    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        bom_seen.append(rel)
        p.write_bytes(raw.decode("utf-8-sig").encode("utf-8"))

files = [
    "oracle.md", "oracle_freeze.json", "binding.json", "commands.json",
    "decision.md", "recovery.md", "handoff.json", "changes.diff",
    "iso/prompt_injection_guard.py",
    "scripts/ttl30d_probe.py", "scripts/make_mutants.py",
    "scripts/make_diff.py", "scripts/_final_hashes.py",
    "mutants/m1/prompt_injection_guard.py", "mutants/m2/prompt_injection_guard.py",
    "evidence/red_before.json", "evidence/green_after.json",
    "evidence/green_confirm.json", "evidence/mutation_m1_cap_removed.json",
    "evidence/mutation_m2_pastnow_removed.json",
    "evidence/product_tests_before.txt", "evidence/product_tests_after.txt",
    "evidence/product_tests_mutant_m1.txt", "evidence/caller_audit.txt",
    "evidence/hashes.json",
]
out = {}
boms = []
for rel in files:
    data = (attempt / rel).read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        boms.append(rel)
    out[rel] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}

json_files = [f for f in files if f.endswith(".json")]
for f in json_files:
    json.loads((attempt / f).read_text(encoding="utf-8"))  # strict: proves no BOM remains

prod = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\prompt_injection_guard.py")
prods = hashlib.sha256(prod.read_bytes()).hexdigest()  # lowercase
payload = {
    "files": out,
    "json_files": json_files,
    "json_all_valid_strict_utf8": True,
    "bom_normalized": bom_seen,
    "bom_remaining": boms,
    "production_guard_final_sha256": prods,
    "production_expected_sha256": "f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08",
    "production_unchanged": prods == "f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08",
}
(attempt / "evidence" / "final_deliverable_hashes.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps({
    "count": len(out),
    "json_all_valid": True,
    "bom_normalized": bom_seen,
    "bom_remaining": boms,
    "production_unchanged": payload["production_unchanged"],
}))
