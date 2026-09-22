"""Build binding.json for B1-PREREQ — computes every pin fresh (no hand-typed
hashes) over: SRC inputs (live + prefix + append proofs), this attempt's
artifacts, the evidence manifest, and production anchors. Writes binding.json.
Usage: python build_binding.py <attempt_root> <src_attempt> <prod_root>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

MY = Path(sys.argv[1]).resolve()
SRC = Path(sys.argv[2]).resolve()
PROD = Path(sys.argv[3]).resolve()


def h(path: Path) -> dict:
    b = path.read_bytes()
    return {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}


def main() -> int:
    p5 = json.loads((MY / "scratch/append_oracle_r5.stdout.json").read_text(encoding="utf-8"))
    p6 = json.loads((MY / "scratch/append_oracle_r6.stdout.json").read_text(encoding="utf-8"))
    fz = json.loads((MY / "freeze.json").read_text(encoding="utf-8"))
    m6 = json.loads((MY / "scratch/mutations/m6_proof.json").read_text(encoding="utf-8"))
    d6 = json.loads((MY / "scratch/mutations/m6_delta_proof.json").read_text(encoding="utf-8"))
    integ = json.loads((MY / "evidence/final_integrity_check_v2.stdout.txt").read_text(encoding="utf-8"))

    oracle_raw = (SRC / "oracle.md").read_bytes()
    oracle_prefix = hashlib.sha256(oracle_raw[:39287]).hexdigest()

    evidence_manifest = (MY / "evidence/SHA256SUMS.txt").read_text(encoding="ascii").splitlines()

    binding = {
        "card_id": "B1-PREREQ",
        "attempt_id": "a20260922-01",
        "binding_status": "bound",
        "bound_entry_count": 0,  # filled below
        "generated_by": "scratch/build_binding.py (hashes computed, never transcribed)",
        "status_note": "binding.json is written LAST among the prose carriers; it pins handoff.json/decision.md/changes.diff/evidence. It is not itself signed — review_pending stands.",

        "src_pinned": {
            "oracle.md_pre_r5_prefix": {"prefix_bytes": 39287, "prefix_sha256": oracle_prefix,
                                        "matches_freeze_pin": oracle_prefix == "fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae"},
            "oracle.md_post_r5": {"bytes": p5["post_bytes"], "sha256": p5["post_sha256"],
                                  "marker_offset": p5["append_marker_offset"], "frozen_prefix_untouched": p5["frozen_prefix_untouched"]},
            "oracle.md_post_r6_current": dict(h(SRC / "oracle.md"),
                                              marker_offset=p6["append_marker_offset"],
                                              pre_append_sha256=p6["pre_sha256"],
                                              frozen_prefix_untouched=p6["frozen_prefix_untouched"]),
            "oracle_append_proof_r5": h(MY / "scratch/append_oracle_r5.stdout.json"),
            "oracle_append_proof_r6": h(MY / "scratch/append_oracle_r6.stdout.json"),
            "oracle_pre_r5_snapshot": h(MY / "scratch/oracle_pre_r5.md"),
            "reviewer_report.md_on_disk": dict(h(SRC / "reviewer_report.md"),
                                               self_pinned_final_byte_digest="73feb0593b44ffeb448bc5f5b1cea9800f4cc9fb59f40ca19e9aae8038c104fa"),
            "test_b1_rem.py_untouched": dict(h(SRC / "test_b1_rem.py"),
                                             matches_pin=h(SRC / "test_b1_rem.py")["sha256"] == "636b43c8d8e1dc59ccfa36d7c71125ea9b8665222f587510444a3656b6700c16"),
            "iso_fixed_product_files": {rel: h(SRC / "iso/fixed/rf" / rel) for rel in (
                "scripts/revenue_publication.py", "scripts/revenue_core.py",
                "scripts/revenue_report.py", "scripts/contracts/evidence.py")},
            "iso_unfixed_revenue_publication": h(SRC / "iso/rf/scripts/revenue_publication.py"),
            "before_b1_unfixed_stdout_r4_gap_object": h(SRC / "before/b1_unfixed.stdout.txt"),
            "before_frozen_artifacts": h(SRC / "before/frozen_artifacts.json"),
        },

        "my_attempt_pinned": {
            "freeze.json": dict(h(MY / "freeze.json"), chain_head=fz["chain_head"], entry_count=fz["entry_count"],
                                ordering=fz["ordering_rule"][:120] + "..."),
            "oracle.md_frozen": h(MY / "oracle.md"),
            "test_r13_equiv_rem41.py": h(MY / "test_r13_equiv_rem41.py"),
            "commands.json_byte_frozen": h(MY / "commands.json"),
            "conftest.py": h(MY / "conftest.py"),
            "runner/run_arm.ps1": h(MY / "runner/run_arm.ps1"),
            "scratch/apply_m6.py": h(MY / "scratch/apply_m6.py"),
            "scratch/verify_m6_delta.py": h(MY / "scratch/verify_m6_delta.py"),
            "scratch/append_revision.py": h(MY / "scratch/append_revision.py"),
            "scratch/build_freeze.py": h(MY / "scratch/build_freeze.py"),
            "scratch/final_integrity_check.py_frozen_tool": dict(
                h(MY / "scratch/final_integrity_check.py"),
                note="FROZEN tool; its run burned label final_integrity_check with a disclosed tool defect (traceback preserved). NOT edited after freeze."),
            "scratch/final_integrity_check_v2.py": dict(
                h(MY / "scratch/final_integrity_check_v2.py"),
                note="disclosed post-freeze successor (frozenset AST unwrap); ran under NEW label; ran 14/14 ok"),
            "scratch/probe_e21_binding.py": h(MY / "scratch/probe_e21_binding.py"),
            "scratch/oracle_revision_r5.md": h(MY / "scratch/oracle_revision_r5.md"),
            "scratch/oracle_revision_r6.md": h(MY / "scratch/oracle_revision_r6.md"),
            "scratch/make_changes_diff.py": h(MY / "scratch/make_changes_diff.py"),
            "scratch/m6_proof.json": h(MY / "scratch/mutations/m6_proof.json"),
            "scratch/m6_delta_proof.json": dict(h(MY / "scratch/mutations/m6_delta_proof.json"),
                                                exactly_one_changed_file=d6["exactly_one_changed_file"],
                                                mutant_file_sha256=m6["post_sha256"],
                                                target_pre_sha256=m6["pre_sha256"], pre_match=m6["pre_match"]),
            "evidence/SHA256SUMS.txt": dict(h(MY / "evidence/SHA256SUMS.txt"), entries=len(evidence_manifest)),
            "evidence_key_outputs": {name: h(MY / "evidence" / name) for name in (
                "arm1_node_on_fixed.stdout.txt", "arm2_node_on_m6.stdout.txt",
                "arm3_frozen12_on_m6.stdout.txt", "arm4_node_on_unfixed.stdout.txt",
                "probe_e21.stdout.txt", "append_r5.stdout.txt", "append_r6.stdout.txt",
                "m6_build.stdout.txt", "final_integrity_check.stdout.txt",
                "final_integrity_check_v2.stdout.txt", "README.md")},
            "decision.md": h(MY / "decision.md"),
            "handoff.json": h(MY / "handoff.json"),
            "changes.diff": h(MY / "changes.diff"),
            "recovery/README.md": h(MY / "recovery/README.md"),
        },

        "production_pinned": {
            "scripts/revenue_publication.py": h(PROD / "scripts/revenue_publication.py"),
            "scripts/revenue_report.py": h(PROD / "scripts/revenue_report.py"),
            "scripts/revenue_core.py": h(PROD / "scripts/revenue_core.py"),
            "scripts/contracts/evidence.py": h(PROD / "scripts/contracts/evidence.py"),
            "artifacts/registry/publications.jsonl": h(PROD / "artifacts/registry/publications.jsonl"),
            "config/trusted_signer_public_keys.json": "ABSENT (correct fail-closed default; verified post-run)",
            "git_porcelain_scripts_tests_config_artifacts": "EMPTY (evidence/final_integrity_check_v2.stdout.txt check production_git_porcelain_empty)",
        },

        "integrity_summary": {
            "final_check": "evidence/final_integrity_check_v2.stdout.txt",
            "all_ok": integ.get("all_ok"),
            "checks_run": len(integ.get("checks", {})),
            "failures": integ.get("failures"),
        },

        "open_disclosures": [
            "arm4 control deviation (handoff.deviations.arm4_control; decision.md F2)",
            "B1 r1 RED stdout + r1 test file unclosable historical gap (F4/REM-43)",
            "E21 not implemented — documented-not-bindable-here (F3/REM-42)",
            "F6 measurement divergence recorded (handoff.findings.F6)",
            "freeze build history: 3 pre-execution builds (decision.md D-3)",
        ],
    }
    binding["bound_entry_count"] = (
        len(binding["src_pinned"]) + len(binding["my_attempt_pinned"]) + len(binding["production_pinned"])
    )
    out = MY / "binding.json"
    out.write_text(json.dumps(binding, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"binding": str(out), "bound_entry_count": binding["bound_entry_count"],
                      "integrity_all_ok": binding["integrity_summary"]["all_ok"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
