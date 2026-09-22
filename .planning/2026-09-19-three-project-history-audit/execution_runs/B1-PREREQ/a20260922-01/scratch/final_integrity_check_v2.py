"""Final boundary verification for B1-PREREQ — v2 (disclosed successor).

IDENTICAL checks to scratch/final_integrity_check.py (whose run is preserved,
burned label `final_integrity_check`, rc 1 + traceback in evidence/*: its
`ast.literal_eval` assumed `PUBLICATION_ATTESTATION_FIELDS` was a plain literal,
but the fixed tree assigns `frozenset({...})`). v2 unwraps set/frozenset call
nodes and records check-level failures instead of crashing. New label:
`final_integrity_check_v2`.

Checks (all as originally frozen in commands.json PR-c9):
  1. SRC oracle append-only proofs: markers r5/r6 at pre+1, frozen prefixes.
  2. B1 frozen files unchanged.
  3. B1 fixed-tree product files unchanged.
  4. Production anchors unchanged + trust absent + git porcelain empty.
  5. F1 truth: PUBLICATION_ATTESTATION_FIELDS == exactly the 10 fields;
     frozen test ATTESTATION_FIELDS == same 10.
  6. freeze.json chain re-verifies (SRC oracle prefix-pinned post-append).

Usage: python final_integrity_check_v2.py <attempt_root> <src_attempt> <prod_root>
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


def assigned_value(tree: ast.Module, name: str):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    v = node.value
                    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in ("frozenset", "set", "tuple", "list") and len(v.args) == 1:
                        v = v.args[0]
                    return ast.literal_eval(v)
    return None


def main() -> int:
    report: dict = {"tool": "final_integrity_check_v2", "checks": {}, "failures": []}

    def check(name: str, fn):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        report["checks"][name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            report["failures"].append(name)

    proof5 = json.loads((MY / "scratch/append_oracle_r5.stdout.json").read_text(encoding="utf-8"))
    proof6 = json.loads((MY / "scratch/append_oracle_r6.stdout.json").read_text(encoding="utf-8"))
    r5_pre, r6_pre = proof5["pre_bytes"], proof6["pre_bytes"]

    def c_prefixes():
        raw = (SRC / "oracle.md").read_bytes()
        meas = {str(n): hashlib.sha256(raw[:n]).hexdigest() for n in PREFIXES}
        return all(meas[str(n)] == h for n, h in PREFIXES.items()), meas
    check("oracle_frozen_prefix_hashes_27697_31081_35840_39287", c_prefixes)

    def c_r5_marker():
        raw = (SRC / "oracle.md").read_bytes()
        ok = raw[39287:39288] == b"\n" and raw[39288:].startswith(b"## Revision r5")
        return ok, {"byte_at_39287": raw[39287:39288].decode("latin1")}
    check("oracle_marker_r5_at_pre_plus_1", c_r5_marker)

    def c_r6_marker():
        raw = (SRC / "oracle.md").read_bytes()
        ok = raw[r6_pre : r6_pre + 1] == b"\n" and raw[r6_pre + 1 :].startswith(b"## Revision r6")
        return ok, {"r6_pre_bytes": r6_pre, "marker_offset": proof6["append_marker_offset"]}
    check("oracle_marker_r6_at_pre_plus_1", c_r6_marker)

    check("proof_r5_frozen_prefix_untouched", lambda: (proof5["frozen_prefix_untouched"], proof5["append_marker_offset"]))
    check("proof_r6_frozen_prefix_untouched", lambda: (proof6["frozen_prefix_untouched"], proof6["append_marker_offset"]))

    def c_src_frozen():
        now = {rel: sha256_file(SRC / rel) for rel in SRC_PINS}
        return now == SRC_PINS, now
    check("b1_frozen_files_unchanged", c_src_frozen)

    def c_fixed():
        now = {rel: sha256_file(SRC / "iso/fixed/rf" / rel) for rel in FIXED_PINS}
        return now == FIXED_PINS, now
    check("iso_fixed_product_files_unchanged", c_fixed)

    def c_prod():
        now = {rel: sha256_file(PROD / rel) for rel in PROD_PINS}
        return now == PROD_PINS, now
    check("production_anchors_unchanged", c_prod)

    check(
        "production_trust_file_still_absent",
        lambda: (not (PROD / "config/trusted_signer_public_keys.json").exists(), str(PROD / "config/trusted_signer_public_keys.json")),
    )

    def c_porcelain():
        p = subprocess.run(
            ["git", "-C", str(PROD), "status", "--porcelain", "--untracked-files=all",
             "--", "scripts", "tests", "config", "artifacts"],
            capture_output=True, text=True, timeout=120,
        )
        return p.returncode == 0 and p.stdout.strip() == "", {"rc": p.returncode, "stdout": p.stdout[:4000]}
    check("production_git_porcelain_empty", c_porcelain)

    def c_fields():
        tree = ast.parse((SRC / "iso/fixed/rf/scripts/revenue_publication.py").read_text(encoding="utf-8"))
        v = assigned_value(tree, "PUBLICATION_ATTESTATION_FIELDS")
        s = set(v) if v else set()
        return s == TEN_FIELDS, {
            "measured": sorted(s), "count": len(s),
            "has_result_sha256": "result_sha256" in s, "has_receipt_sha256": "receipt_sha256" in s,
        }
    check("fixed_tree_PUBLICATION_ATTESTATION_FIELDS_is_exactly_10", c_fields)

    def c_test_fields():
        tree = ast.parse((SRC / "test_b1_rem.py").read_text(encoding="utf-8"))
        v = assigned_value(tree, "ATTESTATION_FIELDS")
        s = set(v) if v else set()
        return s == TEN_FIELDS, {"count": len(s), "has_result_sha256": "result_sha256" in s}
    check("frozen_test_ATTESTATION_FIELDS_is_exactly_10", c_test_fields)

    def c_runtime_record():
        # runtime confirmation from the probe: record_field_count == 10
        probe = json.loads((MY / "evidence/probe_e21.stdout.txt").read_text(encoding="utf-8"))
        setup = probe["setup"]
        return setup["record_field_count"] == 10 and set(setup["record_fields"]) == TEN_FIELDS, setup
    check("runtime_record_from_probe_is_exactly_10", c_runtime_record)

    def c_chain():
        freeze = json.loads((MY / "freeze.json").read_text(encoding="utf-8"))
        ok, prev, mismatches = True, "0" * 64, []
        for entry in freeze["entries"]:
            if entry["prev_entry_sha256"] != prev:
                ok = False
                mismatches.append(f"{entry['id']}: prev link")
            body = {k: v for k, v in entry.items() if k != "entry_sha256"}
            canon = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
            if hashlib.sha256(canon).hexdigest() != entry["entry_sha256"]:
                ok = False
                mismatches.append(f"{entry['id']}: entry hash")
            live = sha256_file(Path(entry["path"]))
            if live != entry["sha256"]:
                if entry["id"] == "src_oracle_pre_r5":
                    raw = Path(entry["path"]).read_bytes()
                    n = entry.get("prefix_bytes", entry["bytes"])
                    pl = hashlib.sha256(raw[:n]).hexdigest()
                    if pl != entry.get("prefix_sha256", entry["sha256"]):
                        ok = False
                        mismatches.append(f"{entry['id']}: prefix {pl}")
                else:
                    ok = False
                    mismatches.append(f"{entry['id']}: live {live} != {entry['sha256']}")
            prev = entry["entry_sha256"]
        return ok, mismatches
    check("freeze_chain_verifies", c_chain)

    report["all_ok"] = not report["failures"]
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
