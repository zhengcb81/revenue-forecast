"""I-14-D: final hash pass over the attempt's key artifacts.

    python report_final_hashes_i14d.py --out <attempt>/after/final_hashes.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # <attempt>/harness
ATT = HERE.parent

FILES = {
    "iso_trees": {
        f"iso/{tree}/{rel}": ATT / "iso" / tree / rel
        for tree in ("product_base", "product_narrow", "product_mut_greedy",
                     "product_mut_authnl", "product_mut_auth1_r2",
                     "product_mut_authsplit")
        for rel in ("src/company_wiki/source_catalog/observability.py",
                    "src/company_wiki/source_catalog/worker.py",
                    "src/company_wiki/source_catalog/cli.py")
    },
    "copied_suite_and_drivers": {
        "harness/tests/test_i14c_real_exit_redaction.py":
            HERE / "tests" / "test_i14c_real_exit_redaction.py",
        "harness/tests/test_i14d_single_token.py":
            HERE / "tests" / "test_i14d_single_token.py",
        "harness/drive_real_exit.py": HERE / "drive_real_exit.py",
        "harness/run_guard.py": HERE / "run_guard.py",
        "harness/run_real_cli_exit.py": HERE / "run_real_cli_exit.py",
        "harness/run_exit_probe.py": HERE / "run_exit_probe.py",
        "harness/make_posix_diff.py": HERE / "make_posix_diff.py",
        "harness/verify_git_apply.py": HERE / "verify_git_apply.py",
        "harness/apply_i14d_narrow.py": HERE / "apply_i14d_narrow.py",
        "harness/run_i14d_oracle.py": HERE / "run_i14d_oracle.py",
        "harness/run_rule_table_i14d.py": HERE / "run_rule_table_i14d.py",
        "harness/report_i14d_counts.py": HERE / "report_i14d_counts.py",
        # r2 additions (review F-REV-D-01 / RULING 2)
        "harness/authsplit_probe.py": HERE / "authsplit_probe.py",
        "harness/build_authsplit_proto.py": HERE / "build_authsplit_proto.py",
        "harness/run_mutations_i14d.py": HERE / "run_mutations_i14d.py",
        "harness/report_r2_summary.py": HERE / "report_r2_summary.py",
    },
    "documents_and_evidence": {
        "oracle.md": ATT / "oracle.md",
        "binding.json": ATT / "binding.json",
        "decision.md": ATT / "decision.md",
        "commands.json": ATT / "commands.json",
        "changes.diff": ATT / "changes.diff",
        "reviewer_report.md": ATT / "reviewer_report.md",
        "fix_record.md": ATT / "fix_record.md",
        "after/r2_summary.json": ATT / "after" / "r2_summary.json",
        "after/counts.json": ATT / "after" / "counts.json",
        "after/oracle_narrow.json": ATT / "after" / "oracle_narrow.json",
        "after/rule_table_narrow.json": ATT / "after" / "rule_table_narrow.json",
        "before/oracle_base.json": ATT / "before" / "oracle_base.json",
        "before/rule_table_base.json": ATT / "before" / "rule_table_base.json",
        "before/probe_results_base.json": ATT / "before" / "probe_results_base.json",
        "after/probe_results_narrow.json": ATT / "after" / "probe_results_narrow.json",
        "after/authsplit_probe_narrow.json": ATT / "after" / "authsplit_probe_narrow.json",
        "before/authsplit_probe_base.json": ATT / "before" / "authsplit_probe_base.json",
        "mutations/oracle_mut_greedy.json": ATT / "mutations" / "oracle_mut_greedy.json",
        "mutations/rule_table_mut_greedy.json": ATT / "mutations" / "rule_table_mut_greedy.json",
        "mutations/oracle_mut_authnl.json": ATT / "mutations" / "oracle_mut_authnl.json",
        "mutations/rule_table_mut_auth1.json": ATT / "mutations" / "rule_table_mut_auth1.json",
        "mutations/probe_results_mut_greedy.json": ATT / "mutations" / "probe_results_mut_greedy.json",
        "mutations/oracle_mut_authsplit.json": ATT / "mutations" / "oracle_mut_authsplit.json",
        "mutations/rule_table_mut_authsplit.json": ATT / "mutations" / "rule_table_mut_authsplit.json",
        "mutations/authsplit_probe_mut_authsplit.json":
            ATT / "mutations" / "authsplit_probe_mut_authsplit.json",
        "mutations/rule_table_mut_auth1_r2.json": ATT / "mutations" / "rule_table_mut_auth1_r2.json",
        "mutations/oracle_mut_auth1_r2.json": ATT / "mutations" / "oracle_mut_auth1_r2.json",
        "mutations/authsplit_probe_mut_auth1_r2.json":
            ATT / "mutations" / "authsplit_probe_mut_auth1_r2.json",
        "mutations/authsplit_probe_mut_authnl.json":
            ATT / "mutations" / "authsplit_probe_mut_authnl.json",
        "mutations/authsplit_probe_mut_greedy.json":
            ATT / "mutations" / "authsplit_probe_mut_greedy.json",
        "mutations/mutation_matrix.json": ATT / "mutations" / "mutation_matrix.json",
        "mutations/probe_results_mut_auth1_r2.json":
            ATT / "mutations" / "probe_results_mut_auth1_r2.json",
        "mutations/probe_results_mut_authnl.json":
            ATT / "mutations" / "probe_results_mut_authnl.json",
        "mutations/probe_results_mut_authsplit.json":
            ATT / "mutations" / "probe_results_mut_authsplit.json",
        "changes_r2_authsplit.diff": ATT / "changes_r2_authsplit.diff",
        "recovery/recovery_verification_r2.json":
            ATT / "recovery" / "recovery_verification_r2.json",
        "after/cli-r2/E5a/narrow/result.json":
            ATT / "after" / "cli-r2" / "E5a" / "narrow" / "result.json",
        "after/cli-r2/E5b/narrow/result.json":
            ATT / "after" / "cli-r2" / "E5b" / "narrow" / "result.json",
        "after/git_apply_verification.json": ATT / "after" / "git_apply_verification.json",
        "r5/counts.json": ATT / "r5" / "counts.json",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result: dict[str, dict] = {}
    for group, items in FILES.items():
        result[group] = {}
        for label, path in items.items():
            if path.is_file():
                b = path.read_bytes()
                result[group][label] = {
                    "sha256": hashlib.sha256(b).hexdigest(),
                    "bytes": len(b),
                }
            else:
                result[group][label] = {"missing": True}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "attempt": str(ATT),
        "hash_form": "sha256 of raw bytes on disk (CRLF form where applicable)",
        "groups": result,
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"wrote {out}")
    for group, items in result.items():
        missing = [k for k, v in items.items() if v.get("missing")]
        if missing:
            print("MISSING:", group, missing)
        print(f"{group}: {len(items)} entries, {len(missing)} missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
