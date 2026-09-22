"""Post-write self-check for the I-08-C fix round (run AFTER handoff/binding/
commands are final). Validates quoted hashes, both prefix proofs, the R4-4 run
contract, the handoff transition fields, node count, and production read-only.

Run:  C:\\Miniconda\\python.exe -B scratch/fixround/selfcheck.py
Exit: 0 iff errors == [] ; JSON report on stdout.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parents[1]
REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")

HEX64 = re.compile(r"^([0-9a-f]{64})")

ORACLE_R4_PREIMAGE = ("22335", "94a853e978e34f522820cc2e03548fffe8ee2e599725d7a0131f872c93add8b3")
ORACLE_R2_BODY = ("6831", "478bd70e0a1dfbfb924ebec0175bb2bdcdd199880de1c554de099d8ac8723c90")
TEST_R4 = ("13152", "3f83fdf2b7d81aba9a0bbafeb08c6c5fdf9344607fce5e5a34bb920da6454fbb")
MUTATION = ("12976", "eb19e62846ed7e03f5fe74aee5a5debca9f84cf0a790df5d1e24d089f04d0858")

PRODUCTION_ANCHORS = {
    "scripts/revenue_publication.py": "183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba",
    "scripts/revenue_core.py": "1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae",
    "scripts/revenue_report.py": "a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f",
    "scripts/publication_registry.py": "29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344",
    "artifacts/registry/publications.jsonl": "bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91",
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def size(p: Path) -> int:
    return p.stat().st_size


def check_quoted_hashes(mapping: dict, base: Path, errors: list, label: str) -> int:
    checked = 0
    for key, value in mapping.items():
        if not isinstance(value, str):
            continue
        m = HEX64.match(value)
        if not m:
            continue  # 'self ...', 'hash on receipt ...' etc.
        path = base / key
        if not path.is_file():
            errors.append(f"{label}: quoted file missing: {key}")
            continue
        got = sha256(path)
        if got != m.group(1):
            errors.append(f"{label}: {key} quoted {m.group(1)} != on-disk {got}")
        checked += 1
    return checked


def main() -> int:
    errors: list[str] = []
    notes: list[str] = []

    # 1. every JSON in the attempt root parses
    for name in ("handoff.json", "binding.json", "commands.json", "exploratory_manifest.json"):
        try:
            json.loads((ATTEMPT / name).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"JSON parse failed: {name}: {exc}")

    handoff = json.loads((ATTEMPT / "handoff.json").read_text(encoding="utf-8"))
    binding = json.loads((ATTEMPT / "binding.json").read_text(encoding="utf-8"))

    # 2. quoted deliverable / binding hashes match disk
    n1 = check_quoted_hashes(handoff["deliverables"], ATTEMPT, errors, "handoff.deliverables")
    cur = binding["post_run_hashes"]["current_after_fix_round"]
    n2 = check_quoted_hashes(cur, ATTEMPT, errors, "binding.post_run_hashes.current")
    notes.append(f"verified {n1} handoff deliverable hashes and {n2} binding post-run hashes")

    # 3. both prefix proofs
    oracle = (ATTEMPT / "oracle.md").read_bytes()
    n_pre, h_pre = ORACLE_R4_PREIMAGE
    if hashlib.sha256(oracle[: int(n_pre)]).hexdigest() != h_pre:
        errors.append("prefix proof failed: oracle.md[0:22335] != 94a853e9...")
    n_r2, h_r2 = ORACLE_R2_BODY
    if hashlib.sha256(oracle[: int(n_r2)]).hexdigest() != h_r2:
        errors.append("prefix proof failed: oracle.md[0:6831] != 478bd70e...")
    proof = json.loads((HERE / "prefix_proof.json").read_text(encoding="utf-8-sig"))
    if proof.get("append_only_proof") is not True:
        errors.append("prefix_proof.json does not report append_only_proof: true")

    # 4. frozen file sizes/hashes
    for path, (n, want), label in (
        (ATTEMPT / "test_i08c_consumer_rejection.py", TEST_R4, "test file"),
        (HERE / "mutation" / "test_i08c_mutation_pinned_gap.py", MUTATION, "mutation file"),
    ):
        if size(path) != int(n) or sha256(path) != want:
            errors.append(
                f"{label} mismatch: {size(path)}B/{sha256(path)} != {n}B/{want}"
            )

    # 5. R4-4 run contract as recorded in rcs.txt
    rcs = (HERE / "rcs.txt").read_text(encoding="utf-8").replace("\r", "")
    expected_rcs = "RUN-A=0\nRUN-B=1\nRUN-B2=1\nRUN-M=1\n"
    if rcs.strip() != expected_rcs.strip():
        errors.append(f"rcs.txt mismatch: {rcs!r} != {expected_rcs!r}")

    # 6. handoff transition fields (never self-signed)
    if handoff.get("status") != "review_pending":
        errors.append(f"status is {handoff.get('status')!r}, expected 'review_pending'")
    if handoff.get("implementer_self_acceptance") is not False:
        errors.append("implementer_self_acceptance must be false")
    if handoff.get("ready_for_re_review") is not True:
        errors.append("ready_for_re_review must be true")
    if "changes_required" not in str(handoff.get("reviewer_verdict", "")):
        errors.append("reviewer_verdict must still record the historical changes_required verdict")
    if handoff.get("fix_record", {}).get("points_at", "").find("revision r4") < 0:
        errors.append("fix_record must point at oracle revision r4")
    if handoff.get("fix_record", {}).get("self_sign") is not False:
        errors.append("fix_record.self_sign must be false")

    # 7. matrix still 13 nodes and the flip landed
    test_src = (ATTEMPT / "test_i08c_consumer_rejection.py").read_text(encoding="utf-8")
    nodes = re.findall(r"^def (test_\w+)\(", test_src, flags=re.M)
    if len(nodes) != 13:
        errors.append(f"expected 13 nodes, found {len(nodes)}")
    if 'match="attestation_missing_record"' not in test_src:
        errors.append("e11 rejection assertion missing")
    if 'match="segment base revenue mismatch"' not in test_src:
        errors.append("e13 rejection assertion missing")
    if "test_e11_host_signed_label_flip_is_rejected_at_consumption" not in nodes:
        errors.append("e11 node id not renamed")
    if "test_e13_segment_base_revenue_forgery_is_rejected_by_output_gates" not in nodes:
        errors.append("e13 node id not renamed")
    if 'os.environ.get("RF_IMPORT_ROOT")' not in test_src:
        errors.append("import-root override missing")

    # 8. production read-only
    for rel, want in PRODUCTION_ANCHORS.items():
        got = sha256(REPO / rel)
        if got != want:
            errors.append(f"production anchor changed: {rel} -> {got}")

    report = {
        "self_check": "PASS" if not errors else "FAIL",
        "errors": errors,
        "notes": notes,
        "oracle_bytes": len(oracle),
        "oracle_sha256": hashlib.sha256(oracle).hexdigest(),
        "nodes": nodes,
        "status": handoff.get("status"),
        "ready_for_re_review": handoff.get("ready_for_re_review"),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
