"""Final boundary verification for B1-PREREQ (run AFTER all arms + probe).

Checks, prints one JSON object, exit 0 iff everything matches:
  1. SRC oracle append-only proofs: markers r5/r6 at pre+1, every frozen prefix
     hash still matches (27697 / 31081 / 35840 / 39287 / post-r5).
  2. B1's frozen files unchanged (test_b1_rem.py, before/*, reviewer_report.md).
  3. B1's fixed-tree product files unchanged (the four pins) — this card never
     wrote them.
  4. Production anchors unchanged + trust file absent + git porcelain empty for
     scripts/ tests/ config/ artifacts/ (read-only git status).
  5. F1 truth re-measured from executed bytes: PUBLICATION_ATTESTATION_FIELDS
     in the fixed tree == exactly the 10-field set (no result_sha256).
  6. freeze.json chain re-verifies.

Usage: python final_integrity_check.py <attempt_root> <src_attempt> <prod_root>
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MY = Path(sys.argv[1]).resolve()
SRC = Path(sys.argv[2]).resolve()
PROD = Path(sys.argv[3]).resolve()

FIXED_PINS = {
    "scripts/revenue_publication.py": "bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0",
    "scripts/revenue_core.py": "8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883",
    "scripts/revenue_report.py": "212f00598feca408dc429d4c7a5332131ce25f1165b079347e4b295345df7d3b",
    "scripts/contracts/evidence.py": "054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561",
}
SRC_PINS = {
    "test_b1_rem.py": "636b43c8d8e1dc59ccfa36d7c71125ea9b8665222f587510444a3656b6700c16",
    "reviewer_report.md": "6bfd2922cdf3418416731e62098567d20ab1dcdc98429d8cc1e899e721e7951b",
    "before/b1_unfixed.stdout.txt": "58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335",
    "before/frozen_artifacts.json": "4721d1fbcb620346fe19c93ef793d527e644bd3e096bd5a014f576caab82b1f4",
}
PROD_PINS = {
    "scripts/revenue_publication.py": "183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba",
    "scripts/revenue_report.py": "a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f",
    "scripts/revenue_core.py": "1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae",
    "scripts/contracts/evidence.py": "054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561",
}
PREFIXES = {
    27697: "81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281",
    31081: "60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4",
    35840: "231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523",
    39287: "fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae",
}
TEN_FIELDS = {
    "attestation_payload_schema_version", "domain_separator", "issuer", "key_id",
    "algorithm", "fingerprint", "request_id", "payload_sha256", "signed_at",
    "signature",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    report: dict = {"checks": {}, "failures": []}

    def check(name: str, ok: bool, detail):
        report["checks"][name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            report["failures"].append(name)

    # 1. SRC oracle append-only proofs
    oracle = (SRC / "oracle.md").read_bytes()
    proof5 = json.loads((MY / "scratch/append_oracle_r5.stdout.json").read_text(encoding="utf-8"))
    proof6 = json.loads((MY / "scratch/append_oracle_r6.stdout.json").read_text(encoding="utf-8"))
    r5_pre = proof5["pre_bytes"]
    r6_pre = proof6["pre_bytes"]
    prefix_meas = {str(n): hashlib.sha256(oracle[:n]).hexdigest() for n in PREFIXES}
    check("oracle_prefix_hashes", all(prefix_meas[str(n)] == h for n, h in PREFIXES.items()), prefix_meas)
    check(
        "oracle_marker_r5_at_pre_plus_1",
        oracle[39287:39288] == b"\n" and oracle[39288:].startswith(b"## Revision r5"),
        {"byte_at_39287": oracle[39287:39288].decode("latin1")},
    )
    check(
        "oracle_marker_r6_at_pre_plus_1",
        oracle[r6_pre : r6_pre + 1] == b"\n"
        and oracle[r6_pre + 1 :].startswith(b"## Revision r6"),
        {"r6_pre_bytes": r6_pre},
    )
    check("proof5_frozen_prefix_untouched", proof5["frozen_prefix_untouched"], proof5["append_marker_offset"])
    check("proof6_frozen_prefix_untouched", proof6["frozen_prefix_untouched"], proof6["append_marker_offset"])
    check("oracle_r5_prefix_still_stable", hashlib.sha256(oracle[:r5_pre]).hexdigest() == proof5["pre_sha256"], r5_pre)

    # 2. B1 frozen files unchanged
    src_now = {rel: sha256_file(SRC / rel) for rel in SRC_PINS}
    check("b1_frozen_files_unchanged", src_now == SRC_PINS, src_now)

    # 3. fixed tree product files unchanged (this card never wrote them)
    fixed_now = {rel: sha256_file(SRC / "iso/fixed/rf" / rel) for rel in FIXED_PINS}
    check("iso_fixed_product_files_unchanged", fixed_now == FIXED_PINS, fixed_now)

    # 4. production zero-write
    prod_now = {rel: sha256_file(PROD / rel) for rel in PROD_PINS}
    check("production_anchors_unchanged", prod_now == PROD_PINS, prod_now)
    trust_absent = not (PROD / "config/trusted_signer_public_keys.json").exists()
    check("production_trust_file_still_absent", trust_absent, str(PROD / "config/trusted_signer_public_keys.json"))
    porcelain = subprocess.run(
        ["git", "-C", str(PROD), "status", "--porcelain", "--untracked-files=all",
         "--", "scripts", "tests", "config", "artifacts"],
        capture_output=True, text=True, timeout=120,
    )
    check(
        "production_git_porcelain_empty",
        porcelain.returncode == 0 and porcelain.stdout.strip() == "",
        {"rc": porcelain.returncode, "stdout_bytes": len(porcelain.stdout), "stdout": porcelain.stdout[:2000]},
    )

    # 5. F1 truth from executed bytes: 10-field set in the fixed tree
    src_py = (SRC / "iso/fixed/rf/scripts/revenue_publication.py").read_text(encoding="utf-8")
    tree = ast.parse(src_py)
    fields_value = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "PUBLICATION_ATTESTATION_FIELDS":
                    fields_value = set(ast.literal_eval(node.value))
    check(
        "fixed_tree_attestation_fields_is_exactly_10",
        fields_value == TEN_FIELDS,
        {"measured": sorted(fields_value) if fields_value else None,
         "count": len(fields_value) if fields_value else None,
         "has_result_sha256": "result_sha256" in (fields_value or set()),
         "has_receipt_sha256": "receipt_sha256" in (fields_value or set())},
    )

    # 5b. frozen test's ATTESTATION_FIELDS is the same 10 (SRC frozen file + my copy)
    test_src = (SRC / "test_b1_rem.py").read_text(encoding="utf-8")
    ttree = ast.parse(test_src)
    test_fields = None
    for node in ttree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "ATTESTATION_FIELDS":
                    test_fields = set(ast.literal_eval(node.value))
    check("frozen_test_attestation_fields_is_exactly_10", test_fields == TEN_FIELDS,
          {"count": len(test_fields) if test_fields else None})

    # 6. freeze chain re-verification
    freeze = json.loads((MY / "freeze.json").read_text(encoding="utf-8"))
    chain_ok = True
    prev = "0" * 64
    mismatches = []
    for entry in freeze["entries"]:
        if entry["prev_entry_sha256"] != prev:
            chain_ok = False
            mismatches.append(f"{entry['id']}: prev link")
        body = {k: v for k, v in entry.items() if k != "entry_sha256"}
        body_canon = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if hashlib.sha256(body_canon).hexdigest() != entry["entry_sha256"]:
            chain_ok = False
            mismatches.append(f"{entry['id']}: entry hash")
        live = sha256_file(Path(entry["path"]))
        if live != entry["sha256"]:
            # SRC oracle legitimately changed after freeze (r5/r6 appends) —
            # that entry is pinned as a PREFIX, verified in step 1 instead.
            if entry["id"] in ("src_oracle_pre_r5",):
                raw = Path(entry["path"]).read_bytes()
                n = entry.get("prefix_bytes", entry["bytes"])
                prefix_live = hashlib.sha256(raw[:n]).hexdigest()
                if prefix_live != entry.get("prefix_sha256", entry["sha256"]):
                    chain_ok = False
                    mismatches.append(f"{entry['id']}: prefix {prefix_live}")
            else:
                chain_ok = False
                mismatches.append(f"{entry['id']}: live {live} != {entry['sha256']}")
        prev = entry["entry_sha256"]
    check("freeze_chain_verifies", chain_ok, mismatches)

    report["all_ok"] = not report["failures"]
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
