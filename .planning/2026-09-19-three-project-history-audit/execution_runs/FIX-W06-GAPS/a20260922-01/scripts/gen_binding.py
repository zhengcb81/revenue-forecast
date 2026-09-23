"""Generate binding.json (before/after pins) for FIX-W06-GAPS a20260922-01."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

A = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
         r"\2026-09-19-three-project-history-audit\execution_runs"
         r"\FIX-W06-GAPS\a20260922-01")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


before_files = sorted((A / "before").rglob("*"))
iso_files = sorted(p for p in (A / "iso").rglob("*") if p.is_file())
script_files = sorted(p for p in (A / "scripts").rglob("*.py") if p.is_file())
evidence_files = sorted(p for p in (A / "evidence").rglob("*") if p.is_file())

manifest = json.loads((A / "before" / "MANIFEST.json").read_text(encoding="utf-8-sig"))

binding = {
    "attempt": "FIX-W06-GAPS/a20260922-01",
    "card": "FIX-W06-GAPS",
    "owner_ruling": "fail 的全部要修复 / 发现的缺陷都要全部修复 / 所有存疑都要确认",
    "frozen_oracle": {"path": "oracle.md", "sha256": sha(A / "oracle.md"),
                      "appends": ["A (P7 key revision)", "B (P6-B commit boundary)",
                                  "C (mutation checklist)", "D (P7 tension resolution)"]},
    "before_originals": [
        {"copy": str(p.relative_to(A)), "sha256": sha(p)}
        for p in before_files if p.is_file()
    ],
    "before_manifest": manifest,
    "after_files": [
        {"path": str(p.relative_to(A)), "sha256": sha(p)}
        for p in iso_files
    ],
    "harness_scripts": [
        {"path": str(p.relative_to(A)), "sha256": sha(p)}
        for p in script_files
    ],
    "evidence_files": [
        {"path": str(p.relative_to(A)), "sha256": sha(p), "bytes": p.stat().st_size}
        for p in evidence_files
    ],
    "product_writes": [
        {
            "repo": "revenue-forecast",
            "path": r"C:\Users\郑曾波\Projects\revenue-forecast\tests\test_message_contract_pins.py",
            "kind": "new test file (P4-SCOPE face 2, parent-authorized test-only surface)",
            "before_sha256": None,
            "after_sha256": sha(Path(r"C:\Users\郑曾波\Projects\revenue-forecast\tests\test_message_contract_pins.py")),
            "identical_to_iso_copy": sha(Path(r"C:\Users\郑曾波\Projects\revenue-forecast\tests\test_message_contract_pins.py"))
            == sha(A / "iso" / "rf" / "test_message_contract_pins.py"),
        },
        {
            "repo": "revenue-forecast",
            "path": r"C:\Users\郑曾波\Projects\revenue-forecast\tests\test_fc905b_trusted_receipt.py",
            "kind": "modified test file (loose regex -> verbatim pin, P4-SCOPE)",
            "before_sha256": sha(A / "before" / "rf" / "test_fc905b_trusted_receipt.py"),
            "after_sha256": sha(Path(r"C:\Users\郑曾波\Projects\revenue-forecast\tests\test_fc905b_trusted_receipt.py")),
            "identical_to_iso_copy": sha(Path(r"C:\Users\郑曾波\Projects\revenue-forecast\tests\test_fc905b_trusted_receipt.py"))
            == sha(A / "iso" / "rf" / "test_fc905b_trusted_receipt.py"),
        },
    ],
    "product_source_integrity": [
        {"path": m["source_path"], "sha256_now": sha(Path(m["source_path"])),
         "sha256_before": m["source_sha256"], "unchanged": sha(Path(m["source_path"])) == m["source_sha256"]}
        for m in manifest if "tests\\" not in m["source_path"]
    ],
    "anchors": {
        "candidate_processing_demand_store": "7bc5feb0cb5e50227a49ac7322c654f84b04f4b71d9d6578571f0899405b8f7f",
        "product_prompt_injection": "7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618",
    },
}

(A / "binding.json").write_text(
    json.dumps(binding, ensure_ascii=False, indent=2), encoding="utf-8")
print("binding.json written")
for entry in binding["product_writes"]:
    print(f"  product write: {entry['path']} identical_to_iso={entry['identical_to_iso_copy']}")
print(f"  product sources unchanged: {all(e['unchanged'] for e in binding['product_source_integrity'])}")
